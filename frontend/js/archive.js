import { getArchives, getArchivedResponse, loadArchives, deleteAllArchives } from "./api.js";
import { decodeHTML, customAlert, customConfirm } from "./utils.js";
import { showTab } from "./main.js";
import { showThumbnailPreview, hideThumbnailPreview, moveThumbnailPreview } from './utils.js';


export async function handle_load_archive(id, portfolios) {
  showTab("archive");
  document.querySelectorAll(".archive-item").forEach(el => el.classList.remove("active"));

  const archive = await getArchivedResponse(id);
  const viewer = document.getElementById("archive-viewer");
  if (!archive) {
    viewer.innerHTML = "<p>Failed to load archive.</p>";
    return;
  }

  const portfolio = portfolios.find(p => p.id === archive.portfolio_id);

  viewer.innerHTML = `
    <p class="timestamp">${new Date(archive.timestamp).toLocaleString()}</p>
    <p class="portfolio-name"><strong>Portfolio:</strong> ${portfolio?.name || 'Unknown'}</p>
    <h3>Advice</h3>
  `;

  const raw = decodeHTML(archive.openai_response);
  const parser = new DOMParser();
  const doc = parser.parseFromString(raw, "text/html");

  // Apply embedded style
  const style = doc.querySelector("style");
  if (style) {
    const existing = document.getElementById("archive-style");
    if (existing) existing.remove();

    const styleEl = document.createElement("style");
    styleEl.id = "archive-style";
    styleEl.textContent = style.textContent;
    document.head.appendChild(styleEl);
  }

  // Inject content
  const body = doc.querySelector("body");
  if (body) {
    const container = document.createElement("div");
    viewer.appendChild(container);

    Array.from(body.children).forEach((el, idx) => {
      const clone = el.cloneNode(true);
      clone.style.opacity = 0;
      clone.style.transition = "opacity 0.3s ease";

      setTimeout(() => {
        container.appendChild(clone);
        requestAnimationFrame(() => {
          clone.style.opacity = 1;
        });
      }, idx * 150);
    });
    setupArchiveThumbnailPreviews(container);
  }
}

function setupArchiveThumbnailPreviews(container) {
  let currentLink = null;
  container.addEventListener('mouseover', function(e) {
    if (e.target.matches('a')) {
      currentLink = e.target;
      showThumbnailPreview(e.target, e.target.href, e);
    }
  });
  container.addEventListener('mousemove', function(e) {
    if (currentLink && e.target === currentLink) {
      moveThumbnailPreview(e);
    }
  });
  container.addEventListener('mouseout', function(e) {
    if (e.target.matches('a')) {
      hideThumbnailPreview();
      currentLink = null;
    }
  });
}

export async function loadArchiveDropdown() {
  try {
    const archives = await getArchives();
    const select = document.getElementById("archive-list");
    select.innerHTML = "";
    archives.forEach(a => {
      const opt = document.createElement("option");
      opt.value = a.id;
      opt.textContent = a.original_question;

      select.appendChild(opt);
    });
  } catch (err) {
    console.warn("Failed to load archive list: " + err.message);
  }
}


document.getElementById("refresh-archives-btn").addEventListener("click", () => {
  loadArchives();
});

document.getElementById("delete-all-archives-btn").addEventListener("click", async () => {
  const confirmDelete = await customConfirm("Are you sure you want to delete ALL archives? This action cannot be undone and will permanently remove all your previous chat history.", "Delete All", "Cancel");
  if (!confirmDelete) return;

  try {
    const response = await deleteAllArchives();
    if (response.deleted) {
      // Clear the archive list
      const archiveSelect = document.getElementById("archive-list");
      archiveSelect.innerHTML = "";
      
      // Reset the viewer
      const viewer = document.getElementById("archive-viewer");
      viewer.innerHTML = "<p>Select an archive to view its details.</p>";
      
      // Show success message
      await customAlert("All archives have been deleted successfully.");
    } else {
      await customAlert("Failed to delete archives. Please try again.");
    }
  } catch (error) {
    console.error("Error deleting all archives:", error);
    await customAlert("An error occurred while deleting archives. Please try again.");
  }
});

window.loadArchiveDropdown = loadArchiveDropdown;


