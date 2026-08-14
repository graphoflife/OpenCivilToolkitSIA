/**
 * materials/index.js – Hauptmodul der Materialien-App
 *
 * UI orchestration only. Computation delegated to Python backend via api.js.
 */

import { getIcon } from '../../icons.js';
import { copyTextToClipboard, copySvgAsPng } from '../../utils.js';
import { renderReport } from '../../components/reportRenderer.js';
import { renderSidebar } from './sidebar.js';
import { renderEditor } from './editor.js';
import { drawDiagram } from './diagrams.js';
import { showAddMaterialModal } from './modal.js';
import { calculateMaterial } from '../../api.js';


export const MaterialsApp = {
  id: 'materials',
  title: 'Materialdefinition',
  icon: getIcon('materials', 24),

  dom: null,
  materialsList: [],
  selectedId: null,
  onStateChangeCallback: null,

  // Last calculation result cache { equations, extras, all_property_keys }
  _calcResult: null,

  getMaterialVars(mat) {
    if (this._calcResult && this._calcResult.equations) {
      const vars = {};
      this._calcResult.equations.forEach(eq => { vars[eq.id] = eq; });
      return vars;
    }
    return {};
  },

  activate(dom, appState, onStateChange) {
    this.dom = dom;
    this.materialsList = appState || [];
    this.onStateChangeCallback = onStateChange;
    this.updateSelection();
    this.renderAll();
  },

  deactivate() {
    this.dom = null;
    this.materialsList = [];
    this.selectedId = null;
    this._calcResult = null;
  },

  loadState(appState) {
    this.materialsList = appState || [];
    this.updateSelection();
    this.renderAll();
  },

  updateSelection() {
    if (this.materialsList.length > 0) {
      if (!this.selectedId || !this.materialsList.some(m => m.id === this.selectedId)) {
        this.selectedId = this.materialsList[0].id;
      }
    } else {
      this.selectedId = null;
    }
  },

  notifyChange() {
    if (this.onStateChangeCallback) this.onStateChangeCallback(this.materialsList);
  },

  async renderAll() {
    this.renderSidebar();
    
    const activeMat = this.materialsList.find(m => m.id === this.selectedId);
    if (!activeMat) {
      this._calcResult = null;
      this.renderEditor();
      this.renderReport(null);
      return;
    }

    try {
      this._calcResult = await calculateMaterial(activeMat);
    } catch (apiErr) {
      console.error('[MaterialsApp] Backend API calculation failed:', apiErr);
      this._calcResult = null;
      this.dom.middlePanel.innerHTML = `
        <div class="error-card" style="margin: 20px;">
          <h3>Backend-Verbindung fehlgeschlagen</h3>
          <p>${apiErr.message}</p>
          <p>Bitte stellen Sie sicher, dass der Python-Server läuft: <code>uvicorn main:app</code></p>
        </div>`;
      this.dom.rightPanel.innerHTML = '';
      return;
    }
    
    this.renderEditor();
    this.renderReport(activeMat);
  },

  renderSidebar() { renderSidebar(this.dom.leftPanel, this); },
  renderEditor()  { renderEditor(this.dom.middlePanel, this); },

  async refreshCalculation() {
    const activeMat = this.materialsList.find(m => m.id === this.selectedId);
    if (!activeMat) return;
    try {
      this._calcResult = await calculateMaterial(activeMat);
    } catch (apiErr) {
      console.error('[MaterialsApp] API calculation failed during refresh:', apiErr);
      this._calcResult = null;
    }
  },

  async renderReport(activeMat = this.materialsList.find(m => m.id === this.selectedId)) {
    if (!activeMat) {
      renderReport(this.dom.rightPanel, {
        titel: '', einträge: [], eigenschaften: {}, alleSchlüssel: [],
        onÄnderung: () => {}, onAllesNeuRendern: () => {},
      });
      return;
    }

    try {
      const result = this._calcResult;
      const { equations, extras, all_property_keys } = result;
      const katexMacros = { "\\diameter": "\\varnothing" };
      const einträge = [];

      // 1. Equation cards from computed CivilVars
      for (const eq of equations) {
        einträge.push({
          beschreibung: eq.description,
          referenz: eq.overridden ? '' : (eq.reference || ''),
          hinweis: eq.overridden ? 'manuell überschrieben' : '',
          propSchlüssel: eq.prop,
          cssKlasse: 'equation-card',
          latexString: eq.latex_equation,
          onRender: (el) => {
            try { window.katex.render(eq.latex_equation, el, { displayMode: true, throwOnError: false, macros: katexMacros }); }
            catch (err) { el.textContent = eq.latex_equation; }
          },
          onTrace: () => this._traceAndActivate(activeMat, eq.id || eq.var_id, all_property_keys, equations),
          onCopy: () => copyTextToClipboard(`\\[ ${eq.latex_equation} \\]`),
        });
      }

      // 2. Extras (formulas and diagrams)
      for (const extra of extras) {
        if (extra.type === 'formula') {
          einträge.push({
            beschreibung: extra.title, referenz: extra.reference, hinweis: '',
            propSchlüssel: extra.id, cssKlasse: 'equation-card',
            latexString: extra.latex,
            onRender: (el) => {
              try { window.katex.render(extra.latex, el, { displayMode: true, throwOnError: false, macros: katexMacros }); }
              catch (err) { el.textContent = extra.latex; }
            },
            onTrace: () => this._traceExtraDeps(activeMat, extra, all_property_keys, equations),
            onCopy: () => copyTextToClipboard(`\\[ ${extra.latex} \\]`),
          });
        } else if (extra.type === 'diagram') {
          const varMap = {};
          equations.forEach(eq => {
            varMap[eq.id] = eq;
            if (eq.var_id) varMap[eq.var_id] = eq;
            if (eq.prop) varMap[eq.prop] = eq;
            const cleanId = (eq.id || '').replace(/_id_[a-z0-9]+$/i, '');
            if (cleanId) varMap[cleanId] = eq;
          });
          const svg = drawDiagram(extra.diagram_type || extra.diagramType, varMap);
          einträge.push({
            beschreibung: extra.title, referenz: extra.reference, hinweis: '',
            propSchlüssel: extra.id, cssKlasse: 'drawing-card',
            svgElement: svg,
            onRender: (el) => {
              el.innerHTML = '';
              el.appendChild(svg);
            },
            onTrace: () => this._traceExtraDeps(activeMat, extra, all_property_keys, equations),
            onCopy: () => copySvgAsPng(svg, `${activeMat.name}_diagramm.png`),
          });
        }
      }

      renderReport(this.dom.rightPanel, {
        titel: activeMat.name, einträge,
        eigenschaften: activeMat.properties, alleSchlüssel: all_property_keys,
        onÄnderung: () => this.notifyChange(),
        onAllesNeuRendern: () => this.renderReport(),
      });

    } catch (err) {
      console.error('[MaterialsApp] Calculation error:', err);
      this.dom.rightPanel.innerHTML = `<div class="error-card">Fehler: ${err.message}</div>`;
    }
  },



  /** Activate all vars in the dep chain of a given variable ID. */
  _traceAndActivate(mat, varId, allKeys, equations) {
    const visited = new Set();
    const visit = (id) => {
      if (!id || visited.has(id)) return;
      visited.add(id);
      const eq = equations.find(e => e.id === id || e.var_id === id || e.prop === id);
      if (eq) {
        mat.properties[`${eq.prop}_inactive`] = false;
        const deps = eq.dep_ids || eq.dependencies || [];
        if (Array.isArray(deps)) {
          deps.forEach(visit);
        } else if (typeof deps === 'object') {
          Object.values(deps).forEach(v => visit(typeof v === 'string' ? v : v.id));
        }
      }
    };
    visit(varId);
    this.renderAll();
    this.notifyChange();
  },

  _traceExtraDeps(mat, extra, allKeys, equations) {
    for (const depId of (extra.dependencies || [])) {
      const eq = equations.find(e => e.id === depId || e.var_id === depId);
      if (eq) mat.properties[`${eq.prop}_inactive`] = false;
    }
    mat.properties[`${extra.id}_inactive`] = false;
    this.renderAll();
    this.notifyChange();
  },

  showAddMaterialModal() {
    showAddMaterialModal(this);
  },
};

