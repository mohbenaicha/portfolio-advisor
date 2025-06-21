import { getAuthHeaders, authenticateUser, loadPortfolioOptions, loadArchives, initApiToken } from "./api.js";
import { loadArchiveDropdown } from "./archive.js";
import { initialUpdateQuestionPlaceholder } from "./portfolio.js";
import { safeFetch, validateRecaptcha, handleLoginErrorDisplay, hideElement, showElement } from "./utils.js";
import { TOKEN_EXPIRY_MS, BASE_URL, reCAPTCHA_SITE_KEY } from "./config.js";

const tokenInput = document.getElementById("token-input");
const loginBtn = document.getElementById("login-btn");
const loginScreen = document.getElementById("login-screen");
const appScreen = document.getElementById("app-screen");
const loadingScreen = document.getElementById("loading-screen");

initApiToken();

function isTokenExpired() {
  const timestamp = localStorage.getItem("authTokenTimestamp");
  if (!timestamp) return true;
  return Date.now() - parseInt(timestamp) > TOKEN_EXPIRY_MS;
}

async function login(token) {
  try {
    showElement(loadingScreen, "Authenticating token...");
    await authenticateUser(token);
    showElement(loadingScreen, "Populating your data...");
    localStorage.setItem("authToken", token);
    localStorage.setItem("authTokenTimestamp", Date.now().toString());


    hideElement(loginScreen);
    showElement(appScreen);
    
    document.querySelector(".grecaptcha-badge").style.display = "none";
    appScreen.style.display = "flex";
    
    handleLoginErrorDisplay(false);
    await loadArchiveDropdown();
    await loadArchives();
    await initialUpdateQuestionPlaceholder();
    await loadPortfolioOptions();

  } catch (err) {
    handleLoginErrorDisplay(true, "Invalid token or authentication failed.");
  } finally {
    hideElement(loadingScreen);
  }
}


async function handleLoginClick() {
  const login_token = tokenInput.value.trim();
  if (!login_token) {
    handleLoginErrorDisplay(true, "Token is required");
    return;
  }

  showElement(loadingScreen, "Launching service container for you, please hold...");
  var captchaValidated = false;
  try {
    const recaptchaToken = await grecaptcha.execute(reCAPTCHA_SITE_KEY);
    captchaValidated = await validateRecaptcha(recaptchaToken);
    console.log("Recaptcha validation result:", captchaValidated);
  }
  catch (err) {
    console.error("Recaptcha validation failed:", err.message);
    captchaValidated = false;
    console.error("Recaptcha validation error:", err);
  }

  if (!captchaValidated) {
    handleLoginErrorDisplay(true, "Could not authenticate you.");
    // hideLoadingScreen();
    hideElement(loadingScreen);
    console.error("Recaptcha validation failed");
    return;
  }
  
  await login(login_token);
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
  // Show loading screen
  showElement(loadingScreen, "Logging out...");
  try {
    const response = await safeFetch(`${BASE_URL}/logout`, {
      method: "POST",
      headers: getAuthHeaders(),
    });

    if (response.message === "Logout successful") {
      localStorage.clear();
      appScreen.classList.add("hidden");
      appScreen.style.display = "none";
      handleLoginErrorDisplay(false);
      tokenInput.value = "";
    
    } else {
      console.error("Logout failed:", response.message);
    }
  } catch (err) {
    console.error("Error during logout:", err.message);
  } finally {
    loginScreen.classList.remove("hidden");
    loginScreen.style.display = "block";
    document.querySelector(".grecaptcha-badge").style.display = "block";
    hideElement(loadingScreen);
  }
}


loginBtn.addEventListener("click", handleLoginClick);
window.addEventListener("DOMContentLoaded", init);

window.logout = logout;
export { login, logout };
