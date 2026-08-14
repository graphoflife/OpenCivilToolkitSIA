/**
 * materials/editor.js – Middle column: parameter input form.
 * 
 * RESPONSIBILITY:
 * Reads variable definitions (fundamental variables) from the materialEngine
 * and dynamically generates form fields. When the user changes a value, the
 * change is persisted to the project state (JSON).
 * 
 * DESIGN:
 * - Contains NO hardcoded HTML forms for material properties.
 *   Everything is built dynamically via `renderFormField()` based on the
 *   engine's variable definitions.
 * - Two groups of parameters:
 *     • 'basis' (fundamental): directly editable by the user
 *     • 'berechnet' (computed): auto-calculated, but can be manually overridden
 */

import { getIcon } from '../../icons.js';

const VORLAGEN_KEYS = ["C12/15", "C16/20", "C20/25", "C25/30", "C30/37", "C35/45", "C40/50", "C45/55", "C50/60", "B500A", "B500B", "B500C", "B700B", "Stahl II"];

// =============================================================================
// Single Form Field
// =============================================================================

/**
 * Renders a single form field for a material variable.
 *
 * @param {Object} def   - Variable definition from the engine (id, prop, unit, editor, ...)
 * @param {Object} vars  - Map of variable ID → CivilVar instances
 * @returns {string} HTML string for the form field
 */
function renderFormField(def, vars, isSia) {
  const variable = vars[def.id];
  if (!variable) return '<div class="form-field"></div>';

  const isOverridden = variable.overridden;
  // For overridden values show the raw value; otherwise format it nicely
  const val = isOverridden ? variable.value : (variable.formatted_value || variable.value);
  const displayUnit = def.unit || '-';

  return `
    <div class="form-field">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <label for="inp-${def.prop}">${def.description}</label>
        ${def.editor.group === 'berechnet' ? `
        <label class="override-toggle-container">
          <input type="checkbox" class="override-checkbox" id="chk-${def.prop}" ${isOverridden ? 'checked' : ''} ${isSia ? 'disabled' : ''}>
          <span>Überschreiben</span>
        </label>
        ` : ''}
      </div>
      <div class="input-with-unit">
        <input type="number" step="${def.editor.step}" class="input-control" id="inp-${def.prop}" value="${val}" ${((def.editor.group === 'basis' || isOverridden) && !isSia) ? '' : 'disabled'}>
        <span class="input-unit-label">${displayUnit}</span>
      </div>
    </div>
  `;
}

// =============================================================================
// Editor Groups (rendered from variable definitions)
// =============================================================================

/**
 * Renders a group of form fields under a common heading.
 * Fields can be arranged into rows (side by side) using def.editor.row.
 *
 * @param {string} title - Section heading text
 * @param {Array}  defs  - Array of variable definitions to render in this group
 * @param {Object} vars  - Map of variable ID → CivilVar instances
 * @param {boolean} isSia - Whether the material is a standard SIA material (read-only)
 * @returns {string} HTML string for the editor group
 */
function renderEditorGroup(title, defs, vars, isSia) {
  // Group fields by their row index for side-by-side layout
  const rows = {};
  let maxRow = -1;
  const singleFields = [];

  defs.forEach(def => {
    const row = def.editor.row;
    if (row !== undefined) {
      if (!rows[row]) rows[row] = [];
      rows[row].push(def);
      if (row > maxRow) maxRow = row;
    } else {
      // Fields without a row assignment are rendered individually
      singleFields.push(def);
    }
  });

  let html = `<div class="editor-group"><div class="group-title">${title}</div>`;

  // Render fields that have explicit row assignments
  for (let r = 0; r <= maxRow; r++) {
    if (rows[r]) {
      if (rows[r].length > 1) {
        // Multiple fields in the same row → wrap in a flex container
        html += '<div class="form-row">';
        rows[r].forEach(def => { html += renderFormField(def, vars, isSia); });
        html += '</div>';
      } else {
        // Single field in its row → no wrapper needed
        html += renderFormField(rows[r][0], vars, isSia);
      }
    }
  }

  // Render remaining fields (computed variables without row assignment)
  singleFields.forEach(def => {
    html += renderFormField(def, vars, isSia);
  });

  html += '</div>';
  return html;
}

// =============================================================================
// Main Render Function
// =============================================================================

/**
 * Renders the full parameter editor (middle column) for the currently
 * selected material. Includes the general settings section, fundamental
 * parameters, and computed parameters with override toggles.
 *
 * @param {HTMLElement} panel - The middle panel DOM element
 * @param {Object}      app   - Reference to the MaterialsApp instance
 */
export function renderEditor(panel, app) {
  panel.innerHTML = '';

  const activeMat = app.materialsList.find(m => m.id === app.selectedId);

  // Empty state when no material is selected
  if (!activeMat) {
    panel.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">${getIcon('layers', 48)}</div>
        <h2>Kein Material ausgewählt</h2>
        <p>Bitte wählen Sie links ein Material aus oder erstellen Sie ein neues über den "+"-Button.</p>
      </div>
    `;
    return;
  }

  const result = app._calcResult;
  const defs = (result && result.equations) ? result.equations : [];
  const vars = {};
  defs.forEach(d => { vars[d.id] = d; });

  // ── Header ──────────────────────────────────────────────────────────
  const header = document.createElement('div');
  header.className = 'panel-header';
  header.innerHTML = `<h3>Eigenschaften: ${activeMat.name}</h3>`;
  panel.appendChild(header);

  // ── Content ─────────────────────────────────────────────────────────
  const content = document.createElement('div');
  content.className = 'panel-content editor-card';

  // Split definitions into basis (user-editable) and computed groups
  const basisDefs = defs.filter(d => d.editor.group === 'basis');
  const berechnetDefs = defs.filter(d => d.editor.group === 'berechnet');

  // If this is the only material of its type, force it as default
  const otherMaterialsOfType = app.materialsList.filter(m => m.type === activeMat.type && m.id !== activeMat.id);
  const isOnlyOne = otherMaterialsOfType.length === 0;
  
  if (isOnlyOne) {
    activeMat.is_default = true;
  }

  // General settings section (grade display, name input, default checkbox)
  const isDefaultHtml = `
    <div class="editor-group">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <div class="group-title" style="margin-bottom: 0;">Allgemein</div>
        ${activeMat.is_sia ? `<button id="btn-customize-mat" class="btn btn-primary" style="padding: 4px 12px; font-size: 0.9em;">Material Anpassen</button>` : ''}
      </div>

      <div class="form-field">
        <label for="mat-name">Name des Materials</label>
        <div class="input-with-unit">
          <input type="text" id="mat-name" class="input-control" value="${activeMat.name}" ${activeMat.is_sia ? 'disabled' : ''}>
        </div>
      </div>
      <div class="form-field">
        <label for="mat-index">Kurzbezeichnung (Index)</label>
        <div class="input-with-unit">
          <input type="text" id="mat-index" class="input-control" value="${activeMat.index || activeMat.grade}" ${activeMat.is_sia ? 'disabled' : ''}>
        </div>
      </div>
      <div class="form-field">
        <label for="mat-desc">Beschreibung</label>
        <div class="input-with-unit">
          <input type="text" id="mat-desc" class="input-control" value="${activeMat.description || ''}" ${activeMat.is_sia ? 'disabled' : ''}>
        </div>
      </div>
      <div class="form-field" style="flex-direction:row; justify-content:flex-start;">
        <label style="display:flex; align-items:center; cursor:${isOnlyOne ? 'not-allowed' : 'pointer'};">
          <input type="checkbox" id="chk-is-default" ${activeMat.is_default ? 'checked' : ''} ${isOnlyOne ? 'disabled' : ''} style="margin-right:10px;">
          Als Standard-${activeMat.type === 'concrete' ? 'Beton' : 'Stahl'} verwenden
        </label>
      </div>
    </div>
  `;

  content.innerHTML =
    isDefaultHtml +
    renderEditorGroup('Basisparameter', basisDefs, vars, activeMat.is_sia) +
    renderEditorGroup('Berechnete Parameter (SIA-Normen)', berechnetDefs, vars, activeMat.is_sia);

  panel.appendChild(content);

  // Bind interactive events to the rendered form elements
  bindEditorEvents(panel, activeMat, vars, defs, app);
}

// =============================================================================
// Event Binding
// =============================================================================

/**
 * Wires up all interactive events for the editor panel:
 *   - Material name changes (with uniqueness validation)
 *   - Default material checkbox toggling
 *   - Numeric input changes (basis + computed parameters)
 *   - Override checkbox toggling for computed parameters
 *
 * @param {HTMLElement} panel - The editor panel DOM element
 * @param {Object}      mat   - The active material data object
 * @param {Object}      vars  - Map of variable ID → CivilVar instances
 * @param {Array}       defs  - Variable definitions from the engine
 * @param {Object}      app   - Reference to the MaterialsApp instance
 */
function bindEditorEvents(panel, mat, vars, defs, app) {
  // ── Name input change handler ─────────────────────────────────────
  const inpName = document.getElementById('mat-name');
  if (inpName) {
    inpName.addEventListener('change', (e) => {
      let baseName = e.target.value.trim() || mat.name;
      const rawName = baseName.replace(/_\d+$/, '');
      let finalName = rawName;
      
      // Prevent using names reserved for standard norm materials
      // Since only custom materials can be renamed (SIA ones are disabled),
      // we strictly forbid any exact match with any norm grade.
      const isReserved = VORLAGEN_KEYS.some(g => g === finalName);
      
      if (isReserved) {
         finalName = finalName + '_1';
         alert('Exakte Norm-Namen (z.B. C25/30) sind exklusiv für reine SIA-Materialien reserviert. Der Name wurde angepasst.');
      }
      
      // Ensure uniqueness by appending a counter suffix if necessary
      let counter = 1;
      while (app.materialsList.some(m => m.id !== mat.id && m.name.toLowerCase() === finalName.toLowerCase())) {
        finalName = `${rawName}_${counter++}`;
      }

      mat.name = finalName;
      app.renderAll();
      app.notifyChange();
    });
  }

  // ── Index input change handler ────────────────────────────────────
  const inpIndex = document.getElementById('mat-index');
  if (inpIndex) {
    inpIndex.addEventListener('change', (e) => {
      let baseIndex = e.target.value.trim() || mat.grade;
      const rawIndex = baseIndex.replace(/_\d+$/, '');
      let finalIndex = rawIndex;
      
      // Prevent using names reserved for standard norm materials
      // Since only custom materials can be edited, we strictly forbid exact matches.
      const isReserved = VORLAGEN_KEYS.some(g => g === finalIndex);
      
      if (isReserved) {
         finalIndex = finalIndex + '_1';
         alert('Exakte Norm-Namen (z.B. C25/30) sind exklusiv für reine SIA-Materialien reserviert. Der Index wurde angepasst.');
      }

      // Ensure uniqueness by appending a counter suffix if necessary
      let counter = 1;
      while (app.materialsList.some(m => m.id !== mat.id && m.index.toLowerCase() === finalIndex.toLowerCase())) {
        finalIndex = `${rawIndex}_${counter++}`;
      }

      mat.index = finalIndex;
      app.renderAll();
      app.notifyChange();
    });
  }

  // ── Default material checkbox ─────────────────────────────────────
  const chkDefault = document.getElementById('chk-is-default');
  if (chkDefault) {
    chkDefault.addEventListener('change', () => {
      if (chkDefault.checked) {
        // Unset default on all other materials of the same type first
        app.materialsList.forEach(m => {
          if (m.type === mat.type) m.is_default = false;
        });
        mat.is_default = true;
        app.notifyChange();
      } else {
        // Prevent unchecking – there must always be exactly one default per type
        chkDefault.checked = true;
        alert('Es muss immer genau ein Standard-Material dieses Typs festgelegt sein. Um dies zu ändern, öffnen Sie das gewünschte andere Material und markieren es als Standard.');
      }
    });
  }

  // ── Main input handler (called on any parameter change) ───────────
  /**
   * Reads all input values from the form, updates the material properties,
   * recalculates computed values in real-time, and triggers a report refresh.
   */
  const handleInput = async () => {
    // 1. Read current values from all input fields
    for (const def of defs) {
      const inp = document.getElementById(`inp-${def.prop}`);
      if (!inp) continue;
      
      const isNumber = (def.editor.step !== undefined || def.editor.type === 'number');

      if (def.editor.group === 'basis') {
        // Fundamental parameters: store directly
        mat.properties[def.prop] = isNumber ? Number(inp.value) : inp.value;
      } else if (def.editor.group === 'berechnet') {
        // Computed parameters: check override checkbox state
        const chk = document.getElementById(`chk-${def.prop}`);
        if (chk) {
          mat.properties[`${def.prop}_overridden`] = chk.checked;
          mat.properties[def.prop] = chk.checked ? (isNumber ? Number(inp.value) : inp.value) : null;
        }
      }
    }

    // 2. Recalculate and display updated computed values in real-time
    await app.refreshCalculation();
    const updatedVars = app.getMaterialVars(mat);
    for (const def of defs) {
      if (!mat.properties[`${def.prop}_overridden`]) {
        const inp = document.getElementById(`inp-${def.prop}`);
        const variable = updatedVars[def.id];
        if (inp && variable) {
          inp.value = variable.formatted_value || variable.value;
        }
      }
    }

    // 3. Refresh the LaTeX report and persist changes
    app.renderReport(mat);
    app.notifyChange();
  };

  // ── Description input change handler ──────────────────────────────
  const inpDesc = document.getElementById('mat-desc');
  if (inpDesc) {
    inpDesc.addEventListener('change', (e) => {
      mat.description = e.target.value;
      app.notifyChange();
    });
  }

  // ── Customize material button handler ─────────────────────────────
  const btnCustomize = document.getElementById('btn-customize-mat');
  if (btnCustomize) {
    btnCustomize.addEventListener('click', () => {
      mat.is_sia = false;
      mat.description = '';
      
      // Make name unique
      let finalName = mat.grade + '_1';
      let counter = 1;
      while (app.materialsList.some(m => m.id !== mat.id && m.name.toLowerCase() === finalName.toLowerCase())) {
        counter++;
        finalName = `${mat.grade}_${counter}`;
      }
      mat.name = finalName;
      mat.index = finalName;
      
      app.renderAll();
      app.notifyChange();
    });
  }

  // ── Attach input/change events to all form controls ───────────────
  panel.querySelectorAll('.input-control').forEach(input => {
    input.addEventListener('input', handleInput);
    input.addEventListener('change', handleInput);
  });

  panel.querySelectorAll('input[type="number"].input-control').forEach(input => {
    input.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
        e.preventDefault();
        e.stopPropagation();
        const stepAttr = input.getAttribute('step');
        const step = (stepAttr && stepAttr !== 'any') ? Number(stepAttr) : 1;
        let val = Number(input.value) || 0;
        if (e.key === 'ArrowUp') {
          val += step;
        } else {
          val = Math.max(0, val - step);
        }
        input.value = val;
        input.dispatchEvent(new Event('change', { bubbles: true }));
      }
    });
  });

  // ── Override checkbox events ──────────────────────────────────────
  // When an override checkbox is toggled, enable/disable its input field
  panel.querySelectorAll('.override-checkbox').forEach(chk => {
    chk.addEventListener('change', (e) => {
      const prop = e.target.id.replace('chk-', '');
      const targetInput = document.getElementById(`inp-${prop}`);
      if (targetInput) {
        targetInput.disabled = !e.target.checked;
      }
      handleInput();
    });
  });
}
