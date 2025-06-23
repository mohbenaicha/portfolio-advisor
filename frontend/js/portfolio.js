import {
  getPortfolios,
  createPortfolioAPI,
  deletePortfolioAPI
} from './api.js';
import { showToast } from './utils.js';

let selectedPortfolioId = null;
window.getPortfolios = getPortfolios;
window.selectedPortfolioId = selectedPortfolioId;

export async function loadPortfolioDropdown() {
  const portfolios = await getPortfolios();
  const dropdownIds = ["portfolio-dropdown", "portfolio-select"];

  dropdownIds.forEach((id) => {
    const dropdown = document.getElementById(id);
    if (dropdown) {
      dropdown.innerHTML = "";
      portfolios.forEach(p => {
        const opt = document.createElement("option");
        opt.value = p.id;
        opt.textContent = p.name;
        dropdown.appendChild(opt);
      });

      // Ensure the dropdown has options before accessing them
      if (dropdown.options.length > 0) {
        dropdown.selectedIndex = 0; // Select the first option
        if (id === "portfolio-select") {
          const questionBox = document.getElementById("question");
          if (questionBox) {
            const selectedName = dropdown.options[dropdown.selectedIndex].text;
            questionBox.placeholder = `Ask something about ${selectedName}...`;
          }
        }
      }
    }
  });
}

export async function loadPortfolio() {
  const id = parseInt(document.getElementById("portfolio-dropdown").value);
  const portfolios = await getPortfolios();
  const selected = portfolios.find(p => p.id === id);
  if (!selected) {
    console.warn("No matching portfolio found.");
    return;
  }

  selectedPortfolioId = id;
  document.getElementById("portfolio-name").value = selected.name;
  
  // Clear any existing error messages
  const nameErr = document.getElementById("portfolio-name-error");
  if (nameErr) {
    nameErr.textContent = "";
  }
  
  const tbody = document.querySelector("#asset-table tbody");
  tbody.innerHTML = "";

  selected.assets.forEach(a => {
    const row = createAssetRow(a);
    tbody.appendChild(row);
  });

  calculateTotals(selected.assets);
}

export async function initialUpdateQuestionPlaceholder() {
  const dropdown = document.getElementById("portfolio-dropdown");
  if (dropdown) {
    dropdown.addEventListener("change", loadPortfolio);
    await loadPortfolioDropdown();
    if (dropdown.options.length > 0) {
      dropdown.selectedIndex = 0;
      await loadPortfolio();
    }
  }
}

export async function createPortfolio() {
  const assets = [];

  try {
    document.getElementById("portfolio-name").value = "";
    document.querySelector("#asset-table tbody").innerHTML = "";
    selectedPortfolioId = null;

    // Clear any existing error messages
    const nameErr = document.getElementById("portfolio-name-error");
    if (nameErr) {
      nameErr.textContent = "";
    }

    // Pass empty string for name so new portfolio starts blank
    const newPortfolio = await createPortfolioAPI("", assets);
    selectedPortfolioId = newPortfolio.id;

    await loadPortfolioDropdown();

    const dropdown = document.getElementById("portfolio-dropdown");
    if (dropdown && selectedPortfolioId) {
      dropdown.value = selectedPortfolioId.toString(); // force string match
      // Don't call loadPortfolio() for new portfolios - keep name input empty
    }

  } catch (err) {
    console.error('Failed to save portfolio: ' + err.message);
  }
}

export async function deletePortfolio() {
  if (!selectedPortfolioId) return;

  const confirmDelete = window.confirm("Are you sure you want to delete this portfolio? You cannot undo this action. Archived advice associated with this portfolio will be deleted.");
  if (!confirmDelete) return; // Cancel deletion if user clicks "Cancel"


  try {
    await deletePortfolioAPI(selectedPortfolioId);

    // Set selectedPortfolioId so the existing portfolio isn't overwritten
    selectedPortfolioId = null;

    // Reset dropdown
    await loadPortfolioDropdown();
    document.getElementById("portfolio-name").value = "";
    document.querySelector("#asset-table tbody").innerHTML = "";

    // Clear any existing error messages
    const nameErr = document.getElementById("portfolio-name-error");
    if (nameErr) {
      nameErr.textContent = "";
    }

    const dropdown = document.getElementById("portfolio-dropdown");
    if (dropdown.options.length > 0) {
      dropdown.selectedIndex = 0;
      await loadPortfolio();
    }

  } catch (err) {
    console.error('Failed to delete portfolio: ' + err.message);
  }
}

export function addAssetRow() {
  const row = createAssetRow();
  document.querySelector("#asset-table tbody").appendChild(row);
}

function createAssetRow(data = {}) {
  const tr = document.createElement("tr");
  const tdDel = document.createElement("td");
  const btn = document.createElement("button");
  btn.textContent = "✖";
  btn.onclick = () => tr.remove();
  tdDel.appendChild(btn);
  tr.appendChild(tdDel);

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



  return tr;
}

function calculateTotals(assets) {
  const total = assets.reduce((acc, a) => acc + (a.market_price * a.units_held), 0);
  const tableRows = document.querySelectorAll("#asset-table tbody tr");
  
  assets.forEach((a, i) => {
    a.total_value = a.market_price * a.units_held * (a.asset_type === "option" ? 100 : 1);
    a.percentage_of_total = ((a.total_value / total) * 100).toFixed(2);
    
    // Update DOM in same loop
    tableRows[i].querySelector(".auto-total").textContent = a.total_value.toFixed(2);
    tableRows[i].querySelector(".auto-pct").textContent = a.percentage_of_total;
  });
}

export async function saveAssets() {
  const name = document.getElementById("portfolio-name").value.trim();
  const nameErr = document.getElementById("portfolio-name-error");

  // Clear previous error
  nameErr.textContent = "";

  if (!name || name.replace(/[^a-zA-Z0-9]/g, "").trim() === "") {
    nameErr.textContent = "Invalid portfolio name...";
    return;
  }

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

  const errorOutput = document.getElementById("portfolio-err-pout");
  errorOutput.style.color = "red";

  // If there are assets, validate them
  if (assets.length > 0) {
    const tickerSet = new Set();
    const nameSet = new Set();

    // Validate assets
    for (const a of assets) {
      if (!a.ticker || !a.name) {
        errorOutput.textContent = "Error: Ticker and Name cannot be empty.";
        return;
      }
      if (tickerSet.has(a.ticker)) {
        errorOutput.textContent = `Error: Duplicate ticker: ${a.ticker}`;
        return;
      }
      if (nameSet.has(a.name)) {
        errorOutput.textContent = `Error: Duplicate name: ${a.name}`;
        return;
      }
      if (!a.asset_type || !a.sector || !a.region) {
        errorOutput.textContent = "Error: Missing required fields.";
        return;
      }
      if (!a.market_price || !a.units_held || a.market_price <= 0 || a.units_held <= 0) {
        errorOutput.textContent = "Error: Invalid price/units.";
        return;
      }
      
      tickerSet.add(a.ticker);
      nameSet.add(a.name);
    }

    // Calculate totals for assets
    calculateTotals(assets);

    const tableRows = document.querySelectorAll("#asset-table tbody tr");
    tableRows.forEach((row, i) => {
      row.querySelector(".auto-total").textContent = assets[i].total_value.toFixed(2);
      row.querySelector(".auto-pct").textContent = assets[i].percentage_of_total;
    });
  }

  // Clear any previous errors if we reach this point
  errorOutput.textContent = "";

  try {
    await createPortfolioAPI(name, assets, selectedPortfolioId);
    await loadPortfolioDropdown();
    
    // Show success notification
    showToast("💾 Portfolio saved successfully!", 2500);
  } catch (err) {
    console.error('Failed to save portfolio: ' + err.message);
    showToast("❌ Failed to save portfolio. Please try again.", 3000);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const table = document.querySelector("table");

  table.addEventListener("click", (event) => {
    const target = event.target;

    if (
      (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.tagName === "SELECT") &&
      !["price", "units"].includes(target.id) // Exclude elements with id="price" or id="units"
    ) {
      document.querySelectorAll("table td input, table td textarea, table td select").forEach((el) => {
        el.classList.remove("active");
      });
      target.classList.add("active");
    }
  });

  document.addEventListener("click", (event) => {
    if (!table.contains(event.target)) {
      document.querySelectorAll("table td input, table td textarea, table td select").forEach((el) => {
        el.classList.remove("active");
      });
    }
  });

  initPortfolioUpload();
});

export async function duplicatePortfolio() {
  if (!selectedPortfolioId) {
    showToast("Please select a portfolio to duplicate.", 3000);
    return;
  }

  try {
    // Get current portfolio data
    const portfolios = await getPortfolios();
    const currentPortfolio = portfolios.find(p => p.id === selectedPortfolioId);
    
    if (!currentPortfolio || !currentPortfolio.assets) {
      showToast("No portfolio data found to duplicate.", 3000);
      return;
    }

    // Create new portfolio with blank name and copied assets
    const newPortfolio = await createPortfolioAPI("", currentPortfolio.assets);
    
    // Update the selected portfolio ID to the new one
    selectedPortfolioId = newPortfolio.id;
    
    // Reload the dropdown to include the new portfolio
    await loadPortfolioDropdown();
    
    // Select the new portfolio in the dropdown
    const dropdown = document.getElementById("portfolio-dropdown");
    if (dropdown) {
      dropdown.value = selectedPortfolioId.toString();
    }
    
    // Clear the portfolio name field (since it's a new portfolio)
    document.getElementById("portfolio-name").value = "";
    
    // Clear any existing error messages
    const nameErr = document.getElementById("portfolio-name-error");
    if (nameErr) {
      nameErr.textContent = "";
    }
    
    // Clear any existing error output
    const errorOutput = document.getElementById("portfolio-err-pout");
    if (errorOutput) {
      errorOutput.textContent = "";
    }
    
    // Reload the portfolio to show the duplicated assets
    await loadPortfolio();
    
    showToast("Portfolio duplicated successfully! 📋", 2500);
    
  } catch (err) {
    console.error('Failed to duplicate portfolio: ' + err.message);
    showToast("Failed to duplicate portfolio. Please try again.", 3000);
  }
}

window.createPortfolio = createPortfolio;
window.saveAssets = saveAssets;
window.loadPortfolio = loadPortfolio;
window.deletePortfolio = deletePortfolio;
window.duplicatePortfolio = duplicatePortfolio;
window.addAssetRow = addAssetRow;

// logic for uploading portfoloi
function initPortfolioUpload() {
  const uploadBtn = document.getElementById('upload-portfolio-btn');
  const modal = document.getElementById('upload-modal');
  const closeBtn = document.getElementById('upload-modal-close');
  const dropArea = document.getElementById('upload-drop-area');
  const fileInput = document.getElementById('upload-file-input');
  const browseLink = document.getElementById('upload-browse-link');
  const errorsDiv = document.getElementById('upload-errors');
  const schemaSample = document.getElementById('upload-schema-sample');

  // schema req
  const assetTypeEnum = ["stock", "bond", "option", "future", "swap"];
  const sectorEnum = ["Technology", "Finance", "Utilities", "Healthcare", "Consumer Goods", "Energy", "Real Estate", "Government Bonds", "Retail", "Life Sciences", "Manufacturing"];
  const regionEnum = ["US", "Europe", "Asia", "Emerging Markets", "Global"];
  const schemaCols = [
    {name: 'ticker', type: 'string', required: true},
    {name: 'name', type: 'string', required: true},
    {name: 'asset_type', type: 'enum', required: true, values: assetTypeEnum},
    {name: 'sector', type: 'enum', required: true, values: sectorEnum},
    {name: 'region', type: 'enum', required: true, values: regionEnum},
    {name: 'market_price', type: 'float', required: true, min: 0.01},
    {name: 'units_held', type: 'int', required: true, min: 1},
    {name: 'is_hedge', type: 'int', required: true, values: [0,1]},
    {name: 'hedges_asset', type: 'string', required: false}
  ];

  // schema sample
  // TODO: add sample csv
  schemaSample.innerHTML =
    `<b>Required columns:</b><br>` +
    schemaCols.map(col => {
      let desc = `<b>${col.name}</b> (${col.type}`;
      if (col.values) desc += `: ${col.values.join(', ')}`;
      if (col.min) desc += `, min: ${col.min}`;
      desc += col.required ? ', required' : ', optional';
      return desc + ')';
    }).join('<br>') +
    `<br><br>Example:<br>` +
    `<pre>ticker,name,asset_type,sector,region,market_price,units_held,is_hedge,hedges_asset\nAAPL,Apple,stock,Technology,US,150,10,0,\nXOM,Exxon,stock,Energy,US,100,5,1,AAPL</pre>`;

  // open/close elemnt
  uploadBtn.onclick = () => { modal.classList.remove('hidden'); errorsDiv.textContent = ''; };
  closeBtn.onclick = () => { modal.classList.add('hidden'); };
  window.addEventListener('keydown', e => { if (e.key === 'Escape') modal.classList.add('hidden'); });

  // drop file area
  dropArea.addEventListener('dragover', e => { e.preventDefault(); dropArea.classList.add('dragover'); });
  dropArea.addEventListener('dragleave', e => { dropArea.classList.remove('dragover'); });
  dropArea.addEventListener('drop', e => {
    e.preventDefault(); dropArea.classList.remove('dragover');
    if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
  });
  dropArea.onclick = () => fileInput.click();
  browseLink.onclick = e => { e.stopPropagation(); fileInput.click(); };
  fileInput.onchange = e => { if (fileInput.files.length) handleFile(fileInput.files[0]); };

  function handleFile(file) {
    if (!file.name.endsWith('.csv')) {
      errorsDiv.textContent = 'Please upload a .csv file.';
      return;
    }
    const reader = new FileReader();
    reader.onload = e => {
      const text = e.target.result;
      parseAndValidateCSV(text);
    };
    reader.readAsText(file);
  }

  function parseAndValidateCSV(text) {
    errorsDiv.textContent = '';
    // todo: replace with csv parser
    const lines = text.trim().split(/\r?\n/);
    if (lines.length < 2) {
      errorsDiv.textContent = 'CSV must have a header and at least one row.';
      return;
    }
    const headers = lines[0].split(',').map(h => h.trim());
    const required = schemaCols.filter(c => c.required).map(c => c.name);
    for (const req of required) {
      if (!headers.includes(req)) {
        errorsDiv.textContent = `Missing required column: ${req}`;
        return;
      }
    }
    const assets = [];
    for (let i = 1; i < lines.length; ++i) {
      if (!lines[i].trim()) continue;
      const vals = lines[i].split(',');
      if (vals.length < headers.length) {
        errorsDiv.textContent = `Row ${i+1} has missing columns.`;
        return;
      }
      const asset = {};
      for (let j = 0; j < headers.length; ++j) {
        asset[headers[j]] = vals[j] ? vals[j].trim() : '';
      }
      // validating feilds:
      // required: 
      for (const col of schemaCols) {
        const val = asset[col.name];
        if (col.required && (val === undefined || val === '')) {
          errorsDiv.textContent = `Row ${i+1}: ${col.name} is required.`;
          return;
        }
        if (col.type === 'enum' && val && !col.values.includes(val)) {
          errorsDiv.textContent = `Row ${i+1}: ${col.name} must be one of: ${col.values.join(', ')}`;
          return;
        }
        if (col.type === 'float' && val) {
          const num = parseFloat(val);
          if (isNaN(num) || num < (col.min || 0)) {
            errorsDiv.textContent = `Row ${i+1}: ${col.name} must be a number >= ${col.min}`;
            return;
          }
          asset[col.name] = num;
        }
        if (col.type === 'int' && val) {
          const num = parseInt(val, 10);
          if (isNaN(num) || num < (col.min || 0) || !/^\d+$/.test(val)) {
            errorsDiv.textContent = `Row ${i+1}: ${col.name} must be a whole number >= ${col.min}`;
            return;
          }
          asset[col.name] = num;
        }
        if (col.name === 'is_hedge' && val !== undefined) {
          if (val !== '0' && val !== '1' && val !== 0 && val !== 1) {
            errorsDiv.textContent = `Row ${i+1}: is_hedge must be 0 or 1.`;
            return;
          }
          asset.is_hedge = val == '1';
        }
      }
      assets.push(asset);
    }
    createPortfolioFromUpload(assets);
    modal.classList.add('hidden');
  }

  async function createPortfolioFromUpload(assets) {
    await window.createPortfolio();
    // populate table
    const tbody = document.querySelector('#asset-table tbody');
    tbody.innerHTML = '';
    assets.forEach(a => {
      const row = window.createAssetRow ? window.createAssetRow(a) : createAssetRow(a);
      tbody.appendChild(row);
    });
  }
}
