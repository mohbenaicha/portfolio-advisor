export function showTab(tabId) {
  document.querySelectorAll(".tab").forEach(el => el.classList.add("hidden"));
  document.getElementById(tabId).classList.remove("hidden");
}
