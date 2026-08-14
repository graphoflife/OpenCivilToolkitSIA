/**
 * plates/index.js - Hauptmodul der Platten-App
 *
 * UI orchestration only. All computation is delegated to the Python backend
 * via js/api.js. This module renders the sidebar, editor, and report panel,
 * and calls the API whenever calculation results are needed.
 */

import { getIcon } from '../../icons.js';
import { getProjectState, triggerSave } from '../../persistence.js';
import { renderSidebar } from './sidebar.js';
import { renderEditor } from './editor.js';
import { renderReport } from '../../components/reportRenderer.js';
import { drawPlateCrossSection, drawInteractionDiagram } from './diagrams.js';
import { calculatePlate, createNewPlate } from '../../api.js';

export const PlatesApp = {
  id: 'plates',
  title: 'Plattenanalyse',
  icon: getIcon('plates', 24),
  dom: null,
  activePlateId: null,

  activate(dom) {
    this.dom = dom;
    const state = getProjectState();
    if (!state.plates) state.plates = [];
    if (state.plates.length > 0 && !this.activePlateId) {
      this.activePlateId = state.plates[0].id;
    }
    this.render();
  },

  deactivate() {
    this.dom.leftPanel.innerHTML = '';
    this.dom.middlePanel.innerHTML = '';
    this.dom.rightPanel.innerHTML = '';
  },

  render() {
    const state = getProjectState();
    renderSidebar(this.dom.leftPanel, state.plates, this.activePlateId, {
      onSelect: (id) => { this.activePlateId = id; this.render(); },
      onCreate: async () => {
        const name = `Platte ${state.plates.length + 1}`;
        const newPlate = await createNewPlate(name, state.materials || []);
        state.plates.push(newPlate);
        this.activePlateId = newPlate.id;
        triggerSave();
        this.render();
      },
      onDelete: (id) => {
        state.plates = state.plates.filter(p => p.id !== id);
        if (this.activePlateId === id) {
          this.activePlateId = state.plates.length > 0 ? state.plates[0].id : null;
        }
        triggerSave();
        this.render();
      }
    });

    const activePlate = state.plates.find(p => p.id === this.activePlateId);
    if (activePlate) {
      renderEditor(this.dom.middlePanel, activePlate, () => {
        triggerSave();
        this.renderRightPanel(activePlate);
      }, () => this.render());
      this.renderRightPanel(activePlate);
    } else {
      this.dom.middlePanel.innerHTML = `<div class="empty-state">
        <div class="empty-state-icon">${getIcon('plates', 48)}</div>
        <h2>Keine Platte ausgewählt</h2>
        <p>Erstellen Sie links eine neue Platte, um zu beginnen.</p>
      </div>`;
      this.dom.rightPanel.innerHTML = '';
    }
  },

  async renderRightPanel(plate) {
    try {
      const materials = getProjectState().materials || [];
      const { vars: results, sections } = await calculatePlate(plate, materials);

      const einträge = [];
      const alleSchlüssel = [];
      const katexMacros = { "\\diameter": "\\varnothing" };

      sections.forEach(section => {
        alleSchlüssel.push(section.key);

        if (section.type === 'section_title') {
          einträge.push({
            beschreibung: section.title, referenz: '', hinweis: '',
            propSchlüssel: section.key, cssKlasse: 'section-title-card',
            latexString: null, provides: [],
            onRender: () => {},
            onCopy: () => navigator.clipboard.writeText(section.title),
          });

        } else if (section.type === 'drawing') {
          einträge.push({
            beschreibung: section.title, referenz: '', hinweis: '',
            propSchlüssel: section.key, cssKlasse: 'drawing-card',
            onRender: (el) => { el.innerHTML = drawPlateCrossSection(plate, results); },
          });

        } else if (section.type === 'summary' || section.type === 'equation') {
          const latex = section.latex || (section.var && section.var.latex_equation) || '';
          einträge.push({
            beschreibung: section.title, referenz: '', hinweis: '',
            propSchlüssel: section.key, cssKlasse: 'equation-card',
            latexString: latex, provides: section.provides || [],
            onRender: (el) => {
              try { window.katex.render(latex, el, { displayMode: true, throwOnError: false, macros: katexMacros }); }
              catch (err) { el.textContent = latex; }
            },
            onTrace: section.provides && section.provides.length > 0 ? () => {
              this._activateProvides(plate, section.provides, einträge);
            } : null,
            onCopy: () => navigator.clipboard.writeText(`\\[\n${latex}\n\\]`),
          });

        } else if (section.type === 'chart') {
          einträge.push({
            beschreibung: section.title, referenz: '', hinweis: '',
            propSchlüssel: section.key, cssKlasse: 'drawing-card interaction-card',
            provides: section.provides || [],
            onRender: (el) => { el.innerHTML = drawInteractionDiagram(section.dir, results, 600, 800); },
            onTrace: section.provides && section.provides.length > 0 ? () => {
              this._activateProvides(plate, section.provides, einträge);
            } : null,
          });
        }
      });

      alleSchlüssel.forEach(k => {
        if (plate[`${k}_inactive`] === undefined) plate[`${k}_inactive`] = false;
      });

      renderReport(this.dom.rightPanel, {
        titel: plate.name, einträge, eigenschaften: plate, alleSchlüssel,
        onÄnderung: () => triggerSave(),
        onAllesNeuRendern: () => this.renderRightPanel(plate),
      });

    } catch (e) {
      console.error(e);
      this.dom.rightPanel.innerHTML = `<div class="error-card">Fehler bei der Berechnung: ${e.message}</div>`;
    }
  },

  /** Activates report entries whose `provides` list overlaps with the given var IDs or their dependency tree. */
  _activateProvides(plate, providedVars, einträge) {
    const ids = new Set();

    const visit = (v) => {
      if (!v) return;
      const vId = typeof v === 'string' ? v : (v.id || null);
      if (vId && ids.has(vId)) return;
      if (vId) ids.add(vId);

      const deps = typeof v === 'object' ? v.dependencies : null;
      if (deps) {
        if (Array.isArray(deps)) {
          deps.forEach(visit);
        } else if (typeof deps === 'object') {
          Object.values(deps).forEach(visit);
        }
      }
    };

    (providedVars || []).forEach(visit);

    einträge.forEach(e => {
      if (e.provides && e.provides.some(p => {
        const pId = typeof p === 'string' ? p : (p ? p.id : null);
        return pId && ids.has(pId);
      })) {
        plate[`${e.propSchlüssel}_inactive`] = false;
      }
    });

    this.renderRightPanel(plate);
    triggerSave();
  },
};
