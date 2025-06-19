// load navigation buttons


document.addEventListener("DOMContentLoaded", () => {
  const advisorBtn = document.querySelector("button[data-tab='advisor']");
  if (advisorBtn) advisorBtn.addEventListener("click", () => showTab('advisor'));
  const portfolioBtn = document.querySelector("button[data-tab='portfolio']");
  if (portfolioBtn) portfolioBtn.addEventListener("click", () => showTab('portfolio'));
  const archiveBtn = document.querySelector("button[data-tab='archive']");
  if (archiveBtn) archiveBtn.addEventListener("click", () => showTab('archive'));
});

// shows various tabs
export function showTab(tabId) {
  document.querySelectorAll(".tab").forEach(el => el.classList.add("hidden"));
  document.getElementById(tabId).classList.remove("hidden");

  // highlight active button
  document.querySelectorAll(".tab-button").forEach(btn =>
    btn.classList.remove("active-tab")
  );
  const activeBtn = document.querySelector(`.tab-button[data-tab="${tabId}"]`);
  if (activeBtn) activeBtn.classList.add("active-tab");
}

showTab('advisor');