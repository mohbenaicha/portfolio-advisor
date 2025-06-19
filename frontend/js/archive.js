import { getArchives, getArchivedResponse, loadArchives } from "./api.js";
import { decodeHTML } from "./utils.js";
import { showTab } from "./main.js";


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
    <h2>${archive.original_question}</h2>
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
  }
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
    select.onchange = loadArchive; // <-- add this line here
  } catch (err) {
    console.warn("Failed to load archive list: " + err.message);
  }
}


document.getElementById("refresh-archives-btn").addEventListener("click", () => {
  loadArchives();
});
window.loadArchiveDropdown = loadArchiveDropdown;


