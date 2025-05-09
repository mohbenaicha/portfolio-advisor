import { getArchives, getArchivedResponse } from "./api.js";

async function loadArchive() {
  const id = document.getElementById("archive-list").value;
  if (!id) return alert("Please select an archived response.");

  try {
    const archive = await getArchivedResponse(id);
    const viewer = document.getElementById("archive-viewer");
    viewer.innerHTML = `
      <h2>Question</h2><p>${archive.original_question}</p>
      <h2>Response</h2><p>${archive.openai_response}</p>
      <h3>Citations</h3>
      ${archive.article_ids.map(url => `<p>• <a href="${url}" target="_blank">${url}</a></p>`).join("")}
    `;
  } catch (err) {
    alert("Failed to load archive: " + err.message);
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
      opt.textContent = `${a.timestamp} — ${a.original_question.slice(0, 40)}...`;
      select.appendChild(opt);
    });
  } catch (err) {
    alert("Failed to load archive list: " + err.message);
  }
}

document.addEventListener("DOMContentLoaded", loadArchiveDropdown);
window.loadArchive = loadArchive;
