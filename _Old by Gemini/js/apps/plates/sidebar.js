/**
 * plates/sidebar.js – Linke Spalte: Plattenliste.
 * 
 * VERANTWORTLICHKEIT:
 * Dient als dünner Wrapper um den zentralen `sidebarRenderer`. Mappt die 
 * Platten-Daten in das generische Format, das der Renderer erwartet.
 */

import { renderSidebar as renderUnifiedSidebar } from '../../components/sidebarRenderer.js';

export function renderSidebar(container, plates, activeId, callbacks) {
  const { onSelect, onCreate, onDelete } = callbacks;
  
  renderUnifiedSidebar(container, {
    title: 'Platten',
    items: plates,
    activeId: activeId,
    emptyMessage: 'Keine Platten definiert. Klicken Sie auf "Neu", um eine hinzuzufügen.',
    onCreate: onCreate,
    onSelect: onSelect,
    onDelete: (plate) => {
      // confirm modal is already handled by unified sidebar!
      onDelete(plate.id);
    }
  });
}
