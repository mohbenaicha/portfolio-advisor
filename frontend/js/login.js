import { authenticateUser, loadPortfolioOptions, getArchives } from "./api.js";

async function login() {
  const token = tokenInput.value.trim();
  if (!token) {
    loginError.textContent = "Token is required";
    loginError.style.display = "block";
    return;
  }
  try {
    await authenticateUser(token);
    localStorage.setItem("authToken", token);
    loginScreen.style.display = "none";
    appScreen.style.display = "block";
    loginError.style.display = "none";
    await loadPortfolioOptions();
    await loadArchives(); // Add this line
  } catch (err) {
    loginError.textContent = "Authentication failed: " + err.message;
    loginError.style.display = "block";
  }
}

async function loadArchives() {
  const archives = await getArchives();
  const archiveSelect = document.getElementById("archive-list");
  archiveSelect.innerHTML = "";
  archives.forEach((a) => {
    const opt = document.createElement("option");
    opt.value = a.id;
    opt.textContent = `${a.timestamp} — ${a.original_question.slice(0, 40)}...`;
    archiveSelect.appendChild(opt);
  });
}
