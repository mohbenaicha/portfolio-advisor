import { getAuthHeaders, authenticateUser, loadPortfolioOptions, loadArchives, initApiToken } from "./api.js";
import { loadArchiveDropdown } from "./archive.js";
import { initialUpdateQuestionPlaceholder } from "./portfolio.js";

import { safeFetch } from "./utils.js";
import { TOKEN_EXPIRY_MS, BASE_URL } from "./config.js";

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
    appScreen.style.display = "flex";
    loginError.textContent = "";
    loginError.style.display = "none";
    console.log("---------------User authenticated successfully");
    await loadArchiveDropdown();
    await loadArchives();
    await initialUpdateQuestionPlaceholder();
    await loadPortfolioOptions();

  } catch (err) {
    loginError.textContent = "Invalid token or authentication failed.";
    loginError.style.display = "block";
    loginError.classList.remove("hidden");
    console.error("Login error:", err.message); // Log the error for debugging
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


async function logout() {
  try {
    const response = await safeFetch(`${BASE_URL}/logout`, {
      method: "POST",
      headers: getAuthHeaders(), // Use the same authentication headers as other API calls
    });

    if (response.message === "Logout successful") {
      console.log("User logged out successfully");
      localStorage.clear(); // Clear local storage
      // window.location.href = "/"; // Redirect to login screen

      // Reverse the visual process of login
      appScreen.classList.add("hidden");
      appScreen.style.display = "none";
      loginScreen.classList.remove("hidden");
      loginScreen.style.display = "block";

      // Clear any input fields or error messages
      tokenInput.value = "";
      loginError.textContent = "";
      loginError.style.display = "none";
    } else {
      console.error("Logout failed:", response.message);
    }
  } catch (err) {
    console.error("Error during logout:", err.message);
  }
}

loginBtn.addEventListener("click", handleLoginClick);
window.addEventListener("DOMContentLoaded", init);

window.logout = logout;
export { login, logout };
