/**
 * materials/sidebar.js – Left column: material list.
 * 
 * RESPONSIBILITY:
 * Acts as a thin adapter between the materials app data model and the generic
 * `sidebarRenderer` component. Transforms material-specific data (concrete vs.
 * steel, modification status) into the generic format expected by the renderer.
 *
 * SORTING:
 * Materials are displayed sorted by type (concrete first, then steel) and
 * alphabetically within each type.
 */

import { showPromptModal, showToast } from '../../utils.js';
import { renderSidebar as renderUnifiedSidebar } from '../../components/sidebarRenderer.js';
import { getProjectState, saveNow } from '../../persistence.js';

/**
 * Renders the material list sidebar by delegating to the generic sidebar renderer.
 *
 * @param {HTMLElement} panel - The left panel DOM element
 * @param {Object}      app   - Reference to the MaterialsApp instance.
 *   Must expose: materialsList, selectedId, showAddMaterialModal(),
 *   renderAll(), notifyChange()
 */
export function renderSidebar(panel, app) {
  // Sort: concrete before steel, then alphabetically by name
  const sortedItems = [...app.materialsList].sort((a, b) => {
    const typeOrder = { concrete: 1, steel: 2 };
    const oa = typeOrder[a.type] || 99;
    const ob = typeOrder[b.type] || 99;
    if (oa !== ob) return oa - ob;
    return a.name.localeCompare(b.name);
  });

  renderUnifiedSidebar(panel, {
    title: 'Materialien',
    items: sortedItems,
    activeId: app.selectedId,
    emptyMessage: 'Keine Materialien definiert. Klicken Sie auf "Neu", um eines hinzuzufügen.',

    /**
     * Returns a human-readable type label for the sidebar meta text.
     * @param {Object} mat - Material data object
     * @returns {string} 'Beton' or 'Betonstahl'
     */
    getMetaText: (mat) => mat.type === 'concrete' ? 'Beton' : 'Betonstahl',

    /** Opens the "Add Material" modal */
    onCreate: () => app.showAddMaterialModal(),

    /**
     * Handles material selection from the sidebar.
     * @param {string} id - The selected material's unique ID
     */
    onSelect: (id) => {
      app.selectedId = id;
      app.renderAll();
    },

    /**
     * Handles material deletion, including default material reassignment.
     * If the deleted material was the default for its type, the first
     * remaining material of that type becomes the new default.
     *
     * @param {Object} mat - The material data object to delete
     */
    onDelete: (mat) => {
      app.materialsList = app.materialsList.filter(m => m.id !== mat.id);
      
      // Reassign default if the deleted material was the default for its type
      const remainingOfType = app.materialsList.filter(m => m.type === mat.type);
      let newDefault = null;
      if (remainingOfType.length > 0) {
        if (!remainingOfType.some(m => m.is_default)) {
          remainingOfType[0].is_default = true;
        }
        newDefault = remainingOfType.find(m => m.is_default) || remainingOfType[0];
      }

      // Reassign any plate references to the new default material
      const projState = getProjectState();
      if (projState && projState.plates && newDefault) {
        projState.plates.forEach(plate => {
          if (mat.type === 'concrete' && plate.concrete_id === mat.id) {
            plate.concrete_id = newDefault.id;
          }
          if (mat.type === 'steel' && plate.layers) {
            plate.layers.forEach(layer => {
              if (layer.steel_id === mat.id) {
                layer.steel_id = newDefault.id;
              }
            });
          }
        });
      }

      // Update selection: pick next available or null
      if (app.selectedId === mat.id) {
        app.selectedId = app.materialsList.length > 0 ? app.materialsList[0].id : null;
      }
      app.renderAll();
      app.notifyChange();
      saveNow();
    }
  });
}
