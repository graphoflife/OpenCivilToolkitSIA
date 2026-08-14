/**
 * materials/modal.js – Modal dialog for adding new materials.
 * 
 * RESPONSIBILITY:
 * Provides a UI modal to select from predefined standard materials (from the
 * materialEngine) and add them to the current project. When a material is
 * selected, this module copies the default values from the engine
 * (`createDefaultProperties`) into the persistent project state.
 *
 * FLOW:
 *   1. User clicks "New" → showAddMaterialModal() is called
 *   2. Modal renders with type toggle (Concrete / Steel) and grade dropdown
 *   3. User picks a grade and optionally edits the name
 *   4. On "Create": a new material object is pushed into the app's list
 *      with a unique name and the correct default properties
 */

import { showToast, generateUUID } from '../../utils.js';
import { fetchDefaultProperties } from '../../api.js';

const BETON_VORLAGEN = {
  "C12/15": {}, "C16/20": {}, "C20/25": {}, "C25/30": {},
  "C30/37": {}, "C35/45": {}, "C40/50": {}, "C45/55": {}, "C50/60": {}
};
const STAHL_VORLAGEN = {
  "B500A": {}, "B500B": {}, "B500C": {}, "B700B": {}, "Stahl II": {}
};

/** @type {string} CSS ID of the modal backdrop element */
const MODAL_ID = 'modal-add-material';

/**
 * Shows the modal dialog for adding a new material to the project.
 *
 * @param {Object} app - Reference to the MaterialsApp instance.
 *   Must expose: materialsList, selectedId, renderAll(), notifyChange()
 */
export function showAddMaterialModal(app) {
  // Re-use existing backdrop element or create a new one
  let backdrop = document.getElementById(MODAL_ID);
  if (!backdrop) {
    backdrop = document.createElement('div');
    backdrop.id = MODAL_ID;
    backdrop.className = 'modal-backdrop';
    document.body.appendChild(backdrop);
  }

  backdrop.innerHTML = `
    <div class="modal-container">
      <div class="modal-header">
        <h3>Neues Material hinzufügen</h3>
        <button class="btn-item-action" id="btn-modal-close" style="color:var(--color-text-muted); font-size:1.2rem;">&times;</button>
      </div>
      <div class="modal-body">
        <div class="form-field">
          <label>Materialtyp wählen</label>
          <div style="display:flex; gap:12px;">
            <button class="btn btn-secondary active" id="modal-select-concrete" style="flex:1; border: 2px solid transparent;">Beton</button>
            <button class="btn btn-secondary" id="modal-select-steel" style="flex:1; border: 2px solid transparent;">Betonstahl</button>
          </div>
        </div>
        <div class="form-field">
          <label for="modal-grade-select">Vorlage (Klasse/Sorte)</label>
          <select class="input-control" id="modal-grade-select"></select>
        </div>
        <div class="form-field">
          <label for="modal-name-input">Name</label>
          <input type="text" class="input-control" id="modal-name-input" placeholder="Name eingeben">
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" id="btn-modal-cancel">Abbrechen</button>
        <button class="btn btn-primary" id="btn-modal-create">Erstellen</button>
      </div>
    </div>
  `;

  backdrop.classList.add('active');

  /** @type {'concrete'|'steel'} Currently selected material type */
  let selectedType = 'concrete';

  /**
   * Populates the grade dropdown and auto-fills the name field based
   * on the currently selected material type.
   */
  const updateGradeSelect = () => {
    const select = backdrop.querySelector('#modal-grade-select');
    const nameInput = backdrop.querySelector('#modal-name-input');
    if (!select || !nameInput) return;

    select.innerHTML = '';

    const vorlagen = selectedType === 'concrete' ? BETON_VORLAGEN : STAHL_VORLAGEN;

    // Build <option> entries for each available grade
    Object.keys(vorlagen).forEach(grade => {
      const opt = document.createElement('option');
      opt.value = grade;
      opt.textContent = selectedType === 'concrete'
        ? `Beton ${grade} (SIA 262)`
        : `Betonstahl ${grade}`;
      select.appendChild(opt);
    });

    // Pre-select a sensible default grade
    const defaultGrade = selectedType === 'concrete' ? 'C25/30' : 'B500B';
    if (vorlagen[defaultGrade]) {
      select.value = defaultGrade;
    }

    // Auto-fill the name input with just the grade
    nameInput.value = select.value;
  };

  // Initial population
  updateGradeSelect();

  // ── Type toggle buttons ─────────────────────────────────────────────
  const concreteBtn = backdrop.querySelector('#modal-select-concrete');
  const steelBtn = backdrop.querySelector('#modal-select-steel');

  concreteBtn.addEventListener('click', () => {
    selectedType = 'concrete';
    concreteBtn.classList.add('active');
    steelBtn.classList.remove('active');
    updateGradeSelect();
  });

  steelBtn.addEventListener('click', () => {
    selectedType = 'steel';
    steelBtn.classList.add('active');
    concreteBtn.classList.remove('active');
    updateGradeSelect();
  });

  // ── Grade dropdown updates the name field automatically ─────────────
  backdrop.querySelector('#modal-grade-select').addEventListener('change', (e) => {
    backdrop.querySelector('#modal-name-input').value = e.target.value;
  });

  // ── Close/cancel handlers ───────────────────────────────────────────
  const closeModal = () => {
    backdrop.classList.remove('active');
  };
  backdrop.querySelector('#btn-modal-close').addEventListener('click', closeModal);
  backdrop.querySelector('#btn-modal-cancel').addEventListener('click', closeModal);

  // ── Create button handler ───────────────────────────────────────────
  backdrop.querySelector('#btn-modal-create').addEventListener('click', async () => {
    const name = (backdrop.querySelector('#modal-name-input').value || '').trim();
    const grade = backdrop.querySelector('#modal-grade-select').value;

    if (!name) {
      alert('Bitte geben Sie einen Namen für das Material ein.');
      return;
    }

    // Ensure the name is unique (append counter suffix if needed)
    let finalName = name;
    let counter = 1;
    const rawName = name.replace(/_\d+$/, '');
    while (app.materialsList.some(m => m.name.toLowerCase() === finalName.toLowerCase())) {
      finalName = `${rawName}_${counter++}`;
    }

    const hasOtherOfType = app.materialsList.some(m => m.type === selectedType);
    const isSia = (finalName === grade);

    const props = await fetchDefaultProperties(selectedType, grade);

    const newMat = {
      id: generateUUID(),
      name: finalName,
      index: finalName,
      type: selectedType,
      grade: grade,
      properties: props,
      is_default: !hasOtherOfType,
      is_sia: isSia,
      description: isSia ? 'Material definiert nach SIA Norm' : ''
    };

    app.materialsList.push(newMat);
    app.selectedId = newMat.id;
    app.renderAll();
    app.notifyChange();
    closeModal();
    showToast(`Material "${finalName}" erfolgreich hinzugefügt!`);
  });
}
