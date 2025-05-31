import {
  authenticateUser,
  getPortfolios,
  analyzePrompt,
  saveArchive,
} from "./api.js";



// handles submitting the prompt to the backend
async function submitPrompt() {

  const select = document.getElementById("portfolio-select");
  const questionInput = document.getElementById("question");
  const question = document.getElementById("question").value.trim();
  const portfolioId = parseInt(select.value);
  const responseDiv = document.getElementById("response");



  if (!portfolioId) {
    questionError.textContent = "Please select a portfolio.";
    questionError.style.color = "red"; // Display error in red
    return;
  }

  if (!question || question.replace(/[^a-zA-Z0-9]/g, "").trim() === "") {
    questionInput.value = "Please enter a valid question."; // Clear the textarea
    questionInput.style.color = "red";
    questionInput.addEventListener("input", () => {
      questionInput.style.color = ""; // Reset text color when user starts typing
    });
    return;
  }
  console.log("Submitting question:", question, "for portfolio ID:", portfolioId);


  // Show loading animation
  responseDiv.innerHTML = `
  <div class="loading-animation">
    Generating response&nbsp;&nbsp;<span class="ellipsis">
      <span> .</span>
      <span> .</span>
      <span> .</span>
    </span>
  </div>
`;


  try {
    const refreshArchivesBtn = document.getElementById("refresh-archives-btn");
    if (refreshArchivesBtn) {
      console.log("Disabling refresh archives button");
      refreshArchivesBtn.disabled = true; // Disable the button
    }

    const result = await analyzePrompt(question, portfolioId);
    
    renderResponse(result);
    
    if (!result) {
      throw new Error("No summary returned from the backend or prompt limit reached.");
    }

    console.log("Value of result.archived:", result.archived);
    if (!result.archived) {
      console.log("Archive flag is false, not saving archive.");
      return; // donn't save if archive flag is false
    }
    
    console.log("Saving archive for portfolio ID:", portfolioId, "with question:", question);
    await saveArchive({
      portfolio_id: portfolioId,
      original_question: question,
      openai_response: result.summary,
    });

    if (refreshArchivesBtn) {
      console.log("Re-enabling refresh archives button");
      refreshArchivesBtn.disabled = false; // Re-enable the button
    }
  } catch (err) {
    console.warn("Error occurred:", err.message);
    responseDiv.innerHTML = `<p style="color: red;">Failed to generate response. Please try again.</p>`;
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

