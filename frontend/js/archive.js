import { getArchives, getArchivedResponse } from "./api.js";

console.log('archive.js loaded');

async function loadArchive() {
  console.log("loadArchive triggered");
  const id = document.getElementById("archive-list").value;
  if (!id) return alert("Please select an archived response.");

  try {
    const archive = await getArchivedResponse(id);
    console.log("archive from backend:", archive); // <--- Add this line
    const viewer = document.getElementById("archive-viewer");
    if (!archive) {
      viewer.innerHTML = "<p>Failed to load archive.</p>";
      return;
    }
    viewer.innerHTML = `
      <h2>Question</h2><p>${archive.original_question}</p>
      <h2>Response</h2><p>${archive.openai_response}</p>
    `;
  } catch (err) {
    console.log("Failed to load archive: " + err.message);
  }
}

async function loadArchiveDropdown() {
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

document.addEventListener("DOMContentLoaded", loadArchiveDropdown);

document.addEventListener("DOMContentLoaded", loadArchiveDropdown);
window.loadArchive = loadArchive;
window.loadArchiveDropdown = loadArchiveDropdown;


