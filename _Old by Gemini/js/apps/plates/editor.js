/**
 * plates/editor.js – Mittlere Spalte: Eingabemasken für Platten.
 * 
 * VERANTWORTLICHKEIT:
 * Rendert die UI-Komponenten (HTML), um die Eigenschaften einer Platte
 * (Geometrie, Bewehrung) zu bearbeiten.
 * Organisiert Bewehrungslagen (hinzufügen, löschen, anordnen) und
 * synchronisiert alle Eingaben direkt in das `plate`-Objekt.
 */

import { getIcon } from '../../icons.js';
import { getProjectState } from '../../persistence.js';
import { computePlateLayers } from './diagrams.js';

function createNewLayerLocal(mainDir = 'x') {
  return {
    main_dir: mainDir,
    pos_mode: 'standard',
    clear_dist: 0,
    steel_id: '',
    x: { active: mainDir === 'x', diam: mainDir === 'x' ? 12 : 0, type: 'spacing', spacing: 150, count: 0 },
    y: { active: mainDir === 'y', diam: mainDir === 'y' ? 12 : 0, type: 'spacing', spacing: 150, count: 0 },
  };
}

function createFormField(id, label, unit, value, type = 'number', step = '1') {
  return `
    <div class="form-field">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <label for="${id}">${label}</label>
      </div>
      <div class="input-with-unit">
        <input type="${type}" step="${step}" class="input-control" id="${id}" value="${value}">
        <span class="input-unit-label">${unit}</span>
      </div>
    </div>
  `;
}

function createReadonlyField(label, unit, value) {
  return `
    <div class="form-field">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <label>${label}</label>
      </div>
      <div class="input-with-unit">
        <input type="text" class="input-control" value="${value}" disabled style="background-color: var(--color-bg-input-disabled); color: var(--color-text-muted);">
        <span class="input-unit-label">${unit}</span>
      </div>
    </div>
  `;
}

function createSelectField(id, label, optionsHtml, value = '') {
  // We use replace to inject selected if needed, or it's pre-rendered in optionsHtml
  return `
    <div class="form-field">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <label for="${id}">${label}</label>
      </div>
      <select class="input-control" id="${id}">
        <option value="">-- Bitte wählen --</option>
        ${optionsHtml}
      </select>
    </div>
  `;
}

function createWidthField(plate) {
  return `
    <div class="form-field">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <label for="plate-b">Plattenbreite b</label>
        <label class="override-toggle-container">
          <input type="checkbox" class="override-checkbox" id="plate-is-1m" ${plate.is_plate_1m ? 'checked' : ''}>
          <span>Platte (1000mm)</span>
        </label>
      </div>
      <div class="input-with-unit">
        <input type="number" step="50" class="input-control" id="plate-b" value="${plate.is_plate_1m ? 1000 : plate.b_mm}" ${plate.is_plate_1m ? 'disabled' : ''}>
        <span class="input-unit-label">mm</span>
      </div>
    </div>
  `;
}

export function renderEditor(container, plate, onChange, onFullUpdate) {
  const state = getProjectState();
  const allMaterials = state.materials || [];
  const concretes = allMaterials.filter(m => m.type === 'concrete' || m.id.startsWith('beton_'));
  const steels = allMaterials.filter(m => m.type === 'steel' || m.id.startsWith('stahl_'));
  
  const concreteOptions = concretes.map(m => 
    `<option value="${m.id}" ${plate.concrete_id === m.id ? 'selected' : ''}>${m.name}</option>`
  ).join('');

  // Auto-fallback für ungültige Beton-Zuordnungen
  const defaultConcrete = concretes.find(m => m.is_default) || concretes[0];
  if (plate.concrete_id && !concretes.some(m => m.id === plate.concrete_id)) {
    plate.concrete_id = defaultConcrete ? defaultConcrete.id : '';
    if (onChange) onChange();
  }

  // Auto-fallback für ungültige Stahl-Zuordnungen
  const defaultSteel = steels.find(m => m.is_default) || steels[0];
  let changedSteel = false;
  
  plate.bottom_layers.forEach(layer => {
    if (layer.steel_id && !steels.some(m => m.id === layer.steel_id)) {
      layer.steel_id = defaultSteel ? defaultSteel.id : '';
      changedSteel = true;
    }
  });
  plate.top_layers.forEach(layer => {
    if (layer.steel_id && !steels.some(m => m.id === layer.steel_id)) {
      layer.steel_id = defaultSteel ? defaultSteel.id : '';
      changedSteel = true;
    }
  });
  
  if (changedSteel && onChange) onChange();

  let html = `
    <div class="panel-header">
      <h3>Platten Parameter & Bewehrung</h3>
    </div>
    <div class="panel-content editor-card" style="display: grid; grid-template-columns: minmax(300px, 1fr) minmax(400px, 1.5fr); gap: 24px; align-items: start;">
      
      <!-- Linke Spalte: Parameter -->
      <div class="editor-column" style="display: flex; flex-direction: column; gap: 16px;">
        <div class="editor-group">
          <div class="group-title">Allgemein</div>
          ${createFormField('plate-name', 'Name der Platte', '', plate.name, 'text')}
        </div>

        <div class="editor-group">
          <div class="group-title">Geometrie</div>
          <div class="form-row">
            ${createFormField('plate-h', 'Plattendicke h', 'mm', plate.h_mm, 'number', '10')}
            ${createWidthField(plate)}
          </div>
        </div>
        
        <div class="editor-group">
          <div class="group-title">Material & Überdeckung</div>
          ${createSelectField('plate-concrete', 'Betonsorte', concreteOptions)}
          ${createFormField('plate-dmax', 'Grösstkorndurchmesser', 'mm', plate.D_max !== undefined ? plate.D_max : 32, 'number', '1')}
          <div class="form-row">
            ${createFormField('plate-cover-bottom', 'Untere Überdeckung', 'mm', plate.cover_bottom, 'number', '5')}
            ${createFormField('plate-cover-top', 'Obere Überdeckung', 'mm', plate.cover_top, 'number', '5')}
          </div>
        </div>
      </div>

      <!-- Rechte Spalte: Bewehrung Lagen -->
      <div class="editor-column" style="display: flex; flex-direction: column; gap: 16px;">
        <div class="editor-group">
          <div class="group-title" style="display:flex; justify-content:space-between; align-items:center;">
            <span>Bewehrung Lagen (Unten)</span>
            <label style="font-size: 0.85rem; color: var(--color-text-muted); display:flex; align-items:center; font-weight:normal;">
              <input type="checkbox" id="plate-opt-bot" ${plate.optimal_einlegen_bottom ? 'checked' : ''} style="margin-right: 5px;"> Optimales Einlegen
            </label>
          </div>
          <div id="layers-bottom-container"></div>
          <button id="btn-add-bottom-layer" class="btn btn-secondary" style="margin-top:10px;">
            ${getIcon('plus', 14)} Lage Unten hinzufügen
          </button>
        </div>
        
        <div class="editor-group">
          <div class="group-title" style="display:flex; justify-content:space-between; align-items:center;">
            <span>Bewehrung Lagen (Oben)</span>
            <label style="font-size: 0.85rem; color: var(--color-text-muted); display:flex; align-items:center; font-weight:normal;">
              <input type="checkbox" id="plate-opt-top" ${plate.optimal_einlegen_top ? 'checked' : ''} style="margin-right: 5px;"> Optimales Einlegen
            </label>
          </div>
          <div id="layers-top-container"></div>
          <button id="btn-add-top-layer" class="btn btn-secondary" style="margin-top:10px;">
            ${getIcon('plus', 14)} Lage Oben hinzufügen
          </button>
        </div>
      </div>

    </div>
  `;

  container.innerHTML = html;

  const updateLayers = () => {
    const computed = computePlateLayers(plate);
    renderLayersList(container.querySelector('#layers-bottom-container'), plate.bottom_layers, 'bottom', steels, computed.bottom, () => { onChange(); updateLayers(); });
    renderLayersList(container.querySelector('#layers-top-container'), plate.top_layers, 'top', steels, computed.top, () => { onChange(); updateLayers(); });
  };

  // Bind base inputs
  const bindInput = (id, prop, isNumber = true) => {
    const el = container.querySelector('#' + id);
    if(el) {
      el.addEventListener('change', (e) => {
        if (el.type === 'checkbox') {
          plate[prop] = e.target.checked;
        } else {
          plate[prop] = isNumber ? Number(e.target.value) : e.target.value;
        }
        onChange();
        if (id === 'plate-name' && onFullUpdate) onFullUpdate();
        if (id === 'plate-cover-top' || id === 'plate-cover-bottom' || id === 'plate-opt-bot' || id === 'plate-opt-top') updateLayers();
      });
    }
  };
  
  bindInput('plate-name', 'name', false);
  bindInput('plate-h', 'h_mm');
  bindInput('plate-b', 'b_mm');
  bindInput('plate-concrete', 'concrete_id', false);
  bindInput('plate-dmax', 'D_max');
  bindInput('plate-cover-top', 'cover_top');
  bindInput('plate-cover-bottom', 'cover_bottom');
  bindInput('plate-opt-bot', 'optimal_einlegen_bottom', false);
  bindInput('plate-opt-top', 'optimal_einlegen_top', false);

  const chk1m = container.querySelector('#plate-is-1m');
  if (chk1m) {
    chk1m.addEventListener('change', (e) => {
      plate.is_plate_1m = e.target.checked;
      if (plate.is_plate_1m) plate.b_mm = 1000;
      onChange();
      if (onFullUpdate) onFullUpdate();
    });
  }
  
  updateLayers();

  const defaultSteelId = defaultSteel ? defaultSteel.id : '';

  container.querySelector('#btn-add-bottom-layer').addEventListener('click', () => {
    const layer = createNewLayerLocal('x');
    layer.steel_id = defaultSteelId;
    plate.bottom_layers.push(layer);
    onChange();
    updateLayers();
  });
  
  container.querySelector('#btn-add-top-layer').addEventListener('click', () => {
    const layer = createNewLayerLocal('x');
    layer.steel_id = defaultSteelId;
    plate.top_layers.push(layer);
    onChange();
    updateLayers();
  });

  bindArrowKeyNavigation(container);
}

function renderLayersList(container, layers, position, steels, computedData, onChangeAndReRender) {
  if (layers.length === 0) {
    container.innerHTML = '<div class="empty-state-small" style="padding: 10px; color: var(--color-text-muted); font-size: 0.9rem;">Keine Lagen definiert</div>';
    return;
  }
  
  const steelOptions = steels.map(m => `<option value="${m.id}">${m.name}</option>`).join('');

  let html = '';
  layers.forEach((layer, idx) => {
    const isX = layer.main_dir === 'x';
    const isY = layer.main_dir === 'y';
    const dirData = isX ? layer.x : layer.y;
    
    const comp = computedData[idx];
    const centerDist = comp.bottom_edge_dist + (dirData.diam / 2);
    const computedDistStr = centerDist.toFixed(1);
    
    const isZulage = comp.is_zulage;
    const globalNumStr = comp.global_num ? `${comp.global_num}. Lage${isZulage ? ' (Zulage)' : ''}` : `Lage ${idx + 1}`;
    const color = comp.color || 'var(--color-text)';
    
    html += `
      <div class="layer-card" style="border: 1px solid var(--color-border); border-left: 4px solid ${color}; padding: 12px; border-radius: 6px; margin-bottom: 12px; background: rgba(0,0,0,0.1);">
        <div style="display:flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
          <strong style="font-size: 0.95rem; color: ${color};">
            ${globalNumStr} <span style="color:var(--color-text-muted); font-weight:normal; font-size:0.85rem;">(von unten)</span>
          </strong>
          <div class="instance-actions" style="opacity: 1;">
            <button class="btn-item-action btn-layer-up" data-idx="${idx}" title="Nach oben verschieben" ${idx === 0 ? 'disabled' : ''} style="padding:4px;">${getIcon('arrowUp', 16)}</button>
            <button class="btn-item-action btn-layer-down" data-idx="${idx}" title="Nach unten verschieben" ${idx === layers.length - 1 ? 'disabled' : ''} style="padding:4px;">${getIcon('arrowDown', 16)}</button>
            <button class="btn-item-action btn-remove-layer delete" data-idx="${idx}" title="Löschen" style="padding:4px;">${getIcon('trash', 16)}</button>
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-field">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <label>Richtung</label>
            </div>
            <select class="input-control layer-dir" data-idx="${idx}">
              <option value="x" ${isX ? 'selected' : ''}>X (Längs)</option>
              <option value="y" ${isY ? 'selected' : ''}>Y (Quer)</option>
            </select>
          </div>
          
          <div class="form-field">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <label>Stahlsorte</label>
            </div>
            <select class="input-control layer-steel" data-idx="${idx}">
              <option value="" ${!layer.steel_id ? 'selected' : ''}>-- Bitte wählen --</option>
              ${steels.map(m => `<option value="${m.id}" ${layer.steel_id === m.id ? 'selected' : ''}>${m.name}</option>`).join('')}
            </select>
          </div>
        </div>
        <div class="form-row">
          <div class="form-field">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <label>Positionierung</label>
            </div>
            <select class="input-control layer-pos-mode" data-idx="${idx}">
              <option value="standard" ${layer.pos_mode === 'standard' ? 'selected' : ''}>-- Standard --</option>
              <option value="zulage" ${layer.pos_mode === 'zulage' ? 'selected' : ''}>Zulage (Gleiche Höhe)</option>
            </select>
          </div>
          ${layer.pos_mode === 'zulage'
              ? '<div class="form-field"></div>'
              : createFormField(`layer-clear-dist-${position}-${idx}`, 'Zusätzliche Überdeckung', 'mm', layer.clear_dist)
          }
        </div>

        <div class="form-row">
          <div class="form-field">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <label>Art</label>
            </div>
            <select class="input-control layer-type" data-idx="${idx}">
              <option value="spacing" ${dirData.type === 'spacing' ? 'selected' : ''}>Teilung (Abstand)</option>
              <option value="count" ${dirData.type === 'count' ? 'selected' : ''}>Anzahl (Stk)</option>
            </select>
          </div>
          ${createFormField(`layer-diam-${position}-${idx}`, 'Durchmesser', 'mm', dirData.diam, 'number', '2')}
          ${dirData.type === 'spacing' 
            ? createFormField(`layer-spacing-${position}-${idx}`, 'Teilung', 'mm', dirData.spacing, 'number', '25')
            : createFormField(`layer-count-${position}-${idx}`, 'Anzahl', 'Stk', dirData.count, 'number', '1')}
        </div>
        
        <div class="form-row" style="margin-top: 10px;">
          ${createReadonlyField(`Absoluter Abstand zur Kante`, 'mm', computedDistStr)}
        </div>
      </div>
    `;
  });
  
  container.innerHTML = html;
  
  // Bind events
  container.querySelectorAll('.btn-remove-layer').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const idx = Number(e.currentTarget.dataset.idx);
      layers.splice(idx, 1);
      onChangeAndReRender();
    });
  });
  
  container.querySelectorAll('.btn-layer-up').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const idx = Number(e.currentTarget.dataset.idx);
      if (idx > 0) {
        const temp = layers[idx];
        layers[idx] = layers[idx - 1];
        layers[idx - 1] = temp;
        onChangeAndReRender();
      }
    });
  });

  container.querySelectorAll('.btn-layer-down').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const idx = Number(e.currentTarget.dataset.idx);
      if (idx < layers.length - 1) {
        const temp = layers[idx];
        layers[idx] = layers[idx + 1];
        layers[idx + 1] = temp;
        onChangeAndReRender();
      }
    });
  });
  
  container.querySelectorAll('.layer-dir').forEach(sel => {
    sel.addEventListener('change', (e) => {
      const idx = Number(e.currentTarget.dataset.idx);
      layers[idx].main_dir = e.currentTarget.value;
      // Copy data from old dir to new dir to preserve values
      if (e.currentTarget.value === 'x') {
        layers[idx].x.diam = layers[idx].y.diam;
        layers[idx].x.spacing = layers[idx].y.spacing;
        layers[idx].y.diam = 0;
        layers[idx].y.spacing = 0;
      } else {
        layers[idx].y.diam = layers[idx].x.diam;
        layers[idx].y.spacing = layers[idx].x.spacing;
        layers[idx].x.diam = 0;
        layers[idx].x.spacing = 0;
      }
      onChangeAndReRender();
    });
  });

  container.querySelectorAll('.layer-steel').forEach(sel => {
    sel.addEventListener('change', (e) => {
      const idx = Number(e.currentTarget.dataset.idx);
      layers[idx].steel_id = e.currentTarget.value;
      onChangeAndReRender();
    });
  });

  container.querySelectorAll('.layer-type').forEach(sel => {
    sel.addEventListener('change', (e) => {
      const idx = Number(e.currentTarget.dataset.idx);
      const isX = layers[idx].main_dir === 'x';
      if (isX) layers[idx].x.type = e.target.value;
      else layers[idx].y.type = e.target.value;
      onChangeAndReRender();
    });
  });

  container.querySelectorAll('.layer-pos-mode').forEach(sel => {
    sel.addEventListener('change', (e) => {
      const idx = Number(e.currentTarget.dataset.idx);
      layers[idx].pos_mode = e.target.value;
      onChangeAndReRender();
    });
  });

  // Bind dynamically created inputs
  layers.forEach((layer, idx) => {
    const isX = layer.main_dir === 'x';
    const dirData = isX ? layer.x : layer.y;
    const diamInp = container.querySelector(`#layer-diam-${position}-${idx}`);
    const spacingInp = container.querySelector(`#layer-spacing-${position}-${idx}`);
    const countInp = container.querySelector(`#layer-count-${position}-${idx}`);
    const absPosInp = container.querySelector(`#layer-abs-pos-${position}-${idx}`);
    const clearDistInp = container.querySelector(`#layer-clear-dist-${position}-${idx}`);
    
    if (diamInp) {
      diamInp.addEventListener('change', (e) => {
        dirData.diam = Number(e.target.value);
        onChangeAndReRender();
      });
    }
    
    if (spacingInp) {
      spacingInp.addEventListener('change', (e) => {
        dirData.spacing = Number(e.target.value);
        onChangeAndReRender();
      });
    }

    if (countInp) {
      countInp.addEventListener('change', (e) => {
        dirData.count = Number(e.target.value);
        onChangeAndReRender();
      });
    }

    if (absPosInp) {
      absPosInp.addEventListener('change', (e) => {
        layer.absolute_pos = Number(e.target.value);
        onChangeAndReRender();
      });
    }

    if (clearDistInp) {
      clearDistInp.addEventListener('change', (e) => {
        layer.clear_dist = Number(e.target.value);
        onChangeAndReRender();
      });
    }
  });

  bindArrowKeyNavigation(container);
}

function bindArrowKeyNavigation(container) {
  if (!container) return;
  container.querySelectorAll('input[type="number"].input-control').forEach(inp => {
    if (inp._arrowNavBound) return;
    inp._arrowNavBound = true;

    inp.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
        e.preventDefault();
        e.stopPropagation();
        const stepAttr = inp.getAttribute('step');
        const step = (stepAttr && stepAttr !== 'any') ? Number(stepAttr) : 1;
        let val = Number(inp.value) || 0;
        if (e.key === 'ArrowUp') {
          val += step;
        } else {
          val = Math.max(0, val - step);
        }
        inp.value = val;
        inp.dispatchEvent(new Event('change', { bubbles: true }));
      }
    });
  });
}

