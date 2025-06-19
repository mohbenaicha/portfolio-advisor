import { BASE_URL } from './config.js';

// user to safely fetch responses from the server and handle errors
export async function safeFetch(url, options = {}) {
  const res = await fetch(url, options);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Error ${res.status}: ${text}`);
  }
  return res.json();
}


const sidebar = document.querySelector('.sidebar');
const resizeHandle = sidebar.querySelector('.sidebar-resize-handle');

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
  try {
    const response = await safeFetch(`${BASE_URL}/verify-recaptcha`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token: recaptchaToken }),
    });
    if (response.message !== "success" || response.score < 0.5) {
      alert("reCAPTCHA validation failed. Please try again.");
      return false;
    }
    return true;
  } catch (err) {
    console.error("Error validating reCAPTCHA:", err.message);
    alert("An error occurred during reCAPTCHA validation. Please try again.");
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

