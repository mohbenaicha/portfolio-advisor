import { BASE_URL } from './config.js';
import { fetchThumbnail } from './api.js';


const loginError = document.getElementById("login-error");
const tempLoadingScreen = document.getElementById("loading-screen");
const sidebar = document.querySelector('.sidebar');
const resizeHandle = sidebar.querySelector('.sidebar-resize-handle');

let thumbnailPreviewDiv = null;


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
  const newWidth = e.clientX - sidebar.getBoundingClientRect().left; 
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
    const maxAttempts = 30; 
    const delay = 2000; 
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        const response = await safeFetch(`${BASE_URL}/verify-recaptcha`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ token: recaptchaToken }),
        });
        return response; 
      } catch (err) {
        if (attempt === maxAttempts - 1) {
          instanceDown = true;
          throw new Error("Container did not start within the timeout period.");
        }
        await new Promise(resolve => setTimeout(resolve, delay)); 
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

  const elements = Array.from(temp.children); 
  targetContainer.innerHTML = ""; 

  let i = 0;
  function revealNext() {
    if (i < elements.length) {
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
  
  const existingToast = document.querySelector('.toast-notification');
  if (existingToast) {
    existingToast.remove();
  }

  
  const toast = document.createElement('div');
  toast.className = 'toast-notification';
  toast.textContent = message;
  
  
  document.body.appendChild(toast);
  
  setTimeout(() => {
    toast.classList.add('show');
  }, 10);
  
  
  setTimeout(() => {
    toast.classList.add('hide');
    setTimeout(() => {
      if (toast.parentNode) {
        toast.remove();
      }
    }, 300);
  }, duration);
}

export async function showThumbnailPreview(linkElement, url, mouseEvent) {
  if (!thumbnailPreviewDiv) {
    thumbnailPreviewDiv = document.createElement('div');
    thumbnailPreviewDiv.id = 'link-thumbnail-preview';
    thumbnailPreviewDiv.style.position = 'absolute';
    thumbnailPreviewDiv.style.zIndex = 9999;
    thumbnailPreviewDiv.style.background = '#222';
    thumbnailPreviewDiv.style.padding = '6px';
    thumbnailPreviewDiv.style.borderRadius = '8px';
    thumbnailPreviewDiv.style.boxShadow = '0 2px 8px rgba(0,0,0,0.2)';
    thumbnailPreviewDiv.style.display = 'none';
    thumbnailPreviewDiv.style.maxWidth = '220px';
    document.body.appendChild(thumbnailPreviewDiv);
  }
  thumbnailPreviewDiv.innerHTML = `<div style='text-align:center;font-size:13px;color:#aaa;margin-bottom:4px;'>Loading preview...</div><div style='display:flex;align-items:center;justify-content:center;height:36px;'><span class='loading-spinner' style='width:24px;height:24px;border:3px solid #888;border-top:3px solid #fff;border-radius:50%;display:inline-block;animation:spin 1s linear infinite;'></span></div>`;
  let top = 0, left = 0;
  if (mouseEvent && mouseEvent.clientX && mouseEvent.clientY) {
    top = mouseEvent.clientY + window.scrollY + 16;
    left = mouseEvent.clientX + window.scrollX + 16;
  } else {
    const rect = linkElement.getBoundingClientRect();
    top = rect.bottom + window.scrollY + 8;
    left = rect.left + window.scrollX;
  }
  thumbnailPreviewDiv.style.display = 'block';
  thumbnailPreviewDiv.style.top = `${top}px`;
  thumbnailPreviewDiv.style.left = `${left}px`;
  await new Promise(resolve => setTimeout(resolve, 0));
  const { image, source } = await fetchThumbnail(url);
  const title = linkElement.innerText;
  // Extract source from URL if backend didn't return one
  let finalSource = source;
  if (!finalSource) {
    try {
      const urlObj = new URL(url);
      finalSource = urlObj.hostname.replace('www.', '');
    } catch (e) {
      finalSource = 'Unknown';
    }
  }
  let html = '';
  if (image) {
    html += `<img src="${image}" style="max-width:210px;max-height:120px;display:block;margin:0 auto 6px auto;">`;
  }
  if (title) {
    html += `<div style='font-weight:bold;font-size:15px;margin-bottom:2px;word-break:break-word;'>${title}</div>`;
  }
  if (finalSource) {
    html += `<div style='font-size:12px;color:#aaa;'>${finalSource}</div>`;
  }
  if (!image && !title && !finalSource) {
    html = 'No preview available';
  }
  thumbnailPreviewDiv.innerHTML = html;
  thumbnailPreviewDiv.style.border = 'none';
}

export function moveThumbnailPreview(mouseEvent) {
  if (!thumbnailPreviewDiv || !mouseEvent) return;
  const previewRect = thumbnailPreviewDiv.getBoundingClientRect();
  let top = mouseEvent.clientY + window.scrollY - previewRect.height - 16;
  let left = mouseEvent.clientX + window.scrollX + 16;
  // Clamp to viewport
  if (left + previewRect.width > window.innerWidth - 8) {
    left = window.innerWidth - previewRect.width - 8;
  }
  if (top < 8) top = 8;
  thumbnailPreviewDiv.style.top = `${top}px`;
  thumbnailPreviewDiv.style.left = `${left}px`;
}

if (!document.getElementById('thumbnail-spinner-style')) {
  const style = document.createElement('style');
  style.id = 'thumbnail-spinner-style';
  style.innerHTML = `@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`;
  document.head.appendChild(style);
}

export function hideThumbnailPreview() {
  if (thumbnailPreviewDiv) {
    thumbnailPreviewDiv.style.display = 'none';
  }
}

// Utility to generate archive title in the format 'Archive Item - YYYY/MM/DD - HH:MM'
export function generateArchiveTitle() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  const hours = String(now.getHours()).padStart(2, '0');
  const minutes = String(now.getMinutes()).padStart(2, '0');
  return `Archive Item - ${year}/${month}/${day} - ${hours}:${minutes}`;
}

// Custom alert function to replace browser alerts
export function customAlert(message) {
  return new Promise((resolve) => {
    const overlay = document.getElementById('custom-alert-overlay');
    const messageEl = document.getElementById('custom-alert-message');
    const buttonsContainer = document.getElementById('custom-alert-buttons');
    
    if (!overlay || !messageEl || !buttonsContainer) {
      // Fallback to browser alert if elements not found
      alert(message);
      resolve();
      return;
    }
    
    messageEl.textContent = message;
    buttonsContainer.innerHTML = '<button id="custom-alert-ok" class="custom-alert-button">OK</button>';
    const button = document.getElementById('custom-alert-ok');
    
    overlay.style.display = 'flex';
    button.focus();
    
    // Handle button click
    const closeAlert = () => {
      overlay.style.display = 'none';
      button.removeEventListener('click', closeAlert);
      document.removeEventListener('keydown', keyHandler);
      overlay.removeEventListener('click', overlayClickHandler);
      resolve();
    };
    
    // Handle Escape key and Enter key
    const keyHandler = (e) => {
      if (e.key === 'Escape' || e.key === 'Enter') {
        closeAlert();
      }
    };
    
    // Handle overlay background click
    const overlayClickHandler = (e) => {
      if (e.target === overlay) {
        closeAlert();
      }
    };
    
    button.addEventListener('click', closeAlert);
    document.addEventListener('keydown', keyHandler);
    overlay.addEventListener('click', overlayClickHandler);
  });
}

// Custom confirm function to replace browser confirms
export function customConfirm(message, confirmText = 'Confirm', cancelText = 'Cancel') {
  return new Promise((resolve) => {
    const overlay = document.getElementById('custom-alert-overlay');
    const messageEl = document.getElementById('custom-alert-message');
    const buttonsContainer = document.getElementById('custom-alert-buttons');
    
    if (!overlay || !messageEl || !buttonsContainer) {
      // Fallback to browser confirm if elements not found
      resolve(confirm(message));
      return;
    }
    
    messageEl.textContent = message;
    buttonsContainer.innerHTML = `
      <button id="custom-confirm-cancel" class="custom-alert-button confirm-secondary">${cancelText}</button>
      <button id="custom-confirm-ok" class="custom-alert-button confirm-primary">${confirmText}</button>
    `;
    
    const confirmBtn = document.getElementById('custom-confirm-ok');
    const cancelBtn = document.getElementById('custom-confirm-cancel');
    
    overlay.style.display = 'flex';
    cancelBtn.focus(); // Focus cancel by default for safety
    
    // Handle button clicks
    const closeConfirm = (result) => {
      overlay.style.display = 'none';
      confirmBtn.removeEventListener('click', confirmHandler);
      cancelBtn.removeEventListener('click', cancelHandler);
      document.removeEventListener('keydown', keyHandler);
      overlay.removeEventListener('click', overlayClickHandler);
      resolve(result);
    };
    
    const confirmHandler = () => closeConfirm(true);
    const cancelHandler = () => closeConfirm(false);
    
    // Handle Escape key (cancel) and Enter key (confirm)
    const keyHandler = (e) => {
      if (e.key === 'Escape') {
        closeConfirm(false);
      } else if (e.key === 'Enter') {
        closeConfirm(true);
      }
    };
    
    // Handle overlay background click (cancel)
    const overlayClickHandler = (e) => {
      if (e.target === overlay) {
        closeConfirm(false);
      }
    };
    
    confirmBtn.addEventListener('click', confirmHandler);
    cancelBtn.addEventListener('click', cancelHandler);
    document.addEventListener('keydown', keyHandler);
    overlay.addEventListener('click', overlayClickHandler);
  });
}