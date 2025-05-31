import { getArchives, getArchivedResponse, loadArchives } from "./api.js";


async function loadArchive() {
  console.log("loadArchive triggered");
  const id = document.getElementById("archive-list").value;
  if (!id) return alert("Please select an archived response.");

  try {
    const archive = await getArchivedResponse(id);
    console.log("archive from backend:", archive);
    const viewer = document.getElementById("archive-viewer");
    if (!archive) {
      viewer.innerHTML = "<p>Failed to load archive.</p>";
      return;
    }
    viewer.innerHTML = `
  <h2>Question</h2><p>${archive.original_question}</p>
  <h2>Response</h2>
`;

    const parser = new DOMParser();
    const doc = parser.parseFromString(archive.openai_response, "text/html");

    const style = doc.querySelector("style");
    const body = doc.querySelector("body");

    if (style) {
      // Optional: remove existing archive styles if you want to avoid stacking
      const oldStyle = document.getElementById("archive-style");
      if (oldStyle) oldStyle.remove();

      const styleEl = document.createElement("style");
      styleEl.id = "archive-style";
      styleEl.textContent = style.textContent;
      document.head.appendChild(styleEl);
    }

    if (body) {
      const container = document.createElement("div");
      container.innerHTML = body.innerHTML;
      viewer.appendChild(container);
    }
  } catch (err) {
    console.log("Failed to load archive: " + err.message);
  }
}

export async function loadArchiveDropdown() {
  try {
    const archives = await getArchives();
    const select = document.getElementById("archive-list");
    select.innerHTML = "";
    archives.forEach(a => {
      const opt = document.createElement("option");
      opt.value = a.id;
      opt.textContent = a.original_question;

      select.appendChild(opt);
    });
    select.onchange = loadArchive; // <-- add this line here
  } catch (err) {
    console.log("Failed to load archive list: " + err.message);
  }
}


document.getElementById("refresh-archives-btn").addEventListener("click", () => {
  console.log("Refresh archives button clicked");
  loadArchives();
});
window.loadArchive = loadArchive;
window.loadArchiveDropdown = loadArchiveDropdown;


