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
      <h2>Response</h2><div>${archive.openai_response}</div>
    `;
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


