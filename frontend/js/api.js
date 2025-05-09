import { safeFetch } from "./utils.js";

const BASE_URL = "http://localhost:8000"; // Update this for production

// Portfolio APIs
export async function getPortfolios() {
  return safeFetch(`${BASE_URL}/portfolios`);
}

export async function createPortfolioAPI(name, assets, id = null) {
  const method = id ? "PUT" : "POST";
  const url = id ? `${BASE_URL}/portfolios/${id}` : `${BASE_URL}/portfolios`;
  return safeFetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, assets })
  });
}


export async function deletePortfolioAPI(id) {
  await safeFetch(`${BASE_URL}/portfolios/${id}`, { method: "DELETE" });
}

// Prompt submission
export async function analyzePrompt(question, portfolio, summary) {
  return safeFetch(`${BASE_URL}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, portfolio_data: portfolio, portfolio_summary: summary })
  });
}

// Archive APIs
export async function getArchives() {
  return safeFetch(`${BASE_URL}/archives`);
}

export async function getArchivedResponse(id) {
  return safeFetch(`${BASE_URL}/responses/${id}`);
}


export async function saveArchive(payload) {
  return safeFetch(`${BASE_URL}/archives`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
}
