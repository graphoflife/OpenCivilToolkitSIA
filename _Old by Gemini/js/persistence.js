/**
 * persistence.js – Save / load management for the global project state.
 *
 * RESPONSIBILITY:
 * Owns and manages the global `projectState` (single source of truth).
 * Provides functions to persist the project via a REST API backend, with an
 * automatic fallback to the browser's localStorage when the server is
 * unreachable. Also handles JSON import/export and full project reset.
 *
 * ARCHITECTURE:
 *   projectState
 *     ├── settings       { code: "SIA" }
 *     ├── activeApp      "materials" | "plates" | ...
 *     ├── materials      [ ... material objects ... ]
 *     └── plates         [ ... plate objects ... ]
 */

import { debounce, showToast } from './utils.js';
import { fetchProject, saveProject } from './api.js';

/** @type {string} localStorage key for the project data fallback */
const LOCAL_STORAGE_KEY = 'open_civil_toolkit_project';

/**
 * The global project state object. All modules read from / write to this
 * object, and persistence is triggered via `triggerSave()`.
 *
 * @type {Object}
 */
let projectState = {
  settings: { code: "SIA" },
  activeApp: "materials",
  materials: [],
  plates: []
};

/**
 * Returns a reference to the current project state.
 * @returns {Object} The live project state object
 */
export function getProjectState() {
  return projectState;
}

/**
 * Replaces the entire project state. Use with caution – prefer
 * mutating the existing state object via getProjectState() instead.
 * @param {Object} newState - The new state to adopt
 */
export function setProjectState(newState) {
  projectState = newState;
}

/**
 * Debounced save function that persists the project state.
 *
 * Strategy:
 *   1. POST to `/api/project` (backend server)
 *   2. On failure, fall back to localStorage
 * Immediately persists the current project state to backend server or localStorage.
 */
export async function saveNow() {
  const statusText = document.getElementById('status-text');
  if (statusText) {
    statusText.className = 'status-indicator unsaved';
    statusText.innerHTML = '<span class="status-dot"></span> Speichert...';
  }

  try {
    await saveProject(projectState);
    if (statusText) {
      statusText.className = 'status-indicator saved';
      statusText.innerHTML = '<span class="status-dot"></span> Synchronisiert';
    }
  } catch (err) {
    console.warn('[persistence] Server save failed, falling back to localStorage.', err);
    try {
      localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(projectState));
    } catch (storageErr) {
      console.error('[persistence] localStorage save also failed:', storageErr);
    }
    if (statusText) {
      statusText.className = 'status-indicator unsaved';
      statusText.innerHTML = '<span class="status-dot"></span> Lokal gesichert';
    }
  }
}

/**
 * Debounced save function that persists the project state.
 * @type {Function}
 */
export const triggerSave = debounce(saveNow, 150);

/**
 * Loads the project state from the backend server, falling back to
 * localStorage if the server is unreachable.
 *
 * @param {Function} onLoadedCallback - Called after state has been loaded
 *   and basic consistency checks have been applied
 */
export async function loadProject(onLoadedCallback) {
  const statusText = document.getElementById('status-text');

  try {
    projectState = await fetchProject();
    if (statusText) {
      statusText.className = 'status-indicator saved';
      statusText.innerHTML = '<span class="status-dot"></span> Synchronisiert';
    }
  } catch (err) {
    // Fallback: read from localStorage
    console.warn('[persistence] Could not load from server, trying localStorage.', err);
    const local = localStorage.getItem(LOCAL_STORAGE_KEY);
    if (local) {
      try {
        projectState = JSON.parse(local);
      } catch (parseErr) {
        console.error('[persistence] Corrupted localStorage data, starting fresh.', parseErr);
      }
    }
    if (statusText) {
      statusText.className = 'status-indicator unsaved';
      statusText.innerHTML = '<span class="status-dot"></span> Lokal geladen';
    }
  }

  // Ensure required top-level fields exist for consistency
  if (!projectState.activeApp) projectState.activeApp = 'materials';
  if (!projectState.settings) projectState.settings = { code: 'SIA' };
  if (!Array.isArray(projectState.materials)) projectState.materials = [];
  if (!Array.isArray(projectState.plates)) projectState.plates = [];
  
  if (onLoadedCallback) onLoadedCallback();
}

/**
 * Sets up event listeners for the header action buttons:
 *   - Export: downloads the project as a JSON file
 *   - Import: loads a JSON file and replaces the current project
 *   - Clear: resets all data after user confirmation
 *
 * @param {Function} onProjectLoaded - Called after import or reset to
 *   re-initialize the UI with the new state
 */
export function setupHeaderActions(onProjectLoaded) {
  // ── Export project as JSON download ─────────────────────────────────
  const btnExport = document.getElementById('btn-export');
  if (btnExport) {
    btnExport.addEventListener('click', () => {
      const blob = new Blob([JSON.stringify(projectState, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `OpenCivilToolkit_Projekt.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      showToast('Projektdatei erfolgreich exportiert!');
    });
  }

  // ── Import project from JSON file ──────────────────────────────────
  const fileInput = document.getElementById('import-file-input');
  const btnImport = document.getElementById('btn-import');
  if (btnImport && fileInput) {
    btnImport.addEventListener('click', () => {
      fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = (evt) => {
        try {
          const data = JSON.parse(evt.target.result);
          if (data && typeof data === 'object') {
            projectState = data;
            showToast('Projektdatei erfolgreich geladen!');
            
            // Apply consistency defaults
            if (!projectState.activeApp) projectState.activeApp = 'materials';
            
            if (onProjectLoaded) onProjectLoaded();
            triggerSave();
          } else {
            showToast('Ungültiges Dateiformat: kein gültiges Objekt.', 'danger');
          }
        } catch (err) {
          console.error('[persistence] Error parsing imported file:', err);
          showToast('Ungültiges Dateiformat.', 'danger');
        }
      };
      reader.onerror = () => {
        showToast('Datei konnte nicht gelesen werden.', 'danger');
      };
      reader.readAsText(file);
      fileInput.value = ''; // Reset so the same file can be re-imported
    });
  }

  // ── Clear all data (with confirmation) ─────────────────────────────
  const btnClear = document.getElementById('btn-clear');
  if (btnClear) {
    btnClear.addEventListener('click', () => {
      import('./utils.js').then(({ showConfirmModal }) => {
        showConfirmModal('Projekt zurücksetzen', 'Möchten Sie wirklich alle Daten löschen? Dies setzt das Projekt zurück.', () => {
          projectState = {
            settings: { code: 'SIA' },
            activeApp: 'materials',
            materials: [],
            plates: []
          };
          
          if (onProjectLoaded) onProjectLoaded();
          triggerSave();
          showToast('Alle Daten gelöscht.');
        });
      });
    });
  }
}
