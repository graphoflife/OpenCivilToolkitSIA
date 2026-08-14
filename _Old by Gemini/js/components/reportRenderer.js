/**
 * components/reportRenderer.js – Reusable LaTeX report component.
 *
 * RESPONSIBILITY:
 * Generates the entire right HTML column (report panel). Takes an abstract array
 * of `einträge` (entries) and transforms them into rendered LaTeX equation lines,
 * SVG drawing cards, and formula lines.
 *
 * KEY FEATURES:
 *   - Overleaf-style document rendering: Clean, flowing document layout
 *     resembling a real LaTeX/Overleaf PDF output.
 *   - Hover interactions: Each line reveals action buttons on hover
 *     (copy, toggle visibility, trace dependencies, expand diagram).
 *   - Dependency tracing: Clicking the trace button fires an event telling the app
 *     which variables are needed, activating them in the report.
 *   - LaTeX copy: Converts the entire visible report into raw LaTeX markup
 *     (with embedded PNG images) and copies it to the clipboard.
 *   - Visibility toggling: Individual lines or all lines can be shown/hidden.
 *   - SVG pan-zoom: Drawing entries are interactive (pan, zoom) via svg-pan-zoom library.
 *
 * ENTRY TYPES:
 *   - 'equation-card': KaTeX-rendered mathematical equation (now rendered as document line)
 *   - 'drawing-card': Interactive SVG diagram with pan-zoom
 */

import { getIcon } from '../icons.js';
import { copyTextToClipboard, copySvgAsPng, showToast, showDiagramModal } from '../utils.js';

// =============================================================================
// KaTeX Rendering Helper
// =============================================================================

/**
 * Renders a LaTeX string into a DOM container using KaTeX.
 * Falls back to plain text display if KaTeX is unavailable or throws an error.
 *
 * @param {string}      latex     - The LaTeX expression to render
 * @param {HTMLElement}  container - Target DOM element for the rendered output
 */
function renderLatex(latex, container) {
  if (!window.katex) {
    container.textContent = latex;
    return;
  }
  try {
    window.katex.render(latex, container, {
      displayMode: true,
      throwOnError: false,
      macros: { "\\diameter": "\\varnothing" }
    });
  } catch (err) {
    console.error('[reportRenderer] KaTeX rendering error:', err);
    container.textContent = latex;
  }
}

// =============================================================================
// SVG Pan-Zoom Setup (for drawing entries)
// =============================================================================

/**
 * Initializes responsive SVG sizing on an SVG element within a drawing entry.
 * Also sets up a ResizeObserver to keep the diagram responsive when
 * panel widths change (e.g. via drag resizers).
 *
 * @param {HTMLElement} renderEl - The container element holding the SVG
 */
function initSvgPanZoom(renderEl) {
  if (!window.svgPanZoom) return;

  const svgEl = renderEl.querySelector('svg');
  if (!svgEl) return;

  // Parse viewBox dimensions for aspect ratio calculation
  const viewBox = svgEl.getAttribute('viewBox');
  let vbW = 600, vbH = 400;
  if (viewBox) {
    const parts = viewBox.split(' ').map(parseFloat);
    if (parts.length === 4 && parts[2] > 0 && parts[3] > 0) {
      vbW = parts[2];
      vbH = parts[3];
    }
  }
  const aspectRatio = vbW / vbH;

  // Calculate initial height based on container width and viewBox aspect ratio
  let computedHeight = renderEl.clientWidth / aspectRatio;
  // Cap height to prevent overly tall diagrams
  if (computedHeight > renderEl.clientWidth) {
    computedHeight = renderEl.clientWidth;
  }

  // Set initial SVG dimensions
  svgEl.style.width = '100%';
  let lastWidth = renderEl.clientWidth;
  if (lastWidth > 0) {
    svgEl.style.height = computedHeight + 'px';
  }

  // NOTE: Pan-zoom is NOT initialized on inline diagrams.
  // It is only activated when the user clicks "Diagramm vergrößern" (modal view).
  // This prevents accidental zooming when scrolling the report panel.

  // Keep diagram responsive when the panel is resized
  const resizeObserver = new ResizeObserver(entries => {
    for (const entry of entries) {
      const newWidth = entry.contentRect.width;
      // Only update if width actually changed (avoid infinite loops)
      if (newWidth > 0 && Math.abs(newWidth - lastWidth) > 1) {
        let newHeight = newWidth / aspectRatio;
        if (newHeight > newWidth) newHeight = newWidth;

        svgEl.style.height = newHeight + 'px';
        lastWidth = newWidth;
      } else if (newWidth > 0 && lastWidth === 0) {
        // Container was hidden initially, now visible — initialize dimensions
        let newHeight = newWidth / aspectRatio;
        if (newHeight > newWidth) newHeight = newWidth;

        svgEl.style.height = newHeight + 'px';
        lastWidth = newWidth;
      }
    }
  });
  resizeObserver.observe(renderEl);
}

// =============================================================================
// Single Report Line (Overleaf-style)
// =============================================================================

/**
 * Creates a single report line DOM element styled like an Overleaf document line.
 * On hover, action buttons appear as a floating toolbar.
 *
 * @param {Object}   eintrag              - Line configuration
 * @param {string}   eintrag.beschreibung - Description text (title line)
 * @param {string}   eintrag.referenz     - Norm reference (e.g. "SIA 262:2025:2.4.2.3")
 * @param {string}   eintrag.hinweis      - Optional hint (e.g. "manuell überschrieben")
 * @param {boolean}  eintrag.aktiv        - Whether the line is active (not dimmed)
 * @param {string}   eintrag.cssKlasse    - CSS class ('equation-card' or 'drawing-card')
 * @param {Function} eintrag.onRender     - Callback(el) to render content into the line body
 * @param {Function} eintrag.onToggle     - Callback when visibility toggle is clicked
 * @param {Function} eintrag.onCopy       - Callback when copy button is clicked
 * @param {Function} [eintrag.onTrace]    - Optional callback for "activate dependencies"
 * @returns {HTMLElement} The constructed line DOM element
 */
function erstelleKarte(eintrag) {
  const isDrawing = eintrag.cssKlasse && eintrag.cssKlasse.includes('drawing-card');
  const isTitle = eintrag.cssKlasse && eintrag.cssKlasse.includes('section-title-card');

  if (isTitle) {
    const line = document.createElement('div');
    line.className = 'report-separator-title';
    line.innerHTML = `<h4>${eintrag.beschreibung}</h4>`;
    return line;
  }

  const line = document.createElement('div');
  line.className = 'report-line' + (isDrawing ? ' report-line-drawing' : '');
  if (!eintrag.aktiv) {
    line.classList.add('inactive-line');
  }

  // ── Title row with description and references ──────────────────────
  const title = document.createElement('div');
  title.className = 'report-line-title';

  const hinweisHtml = eintrag.hinweis
    ? `<span class="report-line-ref report-line-hint">${eintrag.hinweis}</span>`
    : '';
  const refHtml = eintrag.referenz
    ? `<span class="report-line-ref">(${eintrag.referenz})</span>`
    : '';

  title.innerHTML = `
    <span class="report-line-desc">${eintrag.beschreibung}</span>
    <span style="display:flex; gap:6px; align-items:center; margin-left:auto;">
      ${hinweisHtml}
      ${refHtml}
    </span>
  `;
  line.appendChild(title);

  // ── Content render area ────────────────────────────────────────────
  const renderEl = document.createElement('div');
  renderEl.className = isDrawing ? 'report-line-drawing-content' : 'report-line-content';
  line.appendChild(renderEl);

  if (eintrag.onRender) {
    eintrag.onRender(renderEl);
  }

  // Set up responsive SVG sizing for drawing entries (no pan-zoom in inline view)
  if (isDrawing) {
    requestAnimationFrame(() => initSvgPanZoom(renderEl));
  }

  // ── Floating action buttons (visible on hover) ─────────────────────
  const actionsEl = document.createElement('div');
  actionsEl.className = 'report-line-actions';

  // "Expand" and "Reset view" buttons for SVG diagrams
  if (isDrawing) {
    // Expand: opens diagram in a full-screen modal with pan-zoom
    const expandBtn = document.createElement('button');
    expandBtn.className = 'report-action-btn';
    expandBtn.title = 'Diagramm vergrößern';
    expandBtn.innerHTML = getIcon('maximize', 13);
    expandBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const svgEl = renderEl.querySelector('svg');
      if (svgEl) {
        // Clone the SVG for a clean modal view
        const clone = svgEl.cloneNode(true);
        clone.removeAttribute('style');
        clone.style.width = '100%';
        clone.style.height = '100%';
        showDiagramModal(eintrag.beschreibung, clone.outerHTML);
      }
    });
    actionsEl.appendChild(expandBtn);
  }

  // "Activate dependencies" button (traces the variable dependency tree)
  if (eintrag.onTrace) {
    const traceBtn = document.createElement('button');
    traceBtn.className = 'report-action-btn';
    traceBtn.title = 'Abhängigkeiten aktivieren';
    traceBtn.innerHTML = getIcon('trace', 13);
    traceBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      eintrag.onTrace();
    });
    actionsEl.appendChild(traceBtn);
  }

  // Visibility toggle button (show/hide this line in the report)
  const toggleBtn = document.createElement('button');
  toggleBtn.className = 'report-action-btn';
  toggleBtn.title = eintrag.aktiv ? 'Deaktivieren' : 'Aktivieren';
  toggleBtn.innerHTML = eintrag.aktiv ? getIcon('eye', 13) : getIcon('eyeOff', 13);
  toggleBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    eintrag.onToggle();
  });
  actionsEl.appendChild(toggleBtn);

  // Copy button (copies LaTeX or PNG depending on entry type)
  const copyBtn = document.createElement('button');
  copyBtn.className = 'report-action-btn';
  copyBtn.title = 'Kopieren';
  copyBtn.innerHTML = getIcon('copy', 13);
  copyBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    eintrag.onCopy();
  });
  actionsEl.appendChild(copyBtn);

  line.appendChild(actionsEl);
  return line;
}

// =============================================================================
// SVG → Base64 PNG Conversion (for "Copy Report" feature)
// =============================================================================

/**
 * Converts an SVG element to a Base64-encoded PNG data URL.
 * Used when copying the full report to clipboard with embedded images.
 *
 * @param {SVGElement} svgElement - The SVG element to convert
 * @returns {Promise<string|null>} PNG data URL, or null on failure
 */
function svgToBase64Png(svgElement) {
  return new Promise((resolve) => {
    if (!svgElement) {
      resolve(null);
      return;
    }

    const svgString = new XMLSerializer().serializeToString(svgElement);
    const svgBlob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(svgBlob);

    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement('canvas');
      const scale = 2; // 2× for HiDPI output
      canvas.width = (parseInt(svgElement.getAttribute('width'), 10) || 460) * scale;
      canvas.height = (parseInt(svgElement.getAttribute('height'), 10) || 280) * scale;
      const ctx = canvas.getContext('2d');
      // Fill with dark background to match the app theme
      ctx.fillStyle = '#0d1324';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.scale(scale, scale);
      ctx.drawImage(img, 0, 0);
      URL.revokeObjectURL(url);
      resolve(canvas.toDataURL('image/png'));
    };
    img.onerror = () => {
      console.warn('[reportRenderer] Failed to convert SVG to PNG.');
      URL.revokeObjectURL(url);
      resolve(null);
    };
    img.src = url;
  });
}

// =============================================================================
// Main Render Function
// =============================================================================

/**
 * Renders a complete LaTeX calculation report into a panel.
 *
 * @param {HTMLElement} panel  - The right panel DOM element
 * @param {Object}      config - Report configuration
 *
 * @param {string}   config.titel             - Report title (e.g. "Beton C30/37")
 * @param {Array}    config.einträge          - Array of report entries (see entry format below)
 * @param {Object}   config.eigenschaften     - Properties object (reads/writes _inactive flags)
 * @param {string[]} config.alleSchlüssel     - All property keys (for "show/hide all")
 * @param {Function} config.onÄnderung       - Callback when visibility state changes
 * @param {Function} config.onAllesNeuRendern - Callback for full re-render
 *
 * Entry format:
 *   { beschreibung, referenz, hinweis, propSchlüssel,
 *     cssKlasse, onRender, onCopy, onTrace?,
 *     latexString?, svgElement? }
 */
export function renderReport(panel, config) {
  panel.innerHTML = '';

  const {
    titel,
    einträge,
    eigenschaften,
    alleSchlüssel,
    onÄnderung,
    onAllesNeuRendern,
  } = config;

  // ── Empty state ─────────────────────────────────────────────────────
  if (!einträge || einträge.length === 0) {
    panel.innerHTML = `
      <div class="empty-state">
        <h2>LaTeX Bericht</h2>
        <p>Wählen Sie links eine Instanz aus, um den formatierten Bericht anzuzeigen.</p>
      </div>
    `;
    return;
  }

  // Check if any entries are currently hidden (for toggle-all button label)
  const anyInactive = Array.isArray(alleSchlüssel) &&
    alleSchlüssel.some(k => eigenschaften[k + '_inactive'] === true);

  // ── Report header toolbar ───────────────────────────────────────────
  const header = document.createElement('div');
  header.className = 'report-header';
  header.innerHTML = `
    <h3 style="font-size:0.9rem;">LaTeX-Berechnungsbericht</h3>
    <div class="report-actions" style="display:flex; align-items:center; gap:6px;">
      <label class="active-toggle-container" style="font-size:0.8rem; font-weight:normal; margin-right:8px; display:flex; align-items:center; gap:4px;">
        <input type="checkbox" id="chk-global-active-only" ${eigenschaften.only_active_in_report ? 'checked' : ''}>
        <span>Nur aktive Parameter anzeigen</span>
      </label>
      <button class="btn btn-secondary btn-sm" id="btn-toggle-all-visibility" title="${anyInactive ? 'Alle Parameter einblenden' : 'Alle Parameter ausblenden'}">
        ${anyInactive
          ? getIcon('eye', 14, 'margin-right:3px; display:inline-block; vertical-align:middle;') + ' Alle einblenden'
          : getIcon('eyeOff', 14, 'margin-right:3px; display:inline-block; vertical-align:middle;') + ' Alle ausblenden'}
      </button>
      <button class="btn btn-secondary btn-sm" id="btn-copy-latex" title="Gesamten LaTeX-Bericht in Zwischenablage kopieren">
        ${getIcon('copy', 14, 'margin-right:3px; display:inline-block; vertical-align:middle;')}
        Bericht kopieren
      </button>
    </div>
  `;
  panel.appendChild(header);

  // "Show only active" filter checkbox
  const chkActiveOnly = header.querySelector('#chk-global-active-only');
  if (chkActiveOnly) {
    chkActiveOnly.addEventListener('change', (e) => {
      eigenschaften.only_active_in_report = e.target.checked;
      onAllesNeuRendern();
      onÄnderung();
    });
  }

  // "Show/hide all" toggle button
  const btnToggleAll = header.querySelector('#btn-toggle-all-visibility');
  if (btnToggleAll) {
    btnToggleAll.addEventListener('click', () => {
      const zielZustand = !anyInactive; // toggle: if any are inactive → show all, else hide all
      alleSchlüssel.forEach(k => {
        eigenschaften[k + '_inactive'] = zielZustand;
      });
      onAllesNeuRendern();
      onÄnderung();
    });
  }

  // ── Document body (Overleaf-style paper) ────────────────────────────
  const paper = document.createElement('div');
  paper.className = 'report-paper';

  // Apply "active only" filter if enabled
  const gefilterteEinträge = eigenschaften.only_active_in_report
    ? einträge.filter(e => eigenschaften[e.propSchlüssel + '_inactive'] !== true)
    : einträge;

  // Create a document line for each visible entry
  gefilterteEinträge.forEach(eintrag => {
    const istAktiv = eigenschaften[eintrag.propSchlüssel + '_inactive'] !== true;

    const line = erstelleKarte({
      beschreibung: eintrag.beschreibung,
      referenz: istAktiv ? eintrag.referenz : '',
      hinweis: eintrag.hinweis || '',
      aktiv: istAktiv,
      cssKlasse: eintrag.cssKlasse || 'equation-card',
      onRender: eintrag.onRender,
      onTrace: eintrag.onTrace,
      onToggle: () => {
        // Toggle: if currently active → deactivate, and vice versa
        eigenschaften[eintrag.propSchlüssel + '_inactive'] = istAktiv;
        onAllesNeuRendern();
        onÄnderung();
      },
      onCopy: eintrag.onCopy,
    });

    paper.appendChild(line);
  });

  panel.appendChild(paper);

  // ── "Copy Report" button handler ────────────────────────────────────
  const btnCopyLatex = header.querySelector('#btn-copy-latex');
  if (btnCopyLatex) {
    btnCopyLatex.addEventListener('click', async () => {
      // Build a LaTeX document from all visible entries
      let latexDoc = `% Materialdefinition: ${titel}\n`;
      latexDoc += `\\subsection*{Materialdefinition - ${titel}}\n`;
      latexDoc += `\\begin{align*}\n`;

      const svgPromises = [];

      gefilterteEinträge.forEach(eintrag => {
        if (eintrag.latexString) {
          // Convert "=" to "&=" for align* environment
          latexDoc += `  ${eintrag.latexString.replaceAll(' = ', ' &= ')} \\\\\n`;
        }
        if (eintrag.svgElement) {
          svgPromises.push(svgToBase64Png(eintrag.svgElement));
        }
      });

      latexDoc += `\\end{align*}\n`;

      // Convert SVG diagrams to PNG and append as comments
      const pngDataUrls = await Promise.all(svgPromises);
      pngDataUrls.forEach((dataUrl, i) => {
        if (dataUrl) {
          latexDoc += `\n% Diagramm ${i + 1} (als Base64-Bild eingebettet)\n`;
          latexDoc += `% Bild kann in LaTeX mit \\includegraphics eingefügt werden\n`;
        }
      });

      // Build an HTML version with embedded images for rich clipboard paste
      let htmlDoc = `<h3>Materialdefinition - ${titel}</h3>`;
      gefilterteEinträge.forEach(eintrag => {
        if (eintrag.latexString) {
          htmlDoc += `<p>\\[ ${eintrag.latexString} \\]</p>`;
        }
      });
      pngDataUrls.forEach(dataUrl => {
        if (dataUrl) {
          htmlDoc += `<p><img src="${dataUrl}" style="max-width:460px;"></p>`;
        }
      });

      // Write both HTML and plain text to clipboard for maximum compatibility
      try {
        const textBlob = new Blob([latexDoc], { type: 'text/plain' });
        const htmlBlob = new Blob([htmlDoc], { type: 'text/html' });
        await navigator.clipboard.write([
          new ClipboardItem({
            'text/plain': textBlob,
            'text/html': htmlBlob,
          }),
        ]);
        showToast('Bericht (inkl. Bilder) in Zwischenablage kopiert!');
      } catch (err) {
        // Fallback: copy plain LaTeX text only
        console.warn('[reportRenderer] HTML clipboard copy failed, falling back to text:', err);
        copyTextToClipboard(latexDoc);
      }
    });
  }
}
