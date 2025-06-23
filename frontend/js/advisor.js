import { analyzePrompt, saveArchive, getPortfolios } from "./api.js";



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
  responseDiv.innerHTML = `
  <div class="loading-animation">
    Generating response&nbsp;&nbsp;<span class="ellipsis">
      <span> .</span>
      <span> .</span>
      <span> .</span>
    </span>
  </div>
`;

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
    const result = await analyzePrompt(question, portfolioId);

    renderResponse(result);

    if (!result) {
      throw new Error("No summary returned from the backend or prompt limit reached.");
    }

    if (result.archived) {
      // Essentially a final response
      await saveArchive({
        portfolio_id: portfolioId,
        original_question: question,
        openai_response: result.summary,
      });
      // Change the button text to "New Chat"
      askButton.textContent = "New Chat";
    }

    if (refreshArchivesBtn) {
      refreshArchivesBtn.disabled = false; // Re-enable the button
    }

  } catch (err) {
    console.warn("Error occurred:", err.message);
    responseDiv.innerHTML = `<p style="color: red;">Failed to generate response. Please try again.</p>`;
  } finally {
    questionTextarea.disabled = false; // Re-enable the textarea
    askButton.disabled = false; // Re-enable the button
  }
}

// Render the response in the designated advisor panel div
// function renderResponse(data) {
//   try {
//     const div = document.getElementById("response");
//     div.innerHTML = data.summary;
//   }
//   catch (error) {
//     console.error("Error rendering response:", error);
//     const div = document.getElementById("response");
//     div.innerHTML = `<p style="color: red;">Failed to render response.</p>`;
//   }
// }

function renderResponse(data) {
  const container = document.getElementById("response");
  container.innerHTML = data.summary;

  const children = Array.from(container.children);

  // Hide all child elements initially
  children.forEach(el => {
    el.style.opacity = 0;
    el.style.transition = "opacity 0.3s ease";
  });

  // Reveal one at a time
  let i = 0;
  function revealNext() {
    if (i < children.length) {
      children[i].style.opacity = 1;
      i++;
      setTimeout(revealNext, 200); // speed per element
    }
  }

  revealNext();
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
    const responseDiv = document.getElementById("response");

    if (questionInput) {
      questionInput.value = "";
    }

    if (responseDiv) {
      responseDiv.innerHTML = "";
    }

    askButton.textContent = "Ask";
  }
});

window.submitPrompt = submitPrompt;