/**
 * components/sidebarRenderer.js – Reusable sidebar list component.
 *
 * RESPONSIBILITY:
 * Provides a generic, configurable sidebar panel used by all apps that need
 * a left column with a selectable list of items (materials, plates, etc.).
 *
 * FEATURES:
 *   - Header with title and "New" button
 *   - Empty-state message when no items exist
 *   - List of items with selection highlighting, optional rename/delete actions
 *   - Delete confirmation via custom modal (not native confirm())
 *
 * USAGE:
 *   renderSidebar(panelElement, {
 *     title: 'Materialien',
 *     items: [...],
 *     activeId: 'selected-id',
 *     emptyMessage: 'No items yet.',
 *     getMetaText: (item) => item.type,
 *     onCreate: () => { ... },
 *     onSelect: (id) => { ... },
 *     onDelete: (item) => { ... },
 *     onRename: (item) => { ... },  // optional
 *   });
 */

import { getIcon } from '../icons.js';
import { showConfirmModal, showToast } from '../utils.js';

/**
 * Renders a unified sidebar (left column) with a header, "New" button,
 * and a selectable list of items.
 *
 * @param {HTMLElement} panel  - The left panel DOM element to render into
 * @param {Object}      config - Sidebar configuration (see below)
 *
 * @param {string}   config.title        - Header title text
 * @param {Array}    config.items        - Array of list items (each must have `.id` and `.name`)
 * @param {string}   config.activeId     - ID of the currently selected item
 * @param {string}   config.emptyMessage - Message shown when `items` is empty
 * @param {Function} config.getMetaText  - (item) => string — secondary label (e.g. type name)
 * @param {Function} config.onCreate     - Callback when "New" button is clicked
 * @param {Function} config.onSelect     - Callback(id) when an item is clicked
 * @param {Function} config.onDelete     - Callback(item) when an item is deleted
 * @param {Function} [config.onRename]   - Optional callback(item) for renaming
 */
export function renderSidebar(panel, config) {
  const {
    title,
    items,
    activeId,
    emptyMessage,
    getMetaText,
    onCreate,
    onSelect,
    onDelete,
    onRename
  } = config;

  panel.innerHTML = '';

  // ── Header with title and "New" button ──────────────────────────────
  const header = document.createElement('div');
  header.className = 'panel-header';
  header.innerHTML = `
    <h3>${title}</h3>
    <button class="btn btn-primary" id="btn-add-item" title="Neu hinzufügen">
      ${getIcon('plus', 16)} Neu
    </button>
  `;
  panel.appendChild(header);

  // ── Scrollable content area ─────────────────────────────────────────
  const panelContent = document.createElement('div');
  panelContent.className = 'panel-content';

  // Empty state: show a friendly message when there are no items
  if (!items || items.length === 0) {
    const emptyMsg = document.createElement('div');
    emptyMsg.className = 'placeholder-sidebar-content';
    emptyMsg.style.cssText = 'padding:30px 15px; text-align:center; color:var(--color-text-muted);';
    emptyMsg.innerHTML = `<p>${emptyMessage || 'Keine Einträge vorhanden.'}</p>`;
    panelContent.appendChild(emptyMsg);
  } else {
    // ── Item list ───────────────────────────────────────────────────
    const list = document.createElement('ul');
    list.className = 'instances-list';

    items.forEach(itemObj => {
      const item = document.createElement('li');
      item.className = `instance-item ${itemObj.id === activeId ? 'active' : ''}`;
      item.dataset.id = itemObj.id;

      // Secondary metadata text (e.g. "Beton" or "Betonstahl")
      const metaText = getMetaText ? getMetaText(itemObj) : '';
      
      // Build action buttons HTML conditionally
      let actionsHtml = '';
      if (onRename) {
        actionsHtml += `<button class="btn-item-action rename" title="Umbenennen">${getIcon('edit', 14)}</button>`;
      }
      if (onDelete) {
        actionsHtml += `<button class="btn-item-action delete" title="Löschen">${getIcon('trash', 14)}</button>`;
      }

      item.innerHTML = `
        <div class="instance-item-details">
          <span class="instance-name">${itemObj.name}</span>
          ${metaText ? `<span class="instance-meta">${metaText}</span>` : ''}
        </div>
        <div class="instance-actions">
          ${actionsHtml}
        </div>
      `;

      // Selection: clicking the item row (but not action buttons) selects it
      item.addEventListener('click', (e) => {
        if (e.target.closest('.btn-item-action')) return; // ignore action button clicks
        if (onSelect) onSelect(itemObj.id);
      });

      // Rename action (optional)
      if (onRename) {
        const renameBtn = item.querySelector('.rename');
        if (renameBtn) {
          renameBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            onRename(itemObj);
          });
        }
      }

      // Delete action with confirmation modal
      if (onDelete) {
        const deleteBtn = item.querySelector('.delete');
        if (deleteBtn) {
          deleteBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            showConfirmModal(
              'Eintrag löschen',
              `Möchten Sie "${itemObj.name}" wirklich löschen?`,
              () => {
                onDelete(itemObj);
                showToast('Eintrag gelöscht.');
              }
            );
          });
        }
      }

      list.appendChild(item);
    });

    panelContent.appendChild(list);
  }

  panel.appendChild(panelContent);

  // ── Bind "New" button ───────────────────────────────────────────────
  const btnNew = header.querySelector('#btn-add-item');
  if (btnNew && onCreate) {
    btnNew.addEventListener('click', onCreate);
  }

  // ── Bind "Delete" key shortcut for active item ─────────────────────
  if (sidebarDeleteKeyHandler) {
    document.removeEventListener('keydown', sidebarDeleteKeyHandler);
    sidebarDeleteKeyHandler = null;
  }

  if (onDelete && activeId && items && items.length > 0) {
    const activeItem = items.find(i => i.id === activeId);
    if (activeItem) {
      sidebarDeleteKeyHandler = (e) => {
        if (e.key === 'Delete' || e.key === 'Del') {
          const activeEl = document.activeElement;
          const isInput = activeEl && (
            activeEl.tagName === 'INPUT' ||
            activeEl.tagName === 'TEXTAREA' ||
            activeEl.tagName === 'SELECT' ||
            activeEl.isContentEditable
          );
          if (isInput) return;
          if (document.querySelector('.modal-backdrop.active')) return;

          e.preventDefault();
          showConfirmModal(
            'Eintrag löschen',
            `Möchten Sie "${activeItem.name}" wirklich löschen?`,
            () => {
              onDelete(activeItem);
              showToast('Eintrag gelöscht.');
            }
          );
        }
      };
      document.addEventListener('keydown', sidebarDeleteKeyHandler);
    }
  }
}

/** Store global keydown listener for Del key so it can be cleaned up between re-renders */
let sidebarDeleteKeyHandler = null;
