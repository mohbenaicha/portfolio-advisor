import {
  getPortfolios,
  createPortfolioAPI,
  deletePortfolioAPI
} from './api.js';

let selectedPortfolioId = null;

export async function loadPortfolioDropdown() {
  const portfolios = await getPortfolios();
  const dropdown = document.getElementById("portfolio-dropdown");
  dropdown.innerHTML = "";
  portfolios.forEach(p => {
    const opt = document.createElement("option");
    opt.value = p.id;
    opt.textContent = p.name;
    dropdown.appendChild(opt);
  });
  dropdown.value = selectedPortfolioId;
}

export async function loadPortfolio() {
  const id = parseInt(document.getElementById("portfolio-dropdown").value);
  const portfolios = await getPortfolios();
  const selected = portfolios.find(p => p.id === id);
  if (!selected) return;

  selectedPortfolioId = id;
  document.getElementById("portfolio-name").value = selected.name;
  const tbody = document.querySelector("#asset-table tbody");
  tbody.innerHTML = "";

  selected.assets.forEach(a => {
    const row = createAssetRow(a);
    tbody.appendChild(row);
  });
}

export async function createPortfolio() {
  const name = document.getElementById("portfolio-name").value;
  const assets = []; // empty for now
  try {
    const newPortfolio = await createPortfolioAPI(name, assets, selectedPortfolioId);
    selectedPortfolioId = newPortfolio.id;
    await loadPortfolioDropdown();
    await loadPortfolio();
  } catch (err) {
    alert('Failed to save portfolio: ' + err.message);
  }
}

export async function deletePortfolio() {
  if (!selectedPortfolioId) return;
  try {
    await deletePortfolioAPI(selectedPortfolioId);
    selectedPortfolioId = null;
    await loadPortfolioDropdown();
    document.querySelector("#asset-table tbody").innerHTML = "";
  } catch (err) {
    alert('Failed to delete portfolio: ' + err.message);
  }
}

export function addAssetRow() {
  const row = createAssetRow();
  document.querySelector("#asset-table tbody").appendChild(row);
}

function createAssetRow(data = {}) {
  const tr = document.createElement("tr");
  const fields = ["ticker", "name", "asset_type", "sector", "region", "market_price", "units_held", "is_hedge", "hedges_asset"];
  const types = {
    asset_type: ["stock", "bond", "option", "future", "swap"],
    sector: ["Technology", "Finance", "Utilities", "Healthcare", "Consumer Goods", "Energy", "Real Estate", "Government Bonds", "Retail", "Life Sciences", "Manufacturing"],
    region: ["US", "Europe", "Asia", "Emerging Markets", "Global"]
  };

  fields.forEach(f => {
    const td = document.createElement("td");
    let el;
    if (types[f]) {
      el = document.createElement("select");
      types[f].forEach(opt => {
        const option = document.createElement("option");
        option.value = option.textContent = opt;
        el.appendChild(option);
      });
      el.value = data[f] || "";
    } else if (f === "is_hedge") {
      el = document.createElement("input");
      el.type = "checkbox";
      el.checked = data[f] || false;
    } else {
      el = document.createElement("input");
      el.value = data[f] || "";
      el.type = (f === "market_price" || f === "units_held") ? "number" : "text";
    }
    el.name = f;
    td.appendChild(el);
    tr.appendChild(td);
  });

  const tdTotal = document.createElement("td");
  tdTotal.className = "auto-total";
  tdTotal.textContent = data.total_value?.toFixed(2) || "";
  tr.appendChild(tdTotal);

  const tdPct = document.createElement("td");
  tdPct.className = "auto-pct";
  tdPct.textContent = data.percentage_of_total || "";
  tr.appendChild(tdPct);

  const tdDel = document.createElement("td");
  const btn = document.createElement("button");
  btn.textContent = "✖";
  btn.onclick = () => tr.remove();
  tdDel.appendChild(btn);
  tr.appendChild(tdDel);

  return tr;
}

export async function saveAssets() {
  const name = document.getElementById("portfolio-name").value;
  const rows = document.querySelectorAll("#asset-table tbody tr");
  const assets = [];

  rows.forEach(row => {
    const obj = {};
    row.querySelectorAll("input, select").forEach(input => {
      const { name, value, type, checked } = input;
      obj[name] = (type === "checkbox") ? checked : (type === "number" ? parseFloat(value) : value);
    });
    assets.push(obj);
  });

  const tickerSet = new Set();
  for (const a of assets) {
    if (tickerSet.has(a.ticker)) {
      alert(`Duplicate ticker found: ${a.ticker}`);
      return;
    }
    tickerSet.add(a.ticker);
  }

  let total = assets.reduce((acc, a) => acc + (a.market_price * a.units_held), 0);
  assets.forEach(a => {
    a.total_value = a.market_price * a.units_held;
    a.percentage_of_total = ((a.total_value / total) * 100).toFixed(2);
  });

  // Update DOM display
  const tableRows = document.querySelectorAll("#asset-table tbody tr");
  tableRows.forEach((row, i) => {
    row.querySelector(".auto-total").textContent = assets[i].total_value.toFixed(2);
    row.querySelector(".auto-pct").textContent = assets[i].percentage_of_total;
  });

  try {
    await createPortfolioAPI(name, assets, selectedPortfolioId);
    await loadPortfolioDropdown();
  } catch (err) {
    alert('Failed to save portfolio: ' + err.message);
  }
}

// Expose key functions to window if needed
window.createPortfolio = createPortfolio;
window.saveAssets = saveAssets;
window.loadPortfolio = loadPortfolio;
window.deletePortfolio = deletePortfolio;
window.addAssetRow = addAssetRow;
