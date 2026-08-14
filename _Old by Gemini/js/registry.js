/**
 * registry.js – Central app module registry for OpenCivilToolkit.
 *
 * RESPONSIBILITY:
 * Maintains an ordered list of all available application modules. Each module
 * must implement a minimal interface: { id, title, icon, activate(), deactivate(), loadState() }.
 * New modules are registered here as either full implementations or placeholders.
 *
 * HOW TO ADD A NEW MODULE:
 *   1. Create a module folder under `apps/<module-name>/` with an `index.js`.
 *   2. Import the module here and add it to `APP_REGISTRY`.
 *   3. Alternatively, use `createPlaceholderApp()` until the module is ready.
 */

import { MaterialsApp } from './apps/materials/index.js';
import { PlatesApp } from './apps/plates/index.js';
import { getIcon } from './icons.js';

/**
 * Creates a lightweight placeholder app for modules that are not yet implemented.
 * Placeholder apps display a "coming soon" message in all three panels.
 *
 * @param {string} id        - Unique identifier matching the icon name
 * @param {string} title     - Human-readable module title (shown in nav bar)
 * @param {string} iconName  - Icon key from icons.js
 * @returns {Object} An app module object with the standard lifecycle interface
 */
const createPlaceholderApp = (id, title, iconName) => ({
  id,
  title,
  icon: getIcon(iconName, 24),

  /** @type {Object|null} DOM panel references set during activation */
  dom: null,

  /**
   * Activates the placeholder, filling all three panels with informational content.
   * @param {Object} dom - Object with leftPanel, middlePanel, rightPanel references
   */
  activate(dom) {
    this.dom = dom;
    this.dom.leftPanel.innerHTML = `
      <div class="panel-header">
        <h3>${title}</h3>
      </div>
      <div class="placeholder-sidebar-content">
        <button class="btn btn-primary" style="margin: 15px; width: calc(100% - 30px);">Neue Instanz</button>
        <p style="padding: 0 15px; color: var(--color-text-muted); font-size: 0.9rem;">Dies ist ein Platzhalter für die App "${title}".</p>
      </div>
    `;
    this.dom.middlePanel.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">${this.icon}</div>
        <h2>${title} Modul</h2>
        <p>Dieses Modul wird in Kürze implementiert.</p>
      </div>
    `;
    this.dom.rightPanel.innerHTML = `
      <div class="empty-state">
        <h2>LaTeX Berechnungen</h2>
        <p>Hier werden die Berechnungen für ${title} in Echtzeit gerendert.</p>
      </div>
    `;
  },

  /**
   * Cleans up references when switching away from this module.
   */
  deactivate() {
    this.dom = null;
  },

  /**
   * No-op state loader – placeholder apps have no persistent state.
   */
  loadState() {},
});

/**
 * Central application registry.
 *
 * The order of entries determines the order of navigation buttons in the top bar.
 * Each entry must implement:
 *   - id: string          (unique module identifier)
 *   - title: string       (display name)
 *   - icon: string        (SVG HTML from getIcon())
 *   - activate(dom, state, onChange): void
 *   - deactivate(): void
 *   - loadState(state): void
 *
 * @type {ReadonlyArray<Object>}
 */
export const APP_REGISTRY = Object.freeze([
  MaterialsApp,
  PlatesApp,
  createPlaceholderApp('crosssection', 'Querschnittsanalyse', 'crosssection'),
  createPlaceholderApp('stripmethod', 'Streifenmethode', 'stripmethod'),
  createPlaceholderApp('truss', '2D-Fachwerk', 'truss'),
]);
