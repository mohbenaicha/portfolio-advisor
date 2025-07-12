import { analyzePrompt, saveArchive, getPortfolios } from "./api.js";
import { showThumbnailPreview, hideThumbnailPreview, moveThumbnailPreview, generateArchiveTitle, customAlert, customConfirm } from './utils.js';
import { refreshProfiles } from './profile.js';



// handles submitting the prompt to the backend
async function submitPrompt() {

  const select = document.getElementById("portfolio-select");
  const questionInput = document.getElementById("question");
  // Gather all previous user chat bubbles
  const userBubbles = Array.from(document.querySelectorAll('#chat-container .chat-bubble.user'));
  const previousUserMessages = userBubbles.map(b => b.textContent.trim()).filter(Boolean);
  // Append current input
  const currentInput = questionInput.value.trim();
  // Combine all user messages, separated by newlines
  const question = [...previousUserMessages, currentInput].join('\n');
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

  if (!question || question.replace(/[^a-zA-Z0-9]/g, "").trim() === "" || question.length > 500) {
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
    
    // Do NOT clear chat history here!
    // Append only the current input as a chat bubble
    appendMessageToChat(currentInput, 'user');
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

    // Show chat controls after first response
    const chatControls = document.querySelector(".chat-controls");
    if (chatControls) {
      chatControls.classList.add("visible");
    }

    if (result.final_message === true) {
      await refreshProfiles();
    }


  } catch (err) {
    console.warn("Error occurred:", err.message);
    // Remove buffering bubble if it exists
    const bufferingBubble = document.querySelector('.chat-bubble.buffering');
    if (bufferingBubble && bufferingBubble.parentNode) {
      bufferingBubble.parentNode.removeChild(bufferingBubble);
    }
    // Append error as assistant message instead of destroying chat
    appendMessageToChat(`<p style=\"color: red;\">Failed to generate response. Please try again.</p>`, 'assistant');
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

// Clear the current chat
function clearChat() {
  const questionInput = document.getElementById("question");
  const chatContainer = document.getElementById("chat-container");
  const chatControls = document.querySelector(".chat-controls");

  if (questionInput) {
    questionInput.value = "";
  }

  if (chatContainer) {
    chatContainer.innerHTML = "";
  }

  if (chatControls) {
    chatControls.classList.remove("visible");
  }
}

// Archive the current chat
async function archiveChat() {
  const select = document.getElementById("portfolio-select");
  const portfolioId = parseInt(select.value);
  const chatContainer = document.getElementById('chat-container');
  
  if (!portfolioId) {
    await customAlert("Please select a portfolio first.");
    return;
  }
  
  if (!chatContainer.innerHTML.trim()) {
    await customAlert("No chat to archive.");
    return;
  }

  // Ask for confirmation before archiving
  const shouldArchive = await customConfirm("Are you sure you want to archive this chat? This will clear the current conversation.", "Archive", "Cancel");
  if (!shouldArchive) {
    return;
  }

  try {
    // Archive the entire chat history
    const chatHistoryHTML = chatContainer.innerHTML;
    // Use utility to generate archive title
    const archiveTitle = generateArchiveTitle();
    const archivePayload = {
      portfolio_id: portfolioId,
      original_question: "Chat conversation", // Generic since it's the full chat
      openai_response: chatHistoryHTML,
      title: archiveTitle,
    };
    await saveArchive(archivePayload);
    await customAlert("Chat archived successfully!");
    
    // Clear the chat after archiving
    clearChat();
  } catch (error) {
    console.error("Error archiving chat:", error);
    await customAlert("Failed to archive chat. Please try again.");
  }
}




const questionBox = document.getElementById("question");
if (questionBox) {
  questionBox.setAttribute("maxlength", "500");
}
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
  submitPrompt();
  const questionInput = document.getElementById("question");
  if (questionInput) questionInput.value = "";
  const counter = document.getElementById("char-counter");
  if (counter) counter.textContent = `0/500`;
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
  const portfolios = window._portfolios || await getPortfolios();
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
  }

  // Wire up chat control buttons
  const newChatBtn = document.getElementById('new-chat-btn');
  const archiveChatBtn = document.getElementById('archive-chat-btn');
  
  if (newChatBtn) {
    newChatBtn.addEventListener('click', clearChat);
  }
  
  if (archiveChatBtn) {
    archiveChatBtn.addEventListener('click', archiveChat);
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

  // Character counter for question input
  setupCharCounter();
});

window.renderPortfolioSummary = renderPortfolioSummary;

// Character counter for question input
function setupCharCounter() {
  const questionBox = document.getElementById("question");
  if (!questionBox) return;
  let counter = document.getElementById("char-counter");
  if (!counter) {
    counter = document.createElement("span");
    counter.id = "char-counter";
    counter.style.position = "absolute";
    counter.style.right = "12px";
    counter.style.top = "8px";
    counter.style.fontSize = "12px";
    counter.style.color = "#aaa";
    counter.style.zIndex = "10";
    counter.style.pointerEvents = "none";
    counter.style.background = "#141517";
    counter.style.borderRadius = "6px";
    counter.style.padding = "2px 8px";
    // Ensure wrapper is relative
    const wrapper = questionBox.closest('.textarea-wrapper');
    if (wrapper) {
      wrapper.style.position = "relative";
      wrapper.appendChild(counter);
    }
  }
  function updateCounter() {
    counter.textContent = `${questionBox.value.length}/500`;
  }
  questionBox.addEventListener("input", updateCounter);
  updateCounter();
}

// Bind Enter key to Ask/New Chat
const questionInputEl = document.getElementById("question");
if (questionInputEl) {
  questionInputEl.addEventListener("keydown", function(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      const askButton = document.querySelector(".input-footer button");
      if (askButton) askButton.click();
    }
  });
}