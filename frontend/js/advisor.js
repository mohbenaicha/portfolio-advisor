import { analyzePrompt, saveArchive } from "./api.js";



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
    const questionTextarea = document.getElementById("question");
    const askButton = document.querySelector(".input-footer button");
    if (refreshArchivesBtn) {
      console.log("Disabling archives, text input and Ask button elements");
      refreshArchivesBtn.disabled = true;
      if (questionTextarea) {
        console.log("Disabling question textarea");
        questionTextarea.disabled = true;
      }

      if (askButton) {
        console.log("Disabling advisor button");
        askButton.disabled = true;
      }
    }

    const result = await analyzePrompt(question, portfolioId);

    renderResponse(result);

    if (!result) {
      throw new Error("No summary returned from the backend or prompt limit reached.");
    }

    questionTextarea.disabled = false; // Re-enable the textarea
    askButton.disabled = false; // Re-enable the button

    console.log("Value of result.archived:", result.archived);
    if (!result.archived) {
      console.log("Archive flag is false, not saving archive.");
      return;
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
      if (questionTextarea) {
        console.log("Re-enabling question textarea");
      }
    }
    // Change the button text to "New Chat"
    askButton.textContent = "New Chat";
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
    // Perform submitPrompt functionality
    submitPrompt();
  } else if (askButton.textContent === "New Chat") {
    // Perform "New Chat" functionality
    const questionInput = document.getElementById("question");
    const responseDiv = document.getElementById("response");

    if (questionInput) {
      questionInput.value = ""; // Clear the textarea
    }

    if (responseDiv) {
      responseDiv.innerHTML = ""; // Clear the response
    }

    // Change button text back to "Ask"
    askButton.textContent = "Ask";
  }
});


window.submitPrompt = submitPrompt;