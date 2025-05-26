import { safeFetch } from "./utils.js";

const BASE_URL = "http://localhost:8000"; // Update for production

let currentUserId = null;

// Authenticate user and store user ID
export async function authenticateUser(token) {
  const res = await safeFetch(`${BASE_URL}/auth`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token }),
  });
  currentUserId = res.user_id;
  return res;
}

// Get headers including x-user-id if authenticated
function getAuthHeaders() {
  return {
    "Content-Type": "application/json",
    ...(currentUserId ? { "x-user-id": currentUserId.toString() } : {}),
  };
}

// Portfolio APIs
export async function getPortfolios() {
  return safeFetch(`${BASE_URL}/portfolios`, {
    headers: getAuthHeaders(),
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
