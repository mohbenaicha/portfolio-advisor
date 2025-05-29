import { safeFetch } from "./utils.js";
import { showTab } from "./main.js";

const BASE_URL = "http://localhost:8000"; // Update for production

let currentToken = null;


// Call this at startup to sync from localStorage
export function initApiToken() {
  const token = localStorage.getItem("authToken");
  if (token) currentToken = token;
}

// Authenticate user and store user ID
export async function authenticateUser(token) {
  console.log("Authenticating with token:", token);
  const res = await safeFetch(`${BASE_URL}/auth`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token }),
  });
  console.log("Auth response:", res);
  currentToken = token;
  return res;
}


// Get headers including x-user-id if authenticated
function getAuthHeaders() {
  console.log("Using auth headers with token:", currentToken);
  return {
    "Content-Type": "application/json",
    ...(currentToken ? { Authorization: `Bearer ${currentToken}` } : {}),
  };
}

// Portfolio APIs
export async function getPortfolios() {
  return safeFetch(`${BASE_URL}/portfolios`, {
    headers: getAuthHeaders(),
  });
}

export async function loadPortfolioOptions() {
  try {
    const portfolios = await getPortfolios();
    console.log("Portfolios fetched:", portfolios);

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

  archives.forEach((a) => {
    const div = document.createElement("div");
    div.className = "archive-item";
    div.dataset.id = a.id;
    div.innerHTML = `
      <div class="archive-title-wrapper">
        <span class="archive-title">${a.original_question}</span>
      </div>
    `;
    div.onclick = async () => {
      showTab("archive");
      document.querySelectorAll(".archive-item").forEach(el => el.classList.remove("active"));
      div.classList.add("active");

      const archive = await getArchivedResponse(a.id);
      const viewer = document.getElementById("archive-viewer");
      if (!archive) {
        viewer.innerHTML = "<p>Failed to load archive.</p>";
        return;
      }

      const portfolios = await getPortfolios();
      const portfolio = portfolios.find(p => p.id === archive.portfolio_id);

      viewer.innerHTML = `
    <h2>${archive.original_question}</h2>
    <p class="timestamp">${new Date(archive.timestamp).toLocaleString()}</p>
    <p class="portfolio-name"><strong>Portfolio:</strong> ${portfolio?.name || 'Unknown'}</p>
    <h3>Advice</h3>
    <p>${archive.openai_response}</p>
`;

    };
    archiveSelect.appendChild(div);
  });

  document.querySelectorAll(".archive-item").forEach(item => {
    const title = item.querySelector(".archive-title");
    const wrapper = item.querySelector(".archive-title-wrapper");

    item.addEventListener("mouseenter", () => {
      const overflow = title.scrollWidth - wrapper.clientWidth;
      if (overflow > 0) {
        title.style.transition = "transform 1s linear";
        title.style.transform = `translateX(-${overflow}px)`;
      }
    });

    item.addEventListener("mouseleave", () => {
      title.style.transition = "none";
      title.style.transform = "translateX(0)";
      requestAnimationFrame(() => {
        title.style.transition = "";
      });
    });
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

// Prompt submission
export async function analyzePrompt(question, portfolio_id) {
  return safeFetch(`${BASE_URL}/analyze`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({ question, portfolio_id }),
  });
}

// Archive APIs
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

export async function saveArchive(payload) {
  return safeFetch(`${BASE_URL}/archives`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(payload),
  });
}
