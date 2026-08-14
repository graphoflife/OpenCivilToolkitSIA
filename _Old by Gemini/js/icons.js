/**
 * icons.js – Shared SVG icon library for OpenCivilToolkit.
 *
 * RESPONSIBILITY:
 * Centrally manages all SVG icon paths used across the application.
 * Icons are rendered inline as SVG strings to avoid external asset dependencies.
 *
 * USAGE:
 *   import { getIcon, hasIcon } from './icons.js';
 *   const svg = getIcon('materials', 24);          // returns SVG HTML string
 *   const exists = hasIcon('materials');            // returns true
 */

/**
 * Mapping of icon names to their SVG inner markup.
 * Each value is a string of SVG elements (paths, circles, etc.) that fit
 * inside a 24×24 viewBox coordinate system.
 *
 * @type {Readonly<Record<string, string>>}
 */
const ICON_PATHS = Object.freeze({
  // ── Navigation Icons ──────────────────────────────────────────────────
  materials: '<g stroke-linejoin="round" stroke-linecap="round"><ellipse cx="12" cy="4" rx="1.5" ry="0.8"/><path d="M10.5 4 v4 a1.5 0.8 0 0 0 3 0 v-4"/><ellipse cx="10" cy="7" rx="1.5" ry="0.8"/><path d="M8.5 7 v4 a1.5 0.8 0 0 0 3 0 v-4"/><ellipse cx="14" cy="7" rx="1.5" ry="0.8"/><path d="M12.5 7 v4 a1.5 0.8 0 0 0 3 0 v-4"/><polygon points="5,14 9,13 11,16 10,21 4,20 3,17"/><polygon points="16,14 22,16 19,18 13,16"/><polygon points="13,16 19,18 19,21 13,19"/><polygon points="22,16 19,18 19,21 22,19"/></g>',
  plates: '<rect x="2" y="6" width="20" height="12" rx="1"/><circle cx="4" cy="15" r="1" fill="currentColor"/><circle cx="8" cy="15" r="1" fill="currentColor"/><circle cx="12" cy="15" r="1" fill="currentColor"/><circle cx="16" cy="15" r="1" fill="currentColor"/><circle cx="20" cy="15" r="1" fill="currentColor"/>',
  crosssection: '<path d="M6 3h12v4l-4 4v2l4 4v4H6v-4l4-4v-2L6 7V3z"/>',
  stripmethod: '<line x1="3" y1="6" x2="21" y2="6" stroke-dasharray="4,4"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18" stroke-dasharray="4,4"/>',
  truss: '<path d="M3 20L12 4l9 16H3z"/><path d="M12 4v16"/><path d="M3 20l9-8 9 8"/>',

  // ── Action Icons ──────────────────────────────────────────────────────
  eye: '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>',
  eyeOff: '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/>',
  copy: '<rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>',
  trace: '<line x1="6" y1="3" x2="6" y2="15"/><circle cx="6" cy="3" r="3"/><circle cx="6" cy="21" r="3"/><circle cx="18" cy="21" r="3"/><path d="M18 17a5 5 0 0 0-5-5H6"/>',
  plus: '<line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>',
  edit: '<path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"/>',
  trash: '<polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/>',
  layers: '<path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>',
  arrowUp: '<line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/>',
  arrowDown: '<line x1="12" y1="5" x2="12" y2="19"/><polyline points="19 12 12 19 5 12"/>',
  home: '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>',
  maximize: '<path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"/>',
});

/**
 * Checks whether an icon with the given name exists in the library.
 *
 * @param {string} name - Icon name (key in ICON_PATHS)
 * @returns {boolean} true if the icon exists
 */
export function hasIcon(name) {
  return name in ICON_PATHS;
}

/**
 * Generates an inline SVG icon as an HTML string.
 *
 * @param {string} name  - Icon name (key in ICON_PATHS)
 * @param {number} [size=14] - Width and height in pixels
 * @param {string} [style=''] - Optional inline CSS styles
 * @returns {string} SVG HTML string, or empty string if the icon name is unknown
 */
export function getIcon(name, size = 14, style = '') {
  const path = ICON_PATHS[name];
  if (!path) {
    console.warn(`[icons] Unknown icon name: "${name}"`);
    return '';
  }
  const styleAttr = style ? ` style="${style}"` : '';
  return `<svg viewBox="0 0 24 24" width="${size}" height="${size}" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"${styleAttr}>${path}</svg>`;
}
