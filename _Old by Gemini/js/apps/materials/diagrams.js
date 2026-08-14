/**
 * diagrams.js – SVG stress-strain diagrams for concrete and steel.
 *
 * RESPONSIBILITY:
 * Generates SVG diagrams for material properties visualization:
 *   - Simplified rectangular stress-strain diagram for concrete (SIA 262:2025:4.2.1.4)
 *   - Parabola-rectangle stress-strain diagram for concrete (SIA 262:2025:4.2.1.6)
 *   - Elastic-ideoplastic stress-strain diagram for steel (SIA 262:2025:4.2.2.4)
 *
 * Each diagram function receives the computed CivilVar variables and returns
 * SVG markup strings that are assembled into a complete SVG element by drawDiagram().
 */

/** @type {string} SVG namespace URI */
const SVG_NS = 'http://www.w3.org/2000/svg';

/** Shared CSS styles injected into every generated SVG */
const SVG_STYLE = `
  .axis { stroke: #4b5563; stroke-width: 1.5; }
  .grid { stroke: #1f2937; stroke-width: 1; stroke-dasharray: 2,2; }
  .curve { stroke: #3b82f6; stroke-width: 2.5; fill: none; }
  .curve-simplified { stroke: #22c55e; stroke-width: 2; fill: none; stroke-dasharray: 6,3; }
  .text { fill: #9ca3af; font-family: sans-serif; font-size: 11px; }
  .bold-text { fill: #ffffff; font-family: sans-serif; font-size: 12px; font-weight: bold; }
  .marker { fill: #ef4444; }
  .marker-simplified { fill: #22c55e; }
  .legend-text { fill: #9ca3af; font-family: sans-serif; font-size: 10px; }
`;

// ── Chart area boundaries (in viewBox coordinates) ──────────────────
/** @type {number} Left edge of the chart area */
const X_MIN = 100;
/** @type {number} Right edge of the chart area */
const X_MAX = 410;
/** @type {number} Top edge of the chart area */
const Y_MIN = 30;
/** @type {number} Bottom edge of the chart area (axis origin) */
const Y_MAX = 220;

// =============================================================================
// Shared Helpers
// =============================================================================

/**
 * Generates SVG markup for X and Y axes with arrow heads and labels.
 *
 * @param {string} strainLabel - HTML label for the X axis (strain, ε)
 * @param {string} stressLabel - HTML label for the Y axis (stress, σ)
 * @returns {string} SVG markup for the axes
 */
function zeichneAchsen(strainLabel, stressLabel) {
  return `
    <line class="axis" x1="${X_MIN}" y1="${Y_MAX}" x2="${X_MAX + 15}" y2="${Y_MAX}"/>
    <line class="axis" x1="${X_MIN}" y1="${Y_MAX}" x2="${X_MIN}" y2="${Y_MIN - 10}"/>
    <path d="M ${X_MAX + 15},${Y_MAX - 3} L ${X_MAX + 20},${Y_MAX} L ${X_MAX + 15},${Y_MAX + 3} Z" fill="#4b5563"/>
    <path d="M ${X_MIN - 3},${Y_MIN - 10} L ${X_MIN},${Y_MIN - 15} L ${X_MIN + 3},${Y_MIN - 10} Z" fill="#4b5563"/>
    <text class="text" x="${X_MAX + 22}" y="${Y_MAX + 4}">${strainLabel}</text>
    <text class="text" x="${X_MIN}" y="${Y_MIN - 22}" text-anchor="middle">${stressLabel}</text>
  `;
}

/**
 * Creates a blank SVG element with the shared style definitions and
 * standard viewBox dimensions.
 *
 * @returns {SVGElement} An empty SVG element ready for content
 */
function erstelleSvg() {
  const svg = document.createElementNS(SVG_NS, 'svg');
  svg.setAttribute('width', '100%');
  svg.style.height = 'auto';
  svg.setAttribute('viewBox', '0 0 460 290');
  svg.style.backgroundColor = '#0d1324';
  svg.innerHTML = `<style>${SVG_STYLE}</style>`;
  return svg;
}

/**
 * Safely reads a numeric value from a CivilVar, returning null if the
 * variable is missing or has no value.
 *
 * @param {Object} vars - Map of variable ID → CivilVar instances
 * @param {string} key  - Variable ID to look up
 * @returns {number|null} The variable's value, or null
 */
function safeValue(vars, key) {
  const v = vars[key];
  return (v && v.value != null) ? v.value : null;
}

// =============================================================================
// Concrete: Simplified Rectangular Diagram (SIA 262:2025:4.2.1.4)
// =============================================================================

/**
 * Draws the simplified rectangular stress-strain diagram for concrete.
 * Shows a step function: zero stress up to a threshold, then constant f_cd
 * up to the ultimate strain ε_c2d.
 *
 * @param {Object} vars - CivilVar variables (needs f_cd, eps_c2d)
 * @returns {string} SVG markup, or empty string if required data is missing
 */
function zeichneVereinfacht(vars) {
  const fcd = safeValue(vars, 'f_cd');
  const ec2dRaw = safeValue(vars, 'eps_c2d');
  if (fcd == null || ec2dRaw == null) return '';

  // Convert strain from absolute to ‰ for display
  const ec2d = ec2dRaw * 1000;

  // Coordinate mapping functions (data space → SVG space)
  const mapX = (s) => X_MIN + (s / ec2d) * (X_MAX - X_MIN);
  const mapY = (s) => Y_MAX - (s / fcd) * (Y_MAX - Y_MIN);

  // The rectangular step starts at 15% of ultimate strain
  const ecStart = ec2d * 0.15;

  const pathD = `M ${mapX(0)},${mapY(0)} L ${mapX(ecStart)},${mapY(0)} L ${mapX(ecStart)},${mapY(fcd)} L ${mapX(ec2d)},${mapY(fcd)} L ${mapX(ec2d)},${mapY(0)}`;

  return `
    <line class="grid" x1="${mapX(ecStart)}" y1="${Y_MIN}" x2="${mapX(ecStart)}" y2="${Y_MAX}"/>
    <line class="grid" x1="${mapX(ec2d)}" y1="${Y_MIN}" x2="${mapX(ec2d)}" y2="${Y_MAX}"/>
    <line class="grid" x1="${X_MIN}" y1="${mapY(fcd)}" x2="${X_MAX}" y2="${mapY(fcd)}"/>
    <path class="curve" d="${pathD}"/>
    <circle class="marker" cx="${mapX(ecStart)}" cy="${mapY(fcd)}" r="4"/>
    <circle class="marker" cx="${mapX(ec2d)}" cy="${mapY(fcd)}" r="4"/>
    <text class="text" x="${mapX(ecStart) - 15}" y="${Y_MAX + 16}">${ecStart.toFixed(3)}</text>
    <text class="text" x="${mapX(ec2d) - 10}" y="${Y_MAX + 16}">${ec2d.toFixed(3)}</text>
    <text class="bold-text" x="${X_MIN - 8}" y="${mapY(fcd) + 4}" text-anchor="end">f<tspan font-size="9" baseline-shift="sub">cd</tspan> = ${fcd.toFixed(1)} MPa</text>
    <text class="text" x="230" y="265" text-anchor="middle">Vereinfachtes Spannungs-Dehnungs-Diagramm (SIA 262:2025:4.2.1.4)</text>
  `;
}

// =============================================================================
// Concrete: Parabola-Rectangle Diagram (SIA 262:2025:4.2.1.6)
//   with Simplified Rectangular Overlay (SIA 262:2025:4.2.1.4)
// =============================================================================

/**
 * Generates the simplified rectangular stress-strain path as an SVG overlay.
 * Used inside the parabola-rectangle diagram for visual comparison.
 * Uses a distinct color (green, dashed) to differentiate from the main curve.
 *
 * @param {Object} vars - CivilVar variables (needs f_cd, eps_c2d)
 * @param {Function} mapX - X coordinate mapping function
 * @param {Function} mapY - Y coordinate mapping function
 * @param {number} ec2d - Ultimate strain in ‰
 * @param {number} fcd - Design compressive strength in MPa
 * @returns {string} SVG markup for the overlay, or empty string if data is missing
 */
function zeichneVereinfachtOverlay(vars, mapX, mapY, ec2d, fcd) {
  const ecStart = ec2d * 0.15;

  const pathD = `M ${mapX(0)},${mapY(0)} L ${mapX(ecStart)},${mapY(0)} L ${mapX(ecStart)},${mapY(fcd)} L ${mapX(ec2d)},${mapY(fcd)} L ${mapX(ec2d)},${mapY(0)}`;

  return `
    <line class="grid" x1="${mapX(ecStart)}" y1="${Y_MIN}" x2="${mapX(ecStart)}" y2="${Y_MAX}" style="stroke:#22c55e; stroke-opacity:0.4;"/>
    <path class="curve-simplified" d="${pathD}"/>
    <circle class="marker-simplified" cx="${mapX(ecStart)}" cy="${mapY(fcd)}" r="3"/>
    <circle class="marker-simplified" cx="${mapX(ec2d)}" cy="${mapY(fcd)}" r="3"/>
    <text class="text" x="${mapX(ecStart)}" y="${Y_MAX + 16}" text-anchor="middle" style="fill:#22c55e; font-size:10px;">${ecStart.toFixed(3)}</text>
  `;
}

/**
 * Draws the parabola-rectangle stress-strain diagram for concrete,
 * with the simplified rectangular diagram overlaid in a different color.
 * Shows a curved parabolic region (0 → ε_c1d) followed by a constant
 * stress plateau (ε_c1d → ε_c2d), plus the simplified step-function overlay.
 *
 * @param {Object} vars - CivilVar variables (needs f_cd, eps_c1d, eps_c2d, k_sigma)
 * @returns {string} SVG markup, or empty string if required data is missing
 */
function zeichneParabel(vars) {
  const fcd = safeValue(vars, 'f_cd');
  const ec1dRaw = safeValue(vars, 'eps_c1d');
  const ec2dRaw = safeValue(vars, 'eps_c2d');
  const kSigma = safeValue(vars, 'k_sigma');
  if (fcd == null || ec1dRaw == null || ec2dRaw == null || kSigma == null) return '';

  // Convert strain from absolute to ‰
  const ec1d = ec1dRaw * 1000;
  const ec2d = ec2dRaw * 1000;

  // Coordinate mapping functions
  const mapX = (s) => X_MIN + (s / ec2d) * (X_MAX - X_MIN);
  const mapY = (s) => Y_MAX - (s / fcd) * (Y_MAX - Y_MIN);

  // Generate points along the parabolic curve
  const points = [];
  const steps = 30;
  for (let i = 0; i <= steps; i++) {
    const e = (ec1d * i) / steps;
    // ζ = normalized strain ratio
    const zeta = (e / 1000) / ec1dRaw;
    let sigma = 0;
    if (zeta > 0) {
      // Sargin formula: σ = f_cd · (k_σ·ζ - ζ²) / (1 + (k_σ - 2)·ζ)
      sigma = fcd * (kSigma * zeta - Math.pow(zeta, 2)) / (1 + (kSigma - 2) * zeta);
    }
    points.push({ x: mapX(e), y: mapY(sigma) });
  }
  // Constant stress plateau and closing path
  points.push({ x: mapX(ec2d), y: mapY(fcd) });
  points.push({ x: mapX(ec2d), y: mapY(0) });

  const pathD = `M ${points[0].x},${points[0].y} ` +
    points.slice(1).map(p => `L ${p.x},${p.y}`).join(' ');

  // Simplified overlay (using same coordinate mapping)
  const simplifiedOverlay = zeichneVereinfachtOverlay(vars, mapX, mapY, ec2d, fcd);

  // Legend for both curves
  const legendY = 255;
  const legend = `
    <line x1="140" y1="${legendY}" x2="160" y2="${legendY}" class="curve" stroke-width="2"/>
    <text class="legend-text" x="164" y="${legendY + 4}">Parabel-Rechteck (SIA 262:2025:4.2.1.6)</text>
    <line x1="140" y1="${legendY + 14}" x2="160" y2="${legendY + 14}" class="curve-simplified" stroke-width="2"/>
    <text class="legend-text" x="164" y="${legendY + 18}">Vereinfacht (SIA 262:2025:4.2.1.4)</text>
  `;

  return `
    <line class="grid" x1="${mapX(ec1d)}" y1="${Y_MIN}" x2="${mapX(ec1d)}" y2="${Y_MAX}"/>
    <line class="grid" x1="${mapX(ec2d)}" y1="${Y_MIN}" x2="${mapX(ec2d)}" y2="${Y_MAX}"/>
    <line class="grid" x1="${X_MIN}" y1="${mapY(fcd)}" x2="${X_MAX}" y2="${mapY(fcd)}"/>
    <path class="curve" d="${pathD}"/>
    ${simplifiedOverlay}
    <circle class="marker" cx="${mapX(ec1d)}" cy="${mapY(fcd)}" r="4"/>
    <circle class="marker" cx="${mapX(ec2d)}" cy="${mapY(fcd)}" r="4"/>
    <text class="text" x="${mapX(ec1d) - 10}" y="${Y_MAX + 16}">${ec1d.toFixed(2)}</text>
    <text class="text" x="${mapX(ec2d) - 10}" y="${Y_MAX + 16}">${ec2d.toFixed(2)}</text>
    <text class="bold-text" x="${X_MIN - 8}" y="${mapY(fcd) + 4}" text-anchor="end">f<tspan font-size="9" baseline-shift="sub">cd</tspan> = ${fcd.toFixed(1)} MPa</text>
    ${legend}
  `;
}

// =============================================================================
// Steel: Elastic-Ideoplastic Diagram (SIA 262:2025:4.2.2.4)
// =============================================================================

/**
 * Draws the elastic-ideoplastic stress-strain diagram for reinforcing steel.
 * Shows a bilinear curve symmetric about the origin with:
 *   - Linear elastic region (slope = E_s)
 *   - Constant yield plateau at ±f_yd
 *   - Custom axes centered in the chart area (origin at center)
 *
 * @param {Object} vars - CivilVar variables (needs f_yd, f_yd_minus, E_s, eps_ud)
 * @returns {string} SVG markup, or empty string if required data is missing
 */
function zeichneStahl(vars) {
  const fyd = safeValue(vars, 'f_yd');
  const fyd_minus = safeValue(vars, 'f_yd_minus');
  const Es = safeValue(vars, 'E_s');
  if (fyd == null || fyd_minus == null || Es == null) return '';

  // Calculate yield strains from Hook's law: ε_y = f_yd / E_s
  const esy = fyd / Es * 1000;          // tension yield strain [‰]
  const esy_minus = -fyd_minus / Es * 1000; // compression yield strain [‰]

  // Ultimate design strain (with fallback)
  const epsUdRaw = safeValue(vars, 'eps_ud');
  const eud = (epsUdRaw || 4.5) * 10;   // convert % to ‰
  const eud_minus = -eud;

  // Center point for the steel diagram (origin at chart center)
  const cx = (X_MIN + X_MAX) / 2;
  const cy = (Y_MIN + Y_MAX) / 2;

  // Coordinate mapping: centered at (cx, cy), scaled to chart dimensions
  const mapX = (s) => cx + (s / eud) * ((X_MAX - X_MIN) / 2);
  // Scale Y by whichever yield strength is larger (for symmetric appearance)
  const maxF = Math.max(fyd, fyd_minus);
  const mapY = (s) => cy - (s / maxF) * ((Y_MAX - Y_MIN) / 2);

  // Bilinear path: compression plateau → elastic slope → tension plateau
  const pathD = `M ${mapX(eud_minus)},${mapY(-fyd_minus)} L ${mapX(esy_minus)},${mapY(-fyd_minus)} L ${mapX(esy)},${mapY(fyd)} L ${mapX(eud)},${mapY(fyd)}`;

  return `
    <line class="axis" x1="${X_MIN}" y1="${cy}" x2="${X_MAX + 15}" y2="${cy}"/>
    <line class="axis" x1="${cx}" y1="${Y_MAX}" x2="${cx}" y2="${Y_MIN - 10}"/>
    <path d="M ${X_MAX + 15},${cy - 3} L ${X_MAX + 20},${cy} L ${X_MAX + 15},${cy + 3} Z" fill="#4b5563"/>
    <path d="M ${cx - 3},${Y_MIN - 10} L ${cx},${Y_MIN - 15} L ${cx + 3},${Y_MIN - 10} Z" fill="#4b5563"/>
    <text class="text" x="${X_MAX + 22}" y="${cy + 4}">&epsilon;<tspan font-size="8" baseline-shift="sub">s</tspan> [‰]</text>
    <text class="text" x="${cx}" y="${Y_MIN - 22}" text-anchor="middle">&sigma;<tspan font-size="8" baseline-shift="sub">s</tspan> [MPa]</text>

    <line class="grid" x1="${mapX(esy)}" y1="${cy}" x2="${mapX(esy)}" y2="${mapY(fyd)}"/>
    <line class="grid" x1="${mapX(esy_minus)}" y1="${cy}" x2="${mapX(esy_minus)}" y2="${mapY(-fyd_minus)}"/>
    <line class="grid" x1="${cx}" y1="${mapY(fyd)}" x2="${mapX(esy)}" y2="${mapY(fyd)}"/>
    <line class="grid" x1="${cx}" y1="${mapY(-fyd_minus)}" x2="${mapX(esy_minus)}" y2="${mapY(-fyd_minus)}"/>
    
    <path class="curve" d="${pathD}"/>
    
    <circle class="marker" cx="${mapX(esy)}" cy="${mapY(fyd)}" r="4"/>
    <circle class="marker" cx="${mapX(eud)}" cy="${mapY(fyd)}" r="4"/>
    <circle class="marker" cx="${mapX(esy_minus)}" cy="${mapY(-fyd_minus)}" r="4"/>
    <circle class="marker" cx="${mapX(eud_minus)}" cy="${mapY(-fyd_minus)}" r="4"/>
    
    <text class="text" x="${mapX(esy) - 5}" y="${cy + 14}" text-anchor="middle">${esy.toFixed(2)}</text>
    <text class="text" x="${mapX(eud) - 10}" y="${mapY(fyd) - 10}">${eud.toFixed(1)}</text>
    <text class="text" x="${mapX(esy_minus) + 5}" y="${cy - 8}" text-anchor="middle">${esy_minus.toFixed(2)}</text>
    <text class="text" x="${mapX(eud_minus) + 10}" y="${mapY(-fyd_minus) + 16}">${eud_minus.toFixed(1)}</text>
    
    <text class="bold-text" x="${cx - 8}" y="${mapY(fyd) + 4}" text-anchor="end">f<tspan font-size="9" baseline-shift="sub">yd</tspan> = ${fyd.toFixed(0)} MPa</text>
    <text class="bold-text" x="${cx + 8}" y="${mapY(-fyd_minus) + 4}" text-anchor="start">f<tspan font-size="9" baseline-shift="sub">yd</tspan><tspan font-size="9" baseline-shift="super">-</tspan> = ${-fyd_minus.toFixed(0)} MPa</text>
    
    <text class="text" x="230" y="265" text-anchor="middle">Elastisch-ideoplastisch (SIA 262:2025:4.2.2.4)</text>
    <!-- NO_DEFAULT_AXES -->
  `;
}

// =============================================================================
// Public API
// =============================================================================

/**
 * Registry mapping diagram type identifiers to their drawing functions
 * and axis label configurations.
 *
 * @type {Object<string, {fn: Function, strain: string, stress: string}>}
 */
const ZEICHNER = {
  parabola:   { fn: zeichneParabel,     strain: '&epsilon;<tspan font-size="8" baseline-shift="sub">c</tspan> [‰]', stress: '&sigma;<tspan font-size="8" baseline-shift="sub">c</tspan> [MPa]' },
  steel:      { fn: zeichneStahl,       strain: '&epsilon;<tspan font-size="8" baseline-shift="sub">s</tspan> [‰]', stress: '&sigma;<tspan font-size="8" baseline-shift="sub">s</tspan> [MPa]' },
};

/**
 * Draws a stress-strain diagram as an SVG element.
 *
 * @param {string} typ  - Diagram type: 'parabola' or 'steel'
 * @param {Object} vars - CivilVar variables providing the numeric data
 * @returns {SVGElement} A fully constructed SVG element ready for DOM insertion
 */
export function drawDiagram(typ, vars) {
  const config = ZEICHNER[typ];
  if (!config) {
    console.error(`[diagrams] Unknown diagram type: "${typ}". Valid types: ${Object.keys(ZEICHNER).join(', ')}`);
    return document.createElementNS(SVG_NS, 'svg');
  }

  const svg = erstelleSvg();
  const inner = config.fn(vars);

  // Append the diagram content
  svg.innerHTML += inner;

  // Add standard axes unless the diagram provides its own (e.g. steel)
  // The sentinel comment <!-- NO_DEFAULT_AXES --> signals custom axis handling
  if (!inner.includes('NO_DEFAULT_AXES')) {
    svg.innerHTML += zeichneAchsen(config.strain, config.stress);
  }

  return svg;
}
