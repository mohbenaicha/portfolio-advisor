import {
  authenticateUser,
  getPortfolios,
  analyzePrompt,
  saveArchive,
} from "./api.js";

// async function login() {
//   let token = localStorage.getItem("authToken");
//   if (!token) {
//     token = prompt("Enter your auth token:");
//     if (!token) return alert("Token required");
//     localStorage.setItem("authToken", token);
//   }
//   try {
//     await authenticateUser(token);
//     await loadPortfolioOptions();
//   } catch (err) {
//     alert("Authentication failed: " + err.message);
//     localStorage.removeItem("authToken");
//   }
// }


async function submitPrompt() {
  const select = document.getElementById("portfolio-select");
  const question = document.getElementById("question").value.trim();
  const portfolioId = parseInt(select.value);

  if (!portfolioId || !question) return;

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

function renderResponse(data) {
  const div = document.getElementById("response");
  div.innerHTML = `<h2>Summary</h2><p>${data.summary}</p><h3>Citations</h3>`;
  if (data.articles) {
    data.articles.forEach((a) => {
      div.innerHTML += `<p>• <a href="${a.url}" target="_blank">${a.title}</a> — ${a.source}</p>`;
    });
  }
}

window.submitPrompt = submitPrompt;
