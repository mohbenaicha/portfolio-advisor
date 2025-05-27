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

  calculateTotals(selected.assets);
}

document.addEventListener("DOMContentLoaded", () => {
  const dropdown = document.getElementById("portfolio-dropdown");

  if (dropdown) {
    dropdown.addEventListener("change", () => {
      loadPortfolio();
    });
  }
});

export async function createPortfolio() {
  const name = document.getElementById("portfolio-name").value;
  const assets = []; // empty for now
  try {
    const newPortfolio = await createPortfolioAPI(name, assets, selectedPortfolioId);
    selectedPortfolioId = newPortfolio.id;
    await loadPortfolioDropdown();
    await loadPortfolio();
  } catch (err) {
    console.log('Failed to save portfolio: ' + err.message);
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
    console.log('Failed to delete portfolio: ' + err.message);
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

function calculateTotals(assets) {
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
      console.log(`Duplicate ticker found: ${a.ticker}`);
      return;
    }
    tickerSet.add(a.ticker);
  }

  calculateTotals(assets);

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
    console.log('Failed to save portfolio: ' + err.message);
  }
}

// Handle input pop-up on click
document.addEventListener("DOMContentLoaded", () => {
  const table = document.querySelector("table");

  table.addEventListener("click", (event) => {
    const target = event.target;

    // Check if the clicked element is an input, textarea, or select
    if (
      (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.tagName === "SELECT") &&
      !["price", "units"].includes(target.id) // Exclude elements with id="price" or id="units"
    ) {
      // Remove the 'active' class from all inputs
      document.querySelectorAll("table td input, table td textarea, table td select").forEach((el) => {
        el.classList.remove("active");
      });

      // Add the 'active' class to the clicked element
      target.classList.add("active");
    }
  });

  // Remove the 'active' class when clicking outside the table
  document.addEventListener("click", (event) => {
    if (!table.contains(event.target)) {
      document.querySelectorAll("table td input, table td textarea, table td select").forEach((el) => {
        el.classList.remove("active");
      });
    }
  });
});

// Expose key functions to window if needed
window.createPortfolio = createPortfolio;
window.saveAssets = saveAssets;
window.loadPortfolio = loadPortfolio;
window.deletePortfolio = deletePortfolio;
window.addAssetRow = addAssetRow;
