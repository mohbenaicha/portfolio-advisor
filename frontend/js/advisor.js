async function loadPortfolioOptions() {
  const portfolios = await getPortfolios();
  const select = document.getElementById("portfolio-select");
  select.innerHTML = "";
  portfolios.forEach(p => {
    const opt = document.createElement("option");
    opt.value = p.id;
    opt.textContent = p.name;
    select.appendChild(opt);
  });
}

async function submitPrompt() {
  const select = document.getElementById("portfolio-select");
  const question = document.getElementById("question").value;
  const portfolioId = parseInt(select.value);

  const portfolios = await getPortfolios();
  const selected = portfolios.find(p => p.id === portfolioId);
  if (!selected) return;

  const summary = {
    asset_types: [...new Set(selected.assets.map(a => a.asset_type))],
    sectors: [...new Set(selected.assets.map(a => a.sector))],
    regions: [...new Set(selected.assets.map(a => a.region))]
  };

  const result = await analyzePrompt(question, selected.assets, summary);
  renderResponse(result);
}

function renderResponse(data) {
  const div = document.getElementById("response");
  div.innerHTML = `<h2>Summary</h2><p>${data.summary}</p><h3>Citations</h3>`;
  data.articles.forEach(a => {
    div.innerHTML += `<p>• <a href="${a.url}" target="_blank">${a.title}</a> — ${a.source}</p>`;
  });
}

// Load portfolios when advisor tab is shown
document.addEventListener("DOMContentLoaded", loadPortfolioOptions);
