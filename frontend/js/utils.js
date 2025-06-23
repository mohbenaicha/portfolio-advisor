import { BASE_URL } from './config.js';


const loginError = document.getElementById("login-error");
const tempLoadingScreen = document.getElementById("loading-screen");
const sidebar = document.querySelector('.sidebar');
const resizeHandle = sidebar.querySelector('.sidebar-resize-handle');

// user to safely fetch responses from the server and handle errors
export async function safeFetch(url, options = {}) {
  const res = await fetch(url, options);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Error ${res.status}: ${text}`);
  }
  return res.json();
}

resizeHandle.addEventListener('mousedown', (e) => {
  e.preventDefault();
  document.addEventListener('mousemove', resizeSidebar);
  document.addEventListener('mouseup', stopResizing);
});

function resizeSidebar(e) {
  const newWidth = e.clientX - sidebar.getBoundingClientRect().left; // Calculate width from the left edge
  if (newWidth >= 100 && newWidth <= 600) {
    sidebar.style.width = `${newWidth}px`;
  }
}

function stopResizing() {
  document.removeEventListener('mousemove', resizeSidebar);
  document.removeEventListener('mouseup', stopResizing);
}

export function decodeHTML(str) {
  const textarea = document.createElement("textarea");
  textarea.innerHTML = str;
  return textarea.value;
}

export async function validateRecaptcha(recaptchaToken) {
  let instanceDown = false;

  try {
    const maxAttempts = 30; // 1 minute total (30 attempts * 2 seconds)
    const delay = 2000; // 2 seconds
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        const response = await safeFetch(`${BASE_URL}/verify-recaptcha`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ token: recaptchaToken }),
        });
        return response; // Exit loop and return response if successful
      } catch (err) {
        if (attempt === maxAttempts - 1) {
          instanceDown = true;
          throw new Error("Container did not start within the timeout period.");
        }
        await new Promise(resolve => setTimeout(resolve, delay)); // Wait before retrying
      }
    }
    showElement(tempLoadingScreen, "Validating reCAPTCHA...");
    if (response.message !== "success" || response.score < 0.5) {
      alert("reCAPTCHA validation failed. Please try again.");
      return false;
    }
  } catch (err) {
    console.error("Error validating reCAPTCHA:", err.message);
    if (instanceDown) {
      alert("Briefly service is currently unavailable. Please try again later.");
    } else {
      alert("An error occurred during reCAPTCHA validation. Please try again.");
    }
    return false;
  }
}


export function revealArchiveSequentially(body, targetContainer, delay = 200) {
  const temp = document.createElement("div");
  temp.innerHTML = body.innerHTML;

  const elements = Array.from(temp.children); // this gets the actual block-level elements
  targetContainer.innerHTML = ""; // optional: clear existing

  let i = 0;
  function revealNext() {
    if (i < elements.length) {
      console.log("Appending:", elements[i]);
      const clone = elements[i].cloneNode(true);
      targetContainer.appendChild(clone);
      i++;
      setTimeout(revealNext, delay);
    }
  }

  revealNext();
}

export function handleLoginErrorDisplay(show_error = true, message = "") {
  if (show_error) {
    loginError.textContent = message;
    loginError.style.display = "block";
    loginError.classList.remove("hidden");
  }
  else {
    loginError.textContent = "";
    loginError.style.display = "none";
    loginError.classList.add("hidden");
  }
}

const populateLoadingText = (message) => {
  document.getElementById("loading-text").textContent = message;
};


export const hideElement = (element) => {
  if (element) {
    element.classList.add("hidden");
    if (element.id !== "loading-screen") {
      element.style.display = "none";
    }
  }
}

export const showElement = (element, additionContent) => {
  if (element) {
    element.classList.remove("hidden");
    if (element.id === "loading-screen") {
      populateLoadingText(additionContent);
    } else {
      element.style.display = "block";
    }
  }
};

export function showToast(message, duration = 3000) {
  // Remove any existing toast
  const existingToast = document.querySelector('.toast-notification');
  if (existingToast) {
    existingToast.remove();
  }

  // Create new toast
  const toast = document.createElement('div');
  toast.className = 'toast-notification';
  toast.textContent = message;
  
  // Add to DOM
  document.body.appendChild(toast);
  
  // Trigger animation
  setTimeout(() => {
    toast.classList.add('show');
  }, 10);
  
  // Hide after duration
  setTimeout(() => {
    toast.classList.add('hide');
    setTimeout(() => {
      if (toast.parentNode) {
        toast.remove();
      }
    }, 300);
  }, duration);
}