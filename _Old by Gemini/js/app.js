/**
 * app.js – Application shell and top-level orchestrator.
 *
 * RESPONSIBILITY:
 * Bootstraps the OpenCivilToolkit single-page application. Manages the lifecycle
 * of app modules (activation, deactivation, state routing) and builds the
 * top-bar navigation from the central APP_REGISTRY.
 *
 * FLOW:
 *   1. DOMContentLoaded → init()
 *   2. Load persisted project state (server or localStorage fallback)
 *   3. Build navigation buttons from APP_REGISTRY
 *   4. Activate the last-active app module
 */

import { APP_REGISTRY } from './registry.js';
import { setupPanelResizing } from './panelResizer.js';
import { getProjectState, loadProject, setupHeaderActions, triggerSave, saveNow } from './persistence.js';

/**
 * Cached references to the three main layout panels.
 * These are passed to each app module on activation so they can render
 * their own content without querying the DOM again.
 * @type {{ leftPanel: HTMLElement, middlePanel: HTMLElement, rightPanel: HTMLElement }}
 */
const domElements = {
  leftPanel: document.getElementById('left-panel'),
  middlePanel: document.getElementById('middle-panel'),
  rightPanel: document.getElementById('right-panel')
};

/** @type {Object|null} The currently active app module instance */
let currentActiveAppModule = null;

/**
 * Initializes the App Shell:
 *   - Sets up panel resizing (drag handles between columns)
 *   - Registers header action callbacks (import, export, clear)
 *   - Loads persisted project and activates the last-used module
 */
function init() {
  setupPanelResizing();
  
  // Callback invoked whenever a project is loaded, imported, or reset
  const onProjectUpdate = () => {
    buildNavigation();
    switchApp(getProjectState().activeApp);
  };
  
  setupHeaderActions(onProjectUpdate);
  loadProject(onProjectUpdate);
}

/**
 * Builds the top-bar navigation buttons dynamically from the APP_REGISTRY.
 * The currently active app gets the `.active` CSS class for visual highlighting.
 */
function buildNavigation() {
  const nav = document.getElementById('app-navigation');
  if (!nav) {
    console.error('[app] Navigation container #app-navigation not found.');
    return;
  }
  nav.innerHTML = '';
  
  const state = getProjectState();

  APP_REGISTRY.forEach(app => {
    const btn = document.createElement('button');
    btn.className = `nav-btn ${app.id === state.activeApp ? 'active' : ''}`;
    btn.dataset.id = app.id;
    btn.innerHTML = `
      ${app.icon}
      <span class="nav-btn-tooltip">${app.title}</span>
    `;

    // Prevent re-activation if already on this module
    btn.addEventListener('click', () => {
      if (getProjectState().activeApp === app.id) return;
      switchApp(app.id);
    });

    nav.appendChild(btn);
  });
}

/**
 * Switches from the current app module to a different one.
 *
 * Steps:
 *   1. Deactivate the current module (cleanup)
 *   2. Look up the target module in the registry
 *   3. Update the project state with the new active app
 *   4. Toggle the `.active` class on navigation buttons
 *   5. Ensure a state slice exists for the target module
 *   6. Activate the target module with DOM panels, state, and a change callback
 *
 * @param {string} appId - The `id` of the target app module
 */
function switchApp(appId) {
  // 1. Deactivate old app module
  if (currentActiveAppModule && currentActiveAppModule.deactivate) {
    currentActiveAppModule.deactivate();
  }

  // 2. Find the target module in the registry
  const appModule = APP_REGISTRY.find(app => app.id === appId);
  if (!appModule) {
    console.error(`[app] Module '${appId}' not found in APP_REGISTRY.`);
    return;
  }

  // 3. Update project state
  const state = getProjectState();
  state.activeApp = appId;
  currentActiveAppModule = appModule;

  // 4. Toggle active button class in the navigation bar
  const buttons = document.querySelectorAll('.nav-btn');
  buttons.forEach(btn => {
    btn.classList.toggle('active', btn.dataset.id === appId);
  });

  // 5. Ensure a state slice exists for this app (default to empty array)
  if (!state[appId]) {
    state[appId] = [];
  }

  // 6. Activate the module, passing layout panels, its state slice,
  //    and a callback the module can invoke whenever it mutates data
  appModule.activate(
    domElements,
    state[appId],
    (updatedModuleState) => {
      state[appId] = updatedModuleState;
      saveNow();
    }
  );

  saveNow();
}

// ── Bootstrap ─────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', init);
