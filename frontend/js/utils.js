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