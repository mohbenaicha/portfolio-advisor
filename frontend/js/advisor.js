import {
  authenticateUser,
  getPortfolios,
  analyzePrompt,
  saveArchive,
} from "./api.js";



// handles submitting the prompt to the backend
async function submitPrompt() {
  const select = document.getElementById("portfolio-select");
  const question = document.getElementById("question").value.trim();
  const portfolioId = parseInt(select.value);

  if (!portfolioId || !question) return;

  console.log("Submitting question:", question, "for portfolio ID:", portfolioId);

  const result = await analyzePrompt(question, portfolioId);
  renderResponse(result);

  try {
    await saveArchive({
      portfolio_id: portfolioId,
      original_question: question,
      openai_response: result.summary,
    });
  } catch (err) {
    console.warn("Archiving failed:", err.message);
  }
}

// Render the response in the designated advisor panel div
function renderResponse(data) {
  const div = document.getElementById("response");
  div.innerHTML = data.summary;
}

const questionBox = document.getElementById("question");
const advisorDropdown = document.getElementById("portfolio-select");
// update placeholder text in question box based on selected advisor

if (advisorDropdown && questionBox) {
  advisorDropdown.addEventListener("change", function () {
    const selectedName = this.options[this.selectedIndex].text;
    questionBox.placeholder = `Ask something about ${selectedName}...`;
  });
}


window.submitPrompt = submitPrompt;

