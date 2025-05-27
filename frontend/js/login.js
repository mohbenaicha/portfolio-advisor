import { authenticateUser, loadPortfolioOptions, loadArchives, initApiToken } from "./api.js";

const TOKEN_EXPIRY_MS = 24 * 60 * 60 * 1000; // 24 hours

const loginScreen = document.getElementById("login-screen");
const appScreen = document.getElementById("app-screen");
const tokenInput = document.getElementById("token-input");
const loginBtn = document.getElementById("login-btn");
const loginError = document.getElementById("login-error");


initApiToken();

function isTokenExpired() {
  const timestamp = localStorage.getItem("authTokenTimestamp");
  if (!timestamp) return true;
  return Date.now() - parseInt(timestamp) > TOKEN_EXPIRY_MS;
}

async function login(token) {
  if (!token) {
    loginError.textContent = "Token is required";
    loginError.style.display = "block";
    return;
  }
  try {
    await authenticateUser(token);
    localStorage.setItem("authToken", token);
    localStorage.setItem("authTokenTimestamp", Date.now().toString());

    loginScreen.classList.add("hidden");
    appScreen.classList.remove("hidden");
    loginError.textContent = "";
    loginError.style.display = "none";

    await loadPortfolioOptions();
    await loadArchives();
  } catch (err) {
    loginError.textContent = "Authentication failed: " + err.message;
    loginError.style.display = "block";
  }
}


async function handleLoginClick() {
  const token = tokenInput.value.trim();
  await login(token);
}

async function init() {
  const savedToken = localStorage.getItem("authToken");
  if (savedToken && !isTokenExpired()) {
    tokenInput.value = savedToken;
    await login(savedToken);
  } else {
    localStorage.removeItem("authToken");
    localStorage.removeItem("authTokenTimestamp");
    loginScreen.style.display = "block";
    appScreen.style.display = "none";
  }
}

loginBtn.addEventListener("click", handleLoginClick);
window.addEventListener("DOMContentLoaded", init);


export { login };
