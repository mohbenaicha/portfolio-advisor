import { analyzePrompt, saveArchive, getPortfolios } from "./api.js";
import { showThumbnailPreview, hideThumbnailPreview, moveThumbnailPreview } from './utils.js';



// handles submitting the prompt to the backend
async function submitPrompt() {

  const select = document.getElementById("portfolio-select");
  const questionInput = document.getElementById("question");
  const question = document.getElementById("question").value.trim();
  const portfolioId = parseInt(select.value);
  const responseDiv = document.getElementById("response");


  if (!portfolioId) {
    questionInput.value = "Please select a portfolio.";
    questionInput.style.color = "red";
    questionInput.addEventListener("input", () => {
      questionInput.style.color = "";
    });
    return;
  }

  if (!question || question.replace(/[^a-zA-Z0-9]/g, "").trim() === "" || question.length > 1000) {
    questionInput.value = "Please enter a valid question.";
    questionInput.style.color = "red";
    questionInput.addEventListener("input", () => {
      questionInput.style.color = "";
    });
    return;
  }

  // Check if the selected portfolio has at least one asset
  try {
    const portfolios = await getPortfolios();
    const selectedPortfolio = portfolios.find(p => p.id === portfolioId);
    
    if (!selectedPortfolio || !selectedPortfolio.assets || selectedPortfolio.assets.length === 0) {
      questionInput.value = "Portfolio should have at least 1 asset before it can be analyzed.";
      questionInput.style.color = "red";
      questionInput.addEventListener("input", () => {
        questionInput.style.color = "";
      });
      return;
    }
  } catch (error) {
    console.error("Error checking portfolio assets:", error);
    questionInput.value = "Error checking portfolio. Please try again.";
    questionInput.style.color = "red";
    questionInput.addEventListener("input", () => {
      questionInput.style.color = "";
    });
    return;
  }

  // Show loading animation
  // responseDiv.innerHTML = `
  // <div class="loading-animation">
  //   Generating response&nbsp;&nbsp;<span class="ellipsis">
  //     <span> .</span>
  //     <span> .</span>
  //     <span> .</span>
  //   </span>
  // </div>
  // <div id="chat-container"></div>
  // `;

  const refreshArchivesBtn = document.getElementById("refresh-archives-btn");
  const questionTextarea = document.getElementById("question");
  const askButton = document.querySelector(".input-footer button");
  try {
    if (refreshArchivesBtn) refreshArchivesBtn.disabled = true;
    if (questionTextarea) {
      questionTextarea.disabled = true;
    }

    if (askButton) {
      askButton.disabled = true;
    }
    // Do NOT clear chat history here!
    // Append user message as a chat bubble
    appendMessageToChat(question, 'user');
    // Add buffering bubble for assistant
    const chatContainer = document.getElementById('chat-container');
    const bufferingBubble = document.createElement('div');
    bufferingBubble.className = 'chat-bubble assistant buffering';
    bufferingBubble.innerHTML = '<span class="ellipsis"><span> .</span><span> .</span><span> .</span></span>';
    chatContainer.appendChild(bufferingBubble);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    const result = await analyzePrompt(question, portfolioId);
    // Remove buffering bubble
    if (bufferingBubble.parentNode) bufferingBubble.parentNode.removeChild(bufferingBubble);
    renderResponse(result);

    if (!result) {
      throw new Error("No summary returned from the backend or prompt limit reached.");
    }

    if (result.archived) {
      // Archive the entire chat history
      const chatHistoryHTML = document.getElementById('chat-container').innerHTML;
      await saveArchive({
        portfolio_id: portfolioId,
        original_question: question,
        openai_response: chatHistoryHTML,
      });
      // Change the button text to "New Chat"
      askButton.textContent = "New Chat";
    }

    if (refreshArchivesBtn) {
      refreshArchivesBtn.disabled = false; // Re-enable the button
    }

  } catch (err) {
    console.warn("Error occurred:", err.message);
    // Remove buffering bubble if it exists
    const bufferingBubble = document.querySelector('.chat-bubble.buffering');
    if (bufferingBubble && bufferingBubble.parentNode) {
      bufferingBubble.parentNode.removeChild(bufferingBubble);
    }
    // Append error as assistant message instead of destroying chat
    appendMessageToChat(`<p style="color: red;">Failed to generate response. Please try again.</p>`, 'assistant');
  } finally {
    questionTextarea.disabled = false; // Re-enable the textarea
    askButton.disabled = false; // Re-enable the button
  }
}

// Helper to append a chat bubble
function appendMessageToChat(message, sender) {
  const chatContainer = document.getElementById('chat-container');
  const bubble = document.createElement('div');
  bubble.className = sender === 'user' ? 'chat-bubble user' : 'chat-bubble assistant';
  bubble.innerHTML = message;
  chatContainer.appendChild(bubble);
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Render the response as a chat bubble
function renderResponse(data) {
  appendMessageToChat(data.summary, 'assistant');
}




const questionBox = document.getElementById("question");
const advisorDropdown = document.getElementById("portfolio-select");
const askButton = document.querySelector(".input-footer button");


// update placeholder text in question box based on selected advisor
if (advisorDropdown && questionBox) {
  advisorDropdown.addEventListener("change", function () {
    const selectedName = this.options[this.selectedIndex].text;
    questionBox.placeholder = `Ask something about ${selectedName}...`;
  });
}

askButton.addEventListener("click", () => {
  if (askButton.textContent === "Ask") {
    submitPrompt();
  } else if (askButton.textContent === "New Chat") {
    const questionInput = document.getElementById("question");
    const chatContainer = document.getElementById("chat-container");

    if (questionInput) {
      questionInput.value = "";
    }

    if (chatContainer) {
      chatContainer.innerHTML = "";
    }

    askButton.textContent = "Ask";
  }
});

window.submitPrompt = submitPrompt;

// === Portfolio Summary Panel Logic ===

const summaryTabs = [
  { key: 'exposure', label: 'Exposure' },
  { key: 'region', label: 'Region' },
  { key: 'sector', label: 'Sector' }
];

let currentSummaryTab = 'exposure';

async function renderPortfolioSummary() {
  const select = document.getElementById('portfolio-select');
  const summaryContent = document.getElementById('summary-content');
  if (!select || !summaryContent) return;
  const portfolioId = parseInt(select.value);
  if (!portfolioId) {
    summaryContent.innerHTML = '<div style="color: #aaa; text-align: center;">No portfolio selected.</div>';
    return;
  }
  const portfolios = await getPortfolios();
  const portfolio = portfolios.find(p => p.id === portfolioId);
  if (!portfolio || !portfolio.assets || portfolio.assets.length === 0) {
    summaryContent.innerHTML = '<div style="color: #aaa; text-align: center;">No assets in this portfolio.</div>';
    return;
  }

  // Compute summary by tab
  let groupKey;
  if (currentSummaryTab === 'exposure') groupKey = 'asset_type';
  else if (currentSummaryTab === 'region') groupKey = 'region';
  else if (currentSummaryTab === 'sector') groupKey = 'sector';

  // Group assets
  const groups = {};
  let totalValue = 0;
  portfolio.assets.forEach(a => {
    const value = (parseFloat(a.market_price) || 0) * (parseFloat(a.units_held) || 0) * (a.asset_type === 'option' ? 100 : 1);
    totalValue += value;
    const key = a[groupKey] || 'Other';
    if (!groups[key]) groups[key] = 0;
    groups[key] += value;
  });

  // Build table
  let table = `<table class="summary-table" style="width:100%; border-collapse:collapse; table-layout:fixed;">
    <thead><tr>
      <th style='text-align:left;padding:4px;'><span>${currentSummaryTab === 'exposure' ? 'Asset Type' : currentSummaryTab.charAt(0).toUpperCase() + currentSummaryTab.slice(1) + '<br>'}</span></th>
      <th style='text-align:right;padding:4px;'><span>$ Exposure</span></th>
      <th style='text-align:right;padding:4px;'><span>% Exposure</span></th>
    </tr></thead><tbody>`;
  Object.entries(groups).sort((a, b) => b[1] - a[1]).forEach(([label, value]) => {
    const pct = totalValue ? ((value / totalValue) * 100).toFixed(2) : '0.00';
    table += `<tr>
      <td style='padding:4px;'>${label}</td>
      <td style='text-align:right;padding:4px;'>$${value.toLocaleString(undefined, {maximumFractionDigits:2})}</td>
      <td style='text-align:right;padding:4px;'>${pct}%</td>
    </tr>`;
  });
  table += '</tbody></table>';
  summaryContent.innerHTML = table;
}

function setupSummaryTabs() {
  const tabButtons = document.querySelectorAll('.summary-tab');
  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      tabButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentSummaryTab = btn.getAttribute('data-summary');
      renderPortfolioSummary();
    });
  });
}

document.addEventListener('DOMContentLoaded', () => {
  setupSummaryTabs();
  const select = document.getElementById('portfolio-select');
  if (select) {
    select.addEventListener('change', renderPortfolioSummary);
    // Initial render after portfolios load
    setTimeout(renderPortfolioSummary, 600);
  }

  // --- Draggable divider logic for advisor tab ---
  const resizeBar = document.getElementById('advisor-resize-bar');
  const textareaWrapper = document.querySelector('.textarea-wrapper');
  const summaryPanel = document.querySelector('.portfolio-summary-panel');
  const advisorBox = document.querySelector('.advisor-box');
  let isDragging = false;

  if (resizeBar && textareaWrapper && summaryPanel && advisorBox) {
    resizeBar.addEventListener('mousedown', function(e) {
      // Only allow horizontal drag if flex-direction is row
      if (window.getComputedStyle(advisorBox).flexDirection !== 'row') return;
      isDragging = true;
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    });
    document.addEventListener('mousemove', function(e) {
      if (!isDragging) return;
      // Calculate new width for textareaWrapper
      const boxRect = advisorBox.getBoundingClientRect();
      let newWidth = e.clientX - boxRect.left;
      // Set min/max
      const min = 300, max = advisorBox.offsetWidth - 370 - 24; // 370px min for summary panel, 24px for divider/margins
      if (newWidth < min) newWidth = min;
      if (newWidth > max) newWidth = max;
      textareaWrapper.style.width = newWidth + 'px';
      summaryPanel.style.flex = '1 1 0';
    });
    document.addEventListener('mouseup', function(e) {
      if (isDragging) {
        isDragging = false;
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
      }
    });
  }

  // Setup thumbnail previews for links in assistant chat bubbles
  function setupChatBubbleThumbnails() {
    const chatContainer = document.getElementById('chat-container');
    let currentLink = null;
    chatContainer.addEventListener('mouseover', async function(e) {
      if (e.target.matches('.chat-bubble.assistant a')) {
        currentLink = e.target;
        showThumbnailPreview(e.target, e.target.href, e);
      }
    });
    chatContainer.addEventListener('mousemove', function(e) {
      if (currentLink && e.target === currentLink) {
        moveThumbnailPreview(e);
      }
    });
    chatContainer.addEventListener('mouseout', function(e) {
      if (e.target.matches('.chat-bubble.assistant a')) {
        hideThumbnailPreview();
        currentLink = null;
      }
    });
  }
  setupChatBubbleThumbnails();
});