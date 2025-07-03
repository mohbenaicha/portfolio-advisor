import { INVESTMENT_OBJECTIVES, SECTOR_PREFERENCES, REGIONAL_PREFERENCES, ASSET_PREFERENCES } from './profile_options.js';
import { getPortfolios, getProfiles, createProfile, updateProfile, deleteProfileAPI } from './api.js';
import { BASE_URL } from './config.js';
import { showToast } from './utils.js';

document.addEventListener("DOMContentLoaded", () => {
  const profileBtn = document.querySelector("button[data-tab='profile']");
  if (profileBtn) {
    profileBtn.addEventListener("click", () => {
      renderProfileTab();
    });
  }
});

let profiles = [];
let unsavedProfiles = [];
let portfolios = [];
let usedPortfolioIds = new Set();

// Fetch portfolios and profiles from backend
async function fetchPortfolios() {
  portfolios = await getPortfolios();
}

async function fetchProfiles() {
  try {
    profiles = await getProfiles();
    // Always set profile_id for all loaded profiles
    profiles.forEach(p => { p.profile_id = p.id; });
    usedPortfolioIds = new Set(profiles.map(p => p.portfolio_id));
  } catch (err) {
    throw new Error('Could not load profiles: ' + err.message);
  }
}

// Render the Profile tab
export async function renderProfileTab() {
  const container = document.getElementById('profile');
  container.innerHTML = '';
  try {
    await fetchPortfolios();
    await fetchProfiles();
    // Merge backend profiles and unsaved profiles
    const allProfiles = [...profiles, ...unsavedProfiles];
    allProfiles.forEach((profile, idx) => {
      container.appendChild(createProfileDiv(profile, idx, allProfiles));
    });
    if (canAddProfile()) {
      const buttonContainer = document.createElement('div');
      buttonContainer.className = 'profile-buttons-container';
      
      const addBtn = document.createElement('button');
      addBtn.textContent = '+ Add Profile';
      addBtn.onclick = addProfile;
      addBtn.className = 'add-profile-btn';
      buttonContainer.appendChild(addBtn);
      
      const refreshBtn = document.createElement('button');
      refreshBtn.textContent = '↻ Refresh';
      refreshBtn.onclick = refreshProfiles;
      refreshBtn.className = 'add-profile-btn';
      buttonContainer.appendChild(refreshBtn);
      
      container.appendChild(buttonContainer);
    }
  } catch (err) {
    container.innerHTML = `<div class="error-font" style="color:red;">${err.message}</div>`;
  }
}

function canAddProfile() {
  // Only allow add if not all portfolios are used, excluding 'All Portfolios' (null)
  const used = new Set([...usedPortfolioIds].filter(id => id !== null));
  return used.size < portfolios.length;
}

function addProfile() {
  const newProfile = {
    profile_id: null,
    portfolio_id: -1,
    short_term_objectives: [],
    long_term_objectives: [],
    sector_preferences: [],
    regional_preferences: [],
    asset_preferences: []
  };
  unsavedProfiles.push(newProfile);
  renderProfileTab();
}

function createProfileDiv(profile, idx, allProfiles) {
  const div = document.createElement('div');
  div.className = 'profile-div';

  // Build a set of available portfolio IDs (including 'ALL' for All Portfolios)
  const available = new Set(['ALL', ...portfolios.map(p => p.id)]);
  allProfiles.forEach((p, i) => {
    if (i !== idx) {
      if (p.portfolio_id === null) {
        available.delete('ALL');
      } else if (p.portfolio_id !== -1 && p.portfolio_id !== undefined) {
        available.delete(p.portfolio_id);
      }
    }
  });

  // Portfolio dropdown
  const portfolioSelect = document.createElement('select');
  // Add 'All Portfolios' option if available or if this profile already has it
  if ((profile.portfolio_id === null) || (profile.portfolio_id !== -1 && available.has('ALL'))) {
    const allOption = document.createElement('option');
    allOption.value = '';
    allOption.textContent = 'All Portfolios';
    portfolioSelect.appendChild(allOption);
  }
  // Add portfolio options if available or if this profile already has it
  portfolios.forEach(p => {
    if (available.has(p.id) || p.id === profile.portfolio_id) {
      const opt = document.createElement('option');
      opt.value = p.id;
      opt.textContent = p.name;
      portfolioSelect.appendChild(opt);
    }
  });
  portfolioSelect.value = (profile.portfolio_id === null) ? '' : (profile.portfolio_id === -1 ? '' : profile.portfolio_id);
  portfolioSelect.onchange = e => {
    if (!e.target.value) {
      // 'All Portfolios' selected
      if (!available.has('ALL') && profile.portfolio_id !== null) {
        alert('A profile for All Portfolios already exists.');
        portfolioSelect.value = (profile.portfolio_id === null) ? '' : (profile.portfolio_id === -1 ? '' : profile.portfolio_id);
        return;
      }
      profile.portfolio_id = null;
    } else {
      const val = parseInt(e.target.value);
      if (!available.has(val) && val !== profile.portfolio_id) {
        alert('A profile for this portfolio already exists.');
        portfolioSelect.value = (profile.portfolio_id === null) ? '' : (profile.portfolio_id === -1 ? '' : profile.portfolio_id);
        return;
      }
      profile.portfolio_id = val;
    }
  };
  div.appendChild(portfolioSelect);

  // Multi-select fields
  div.appendChild(createMultiSelect('Short-Term Objectives', profile.short_term_objectives, INVESTMENT_OBJECTIVES, val => {
    profile.short_term_objectives = val;
    if (profile.id) profile.profile_id = profile.id;
  }));
  div.appendChild(createMultiSelect('Long-Term Objectives', profile.long_term_objectives, INVESTMENT_OBJECTIVES, val => {
    profile.long_term_objectives = val;
    if (profile.id) profile.profile_id = profile.id;
  }));
  div.appendChild(createMultiSelect('Sector Preferences', profile.sector_preferences, SECTOR_PREFERENCES, val => {
    profile.sector_preferences = val;
    if (profile.id) profile.profile_id = profile.id;
  }));
  div.appendChild(createMultiSelect('Regional Preferences', profile.regional_preferences, REGIONAL_PREFERENCES, val => {
    profile.regional_preferences = val;
    if (profile.id) profile.profile_id = profile.id;
  }));
  div.appendChild(createMultiSelect('Asset Preferences', profile.asset_preferences, ASSET_PREFERENCES, val => {
    profile.asset_preferences = val;
    if (profile.id) profile.profile_id = profile.id;
  }));

  // Profile action buttons
  const actions = document.createElement('div');
  actions.className = 'profile-actions';

  // Save button (use refresh-arch-btn style, floppy unicode)
  const saveBtn = document.createElement('button');
  saveBtn.title = 'Save Profile';
  saveBtn.className = 'refresh-arch-btn';
  saveBtn.innerHTML = '💾';
  saveBtn.onclick = () => saveProfile(profile, idx, allProfiles);
  actions.appendChild(saveBtn);

  // Delete button (use delete-all-arch-btn style, trash unicode)
  const delBtn = document.createElement('button');
  delBtn.title = 'Delete Profile';
  delBtn.className = 'delete-all-arch-btn';
  delBtn.innerHTML = '🗑';
  delBtn.onclick = () => confirmDeleteProfile(idx, allProfiles);
  actions.appendChild(delBtn);

  div.appendChild(actions);
  return div;
}

function createMultiSelect(label, selected, options, onChange) {
  const wrapper = document.createElement('div');
  wrapper.className = 'multi-select-wrapper';
  const lbl = document.createElement('label');
  lbl.textContent = label;
  wrapper.appendChild(lbl);

  // Bubbles
  const bubbleContainer = document.createElement('div');
  bubbleContainer.className = 'bubble-container';
  function renderBubbles() {
    bubbleContainer.innerHTML = '';
    selected.forEach((item, i) => {
      const bubble = document.createElement('span');
      bubble.className = 'bubble';
      bubble.textContent = item;
      const removeBtn = document.createElement('button');
      removeBtn.className = 'bubble-remove';
      removeBtn.textContent = '×';
      removeBtn.onclick = (e) => {
        e.preventDefault();
        selected.splice(i, 1);
        onChange([...selected]);
        renderBubbles();
      };
      bubble.appendChild(removeBtn);
      bubbleContainer.appendChild(bubble);
    });
  }
  renderBubbles();
  wrapper.appendChild(bubbleContainer);

  // Free text input with Enter key functionality
  const input = document.createElement('input');
  input.type = 'text';
  input.placeholder = 'Type a preference and press Enter to add';
  
  input.onkeydown = function(e) {
    if (e.key === 'Enter') {
      e.preventDefault();
      const value = input.value.trim();
      if (value) {
        if (selected.includes(value)) {
          input.value = '';
          return;
        }
        if (selected.length >= 5) {
          return;
        }
        selected.push(value);
        onChange([...selected]);
        renderBubbles();
        input.value = '';
      }
    }
  };
  
  // Keep autocomplete for suggestions but make it optional
  input.oninput = function() {
    if (input.value.trim()) {
      showAutocomplete(input, options, selected, val => {
        if (selected.includes(val)) {
          input.value = '';
          hideAutocomplete();
          return;
        }
        if (selected.length >= 5) {
          return;
        }
        selected.push(val);
        onChange([...selected]);
        renderBubbles();
        input.value = '';
        hideAutocomplete();
      });
    } else {
      hideAutocomplete();
    }
  };
  
  wrapper.appendChild(input);

  return wrapper;
}

let autocompleteDiv = null;
function showAutocomplete(input, options, selected, onSelect) {
  hideAutocomplete();
  autocompleteDiv = document.createElement('div');
  autocompleteDiv.className = 'autocomplete-dropdown';
  const val = input.value.toLowerCase();
  options.filter(opt => opt.toLowerCase().includes(val) && !selected.includes(opt)).forEach(opt => {
    const item = document.createElement('div');
    item.className = 'autocomplete-item';
    item.textContent = opt;
    item.onclick = () => onSelect(opt);
    autocompleteDiv.appendChild(item);
  });
  if (autocompleteDiv.children.length > 0) {
    input.parentNode.appendChild(autocompleteDiv);
  }
}
function hideAutocomplete() {
  if (autocompleteDiv && autocompleteDiv.parentNode) {
    autocompleteDiv.parentNode.removeChild(autocompleteDiv);
  }
  autocompleteDiv = null;
}
document.addEventListener('click', hideAutocomplete);

async function saveProfile(profile, idx, allProfiles) {
  if (
    !profile.short_term_objectives.length &&
    !profile.long_term_objectives.length &&
    !profile.sector_preferences.length &&
    !profile.regional_preferences.length &&
    !profile.asset_preferences.length
  ) {
    showToast('Please add at least one objective or preference.', 3000);
    return;
  }
  try {
    if (profile.profile_id) {
      const patch = { ...profile, id: profile.profile_id };
      delete patch.profile_id;
      await updateProfile(profile.profile_id, patch);
    } else {
      await createProfile(profile);
      unsavedProfiles = unsavedProfiles.filter((p, i) => i !== idx - profiles.length);
    }
    await fetchProfiles();
    renderProfileTab();
    
    // Get portfolio name for toast
    let portfolioName = 'All Portfolios';
    if (profile.portfolio_id) {
      const portfolio = portfolios.find(p => p.id === profile.portfolio_id);
      if (portfolio) {
        portfolioName = portfolio.name;
      }
    }
    
    showToast(`💾 Profile saved successfully for ${portfolioName}!`, 2500);
  } catch (err) {
    showToast('❌ Failed to save profile. Please try again.', 3000);
  }
}

function confirmDeleteProfile(idx, allProfiles) {
  if (confirm('Are you sure you want to delete this profile?')) {
    deleteProfile(idx, allProfiles);
  }
}

async function deleteProfile(idx, allProfiles) {
  const profile = allProfiles[idx];
  try {
    if (profile.id) {
      await deleteProfileAPI(profile.id);
    } else {
      unsavedProfiles = unsavedProfiles.filter((p, i) => i !== idx - profiles.length);
    }
    await fetchProfiles();
    renderProfileTab();
  } catch (err) {
    if (!err.message.includes('Unexpected end of JSON input')) {
      alert('Failed to delete profile: ' + err.message);
    }
  }
}

export async function refreshProfiles() {
  await fetchProfiles();
  renderProfileTab();
} 