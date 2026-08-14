/**
 * panelResizer.js – Draggable column resizers for the three-panel layout.
 *
 * RESPONSIBILITY:
 * Manages the left and right drag handles that allow users to resize the
 * three columns (sidebar, editor, report). Panel widths are persisted in
 * localStorage so they survive page reloads.
 *
 * CONSTRAINTS:
 *   - Left panel:  min 180px, max 500px
 *   - Right panel: min 300px, max 800px
 *   - Middle panel fills the remaining space (CSS grid `1fr`)
 */

/** @type {number} Minimum width in pixels for the left (sidebar) panel */
const LEFT_MIN_PX = 180;
/** @type {number} Maximum width in pixels for the left (sidebar) panel */
const LEFT_MAX_PX = 500;
/** @type {number} Minimum width in pixels for the right (report) panel */
const RIGHT_MIN_PX = 300;
/** @type {number} Maximum width in pixels for the right (report) panel */
const RIGHT_MAX_PX = 800;

/** @type {string} Default left panel width if nothing is stored */
const DEFAULT_LEFT_WIDTH = '260px';
/** @type {string} Default right panel width if nothing is stored */
const DEFAULT_RIGHT_WIDTH = '460px';

/**
 * Clamps a numeric value between a minimum and maximum.
 * @param {number} value - The value to clamp
 * @param {number} min   - Lower bound
 * @param {number} max   - Upper bound
 * @returns {number} The clamped value
 */
function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

/**
 * Sets up mouse-drag event handling for both the left and right resizer
 * handles. Persists the final widths to localStorage on mouse-up.
 *
 * Expects the following DOM structure:
 *   #main-layout
 *     ├── #left-panel
 *     ├── #resizer-left
 *     ├── #middle-panel
 *     ├── #resizer-right
 *     └── #right-panel
 */
export function setupPanelResizing() {
  const resizerLeft = document.getElementById('resizer-left');
  const resizerRight = document.getElementById('resizer-right');
  const layout = document.getElementById('main-layout');

  if (!resizerLeft || !resizerRight || !layout) {
    console.warn('[panelResizer] Required DOM elements not found, skipping resizer setup.');
    return;
  }

  // Restore saved panel widths from localStorage (or use defaults)
  const savedLeft = localStorage.getItem('panel-left-width') || DEFAULT_LEFT_WIDTH;
  const savedRight = localStorage.getItem('panel-right-width') || DEFAULT_RIGHT_WIDTH;
  layout.style.setProperty('--left-width', savedLeft);
  layout.style.setProperty('--right-width', savedRight);

  /**
   * Attaches a drag handler to a resizer element.
   *
   * @param {HTMLElement} resizer      - The resizer handle element
   * @param {string}      cssVar       - CSS custom property name (e.g. '--left-width')
   * @param {string}      storageKey   - localStorage key for persistence
   * @param {Function}    calcWidth    - Function(mouseEvent) → desired width in px
   */
  function attachResizer(resizer, cssVar, storageKey, calcWidth) {
    resizer.addEventListener('mousedown', (e) => {
      e.preventDefault();
      document.body.style.cursor = 'col-resize';
      resizer.classList.add('dragging');

      const onMouseMove = (moveEvent) => {
        const width = calcWidth(moveEvent);
        layout.style.setProperty(cssVar, `${width}px`);
      };

      const onMouseUp = () => {
        document.body.style.cursor = 'default';
        resizer.classList.remove('dragging');
        // Persist the final width
        localStorage.setItem(storageKey, layout.style.getPropertyValue(cssVar));
        document.removeEventListener('mousemove', onMouseMove);
        document.removeEventListener('mouseup', onMouseUp);
      };

      document.addEventListener('mousemove', onMouseMove);
      document.addEventListener('mouseup', onMouseUp);
    });
  }

  // Left resizer: width = cursor X position, clamped to [LEFT_MIN, LEFT_MAX]
  attachResizer(resizerLeft, '--left-width', 'panel-left-width', (e) =>
    clamp(e.clientX, LEFT_MIN_PX, LEFT_MAX_PX)
  );

  // Right resizer: width = viewport width - cursor X, clamped to [RIGHT_MIN, RIGHT_MAX]
  attachResizer(resizerRight, '--right-width', 'panel-right-width', (e) =>
    clamp(window.innerWidth - e.clientX, RIGHT_MIN_PX, RIGHT_MAX_PX)
  );
}
