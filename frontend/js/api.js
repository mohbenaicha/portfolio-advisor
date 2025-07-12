import { safeFetch, decodeHTML, customAlert, customConfirm } from "./utils.js";
import { BASE_URL } from "./config.js";
import { handle_load_archive } from "./archive.js";
let currentToken = null;


export function initApiToken() {
  const token = localStorage.getItem("authToken");
  if (token) currentToken = token;
}

export async function authenticateUser(token) {
  const res = await safeFetch(`${BASE_URL}/auth`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token }),
  });
  currentToken = token;
  return res;
}


export function getAuthHeaders() {
  return {
    "Content-Type": "application/json",
    ...(currentToken ? { Authorization: `Bearer ${currentToken}` } : {}),
  };
}

// Portfolio APIs
export async function getPortfolios(forceRefresh = false) {
  if (!forceRefresh && window._portfolios) {
    return window._portfolios;
  }
  const data = await safeFetch(`${BASE_URL}/portfolios`, {
    headers: getAuthHeaders(),
  });
  window._portfolios = data;
  return data;
}

export async function loadPortfolioOptions() {
  try {
    const portfolios = await getPortfolios();
    const dropdowns = [
      document.getElementById("portfolio-dropdown"),
      document.getElementById("portfolio-select")
    ];
    dropdowns.forEach(dropdown => {
      if (!dropdown) return;
      dropdown.innerHTML = "";
      portfolios.forEach((p) => {
        const opt = document.createElement("option");
        opt.value = p.id;
        opt.textContent = p.name;
        dropdown.appendChild(opt);
      });
    });


  } catch (error) {
    console.error("Error loading portfolio options:", error);
  }
}

export async function loadArchives() {
  const archives = await getArchives();
  const archiveSelect = document.getElementById("archive-list");
  archiveSelect.innerHTML = "";

  // Fetch portfolios ONCE and reuse
  const portfolios = await getPortfolios();

  archives.forEach(async (a) => {
    const div = document.createElement("div");
    div.className = "archive-item";
    div.dataset.id = a.id;
    div.innerHTML = `
      <div class="archive-title-wrapper">
        <button class="delete-archive-btn">❌</button>  
        <span class="archive-title">${a.title || a.original_question}</span>
      </div>
    `;

    // Handle archive item click
    div.onclick = async () => {
      div.classList.add("active");
      handle_load_archive(a.id, portfolios)
    }

    // Handle delete button click
    const deleteButton = div.querySelector(".delete-archive-btn");
    deleteButton.addEventListener("click", async (event) => {
      event.stopPropagation(); // Prevent triggering the archive item click event
      const shouldDelete = await customConfirm("Are you sure you want to delete this archive?", "Delete", "Cancel");
      if (shouldDelete) {
        try {
          const response = await safeFetch(`${BASE_URL}/archives/${a.id}`, {
            method: "DELETE",
            headers: getAuthHeaders(),
          });
          loadArchives(); // Refresh the sidebar
          const viewer = document.getElementById("archive-viewer");
          viewer.innerHTML = "<p>Select an archive to view its details.</p>"; // Reset viewer box content
          if (response.deleted) {
            div.remove(); // Remove the archive item from the DOM
          } else {
            await customAlert("Failed to delete archive.");
          }
        } catch (error) {
          await customAlert("An error occurred while deleting the archive.");
        }
      }
    });

    // Add animation event listeners to this specific item
    const title = div.querySelector(".archive-title");
    const wrapper = div.querySelector(".archive-title-wrapper");
    const deleteBtn = div.querySelector(".delete-archive-btn");

    title.addEventListener("mouseenter", () => {
      const deleteButtonWidth = deleteBtn.offsetWidth;
      const availableSpace = wrapper.clientWidth - deleteButtonWidth - 10; // Subtract padding/margin (e.g., 10px)
      const overflow = title.scrollWidth - availableSpace;

      if (overflow > 0) {
        const duration = Math.min(overflow / 50, 5); // Calculate duration (e.g., 50px per second, max 5 seconds)
        title.style.transition = `transform ${duration}s linear`;
        title.style.transform = `translateX(-${overflow}px)`;
      }
    });

    div.addEventListener("mouseleave", () => {
      title.style.transition = "none";
      title.style.transform = "translateX(0)";
    });

    archiveSelect.appendChild(div);
  });
}

export async function createPortfolioAPI(name, assets, id = null) {
  const method = id ? "PUT" : "POST";
  const url = id ? `${BASE_URL}/portfolios/${id}` : `${BASE_URL}/portfolios`;
  return safeFetch(url, {
    method,
    headers: getAuthHeaders(),
    body: JSON.stringify({ name, assets }),
  });
}

export async function deletePortfolioAPI(id) {
  await safeFetch(`${BASE_URL}/portfolios/${id}`, {
    method: "DELETE",
    headers: getAuthHeaders(),
  });
}

export async function analyzePrompt(question, portfolio_id) {
  return safeFetch(`${BASE_URL}/analyze`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({ question, portfolio_id }),
  });
}

export async function getArchives() {
  return safeFetch(`${BASE_URL}/archives`, {
    headers: getAuthHeaders(),
  });
}

export async function getArchivedResponse(id) {
  return safeFetch(`${BASE_URL}/responses/${id}`, {
    headers: getAuthHeaders(),
  });
}

export async function deleteAllArchives() {
  return safeFetch(`${BASE_URL}/archives`, {
    method: "DELETE",
    headers: getAuthHeaders(),
  });
}

export async function saveArchive(payload) {
  return safeFetch(`${BASE_URL}/archives`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(payload),
  });
}

export async function fetchThumbnail(url) {
  try {
    const resp = await safeFetch(`${BASE_URL}/thumbnail?url=${encodeURIComponent(url)}`);
    // Expect resp: { image, title, source }
    return resp;
  } catch (e) {
    console.error('[fetchThumbnail] Error:', e);
    return { image: null, title: null, source: null };
  }
}

// Profile APIs
export async function getProfiles() {
  return safeFetch(`${BASE_URL}/profiles/`, {
    headers: getAuthHeaders(),
  });
}

export async function createProfile(profile) {
  return safeFetch(`${BASE_URL}/profiles/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(profile),
  });
}

export async function updateProfile(profile_id, profile) {
  return safeFetch(`${BASE_URL}/profiles/${profile_id}`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(profile),
  });
}

export async function deleteProfileAPI(profile_id) {
  return safeFetch(`${BASE_URL}/profiles/${profile_id}`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });
}

export { BASE_URL };