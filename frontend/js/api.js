const BASE_URL = "http://localhost:8000"; // Update this for production

// Portfolio APIs
async function getPortfolios() {
  const res = await fetch(`${BASE_URL}/portfolios`);
  return res.json();
}

async function createPortfolioAPI(name, assets) {
  const res = await fetch(`${BASE_URL}/portfolios`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, assets })
  });
  return res.json();
}

async function deletePortfolioAPI(id) {
  await fetch(`${BASE_URL}/portfolios/${id}`, { method: "DELETE" });
}

// Prompt submission
async function analyzePrompt(question, portfolio, summary) {
  const res = await fetch(`${BASE_URL}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question,
      portfolio_data: portfolio,
      portfolio_summary: summary
    })
  });
  return res.json();
}

// Archive APIs
async function getArchives() {
  const res = await fetch(`${BASE_URL}/archives`);
  return res.json();
}

async function getArchivedResponse(id) {
  const res = await fetch(`${BASE_URL}/responses/${id}`);
  return res.json();
}
