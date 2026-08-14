/**
 * plates/diagrams.js – Generierung der Platten-Zeichnungen.
 * 
 * VERANTWORTLICHKEIT:
 * Erzeugt dynamische SVG-Grafiken für den Plattenquerschnitt.
 * Nimmt die von der plateEngine berechneten Lagen (Abstände, Durchmesser)
 * und zeichnet sie maßstabsgetreu in einen Betonquerschnitt ein.
 * 
 * ABGRENZUNG:
 * - Enthält keine Berechnungslogik für Statik, nur Rendering-Logik für SVG.
 */

const LAYER_COLORS = [
  "#3b82f6", "#ef4444", "#10b981", "#f59e0b",
  "#8b5cf6", "#ec4899", "#14b8a6", "#6366f1",
];

export function computePlateLayers(plate) {
  const processSide = (layers, cover, optimal) => {
    let nextEnv = cover;
    let computedLayers = [];
    let currentGroup = null;
    let groupCounter = 0;

    (layers || []).forEach((layer, idx) => {
      const mainDir = layer.main_dir;
      const rebar = layer[mainDir] || {};
      if (!rebar || rebar.diam <= 0) {
        computedLayers.push({ layer, main_dir: mainDir, bottom_edge_dist: nextEnv, group_idx: -1, global_num: -1, is_zulage: false });
        currentGroup = null;
        return;
      }
      const diam = rebar.diam;
      if (layer.pos_mode === 'zulage' && currentGroup && currentGroup.mainDir === mainDir) {
        currentGroup.layers.push({ layer, idx, diam, is_zulage: true });
        currentGroup.maxDiam = Math.max(currentGroup.maxDiam, diam);
      } else {
        currentGroup = {
          mainDir, layers: [{ layer, idx, diam, is_zulage: false }],
          maxDiam: diam, clearDist: layer.clear_dist || 0, groupIdx: groupCounter++
        };
      }
      const clear = currentGroup.clearDist;
      const outer = nextEnv + clear;
      const inner = outer + currentGroup.maxDiam;
      currentGroup.layers.forEach(item => {
        const bed = optimal ? outer : (inner - item.diam);
        computedLayers.push({
          layer: item.layer, main_dir: mainDir, bottom_edge_dist: bed,
          group_idx: currentGroup.groupIdx, is_zulage: item.is_zulage
        });
      });
      nextEnv = inner;
    });

    return computedLayers;
  };

  const botLayers = processSide(plate.bottom_layers, plate.cover_bottom, plate.optimal_einlegen_bottom !== false);
  const topLayers = processSide(plate.top_layers, plate.cover_top, plate.optimal_einlegen_top === true);

  botLayers.forEach(c => {
    if (c.group_idx >= 0) {
      c.global_num = c.group_idx + 1;
      c.color = LAYER_COLORS[(c.global_num - 1) % LAYER_COLORS.length];
    }
  });
  topLayers.forEach(c => {
    if (c.group_idx >= 0) {
      c.global_num = botLayers.length + c.group_idx + 1;
      c.color = LAYER_COLORS[(c.global_num - 1) % LAYER_COLORS.length];
    }
  });
  return { bottom: botLayers, top: topLayers };
}

export function drawPlateCrossSection(plate, results, width = 600, height = 250) {
  const marginX = 50;
  const marginY = 30;
  
  // Calculate scale
  const drawWidth = width - 2 * marginX;
  const drawHeight = height - 2 * marginY;
  
  const h = plate.h_mm;
  const b = plate.b_mm; // For plates often 1000
  
  const scale = Math.min(drawWidth / b, drawHeight / h);
  
  const scaledH = h * scale;
  const scaledB = b * scale;
  
  const cx = width / 2;
  const cy = height / 2;
  
  const startX = cx - scaledB / 2;
  const startY = cy - scaledH / 2;

  let svg = `<svg viewBox="0 0 ${width} ${height}" width="100%" xmlns="http://www.w3.org/2000/svg">`;
  
  // Definitions for concrete hatch and dashed edges
  svg += `
    <defs>
      <pattern id="concreteHatch" width="10" height="10" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
        <line x1="0" y1="0" x2="0" y2="10" stroke="rgba(255,255,255,0.05)" stroke-width="1"/>
      </pattern>
    </defs>
  `;
  
  // Concrete block
  svg += `<rect x="${startX}" y="${startY}" width="${scaledB}" height="${scaledH}" fill="url(#concreteHatch)" stroke="var(--color-border)" stroke-width="2" />`;
  
  // Dimension labels
  svg += `<text x="${cx}" y="${startY - 10}" fill="var(--color-text)" font-size="14" font-family="sans-serif" text-anchor="middle">b = ${b} mm</text>`;
  svg += `<text x="${startX - 15}" y="${cy}" fill="var(--color-text)" font-size="14" font-family="sans-serif" text-anchor="middle" transform="rotate(-90, ${startX - 15}, ${cy})">h = ${h} mm</text>`;
  
  const computed = (results && results.computed) ? results.computed : computePlateLayers(plate);

  // Draw Rebars
  const drawRebars = (computedLayers, isTop) => {
    let signatureGroups = {};
    computedLayers.forEach(comp => {
      const rebar = comp.layer[comp.main_dir];
      if (!rebar || rebar.diam <= 0 || comp.main_dir !== 'x') return;
      let sig = rebar.type === 'count' ? `count-${rebar.count}` : `spacing-${rebar.spacing}`;
      if (!signatureGroups[sig]) signatureGroups[sig] = [];
      signatureGroups[sig].push(comp);
    });

    for (let sig in signatureGroups) {
      signatureGroups[sig].forEach((comp, idx) => {
        comp._staggerIndex = idx;
        comp._staggerTotal = signatureGroups[sig].length;
      });
    }

    let drawnCircles = [];

    const drawCircles = (comp, rebar, rCenterY, dScaled, color, opacity) => {
      let numCircles, spacingScaled, layerBaseOffset;
      const N = comp._staggerTotal || 1;
      const k = comp._staggerIndex || 0;

      if (rebar.type === 'count') {
        numCircles = Math.max(1, rebar.count || 1);
        let totalCircles = numCircles * N;
        let combinedSpacing = scaledB / totalCircles;
        let overallOffset = combinedSpacing / 2;
        
        spacingScaled = combinedSpacing * N;
        layerBaseOffset = overallOffset + k * combinedSpacing;
      } else {
        spacingScaled = (rebar.spacing || 150) * scale;
        if (spacingScaled <= 0) spacingScaled = 150 * scale;
        numCircles = Math.floor(scaledB / spacingScaled);
        
        let totalCircles = numCircles * N;
        let combinedSpacing = spacingScaled / N;
        let overallOffset = (scaledB - (totalCircles - 1) * combinedSpacing) / 2;
        
        spacingScaled = combinedSpacing * N; 
        layerBaseOffset = overallOffset + k * combinedSpacing;
      }
      
      const r = dScaled / 2;

      for(let i=0; i<numCircles; i++) {
        let baseCx = startX + layerBaseOffset + i * spacingScaled;
        let cx = baseCx;
        let cy = rCenterY;
        
        // Anti-collision logic
        let collision = true;
        let shiftAttempt = 0;
        
        while (collision && shiftAttempt < 15) {
          collision = false;
          for (let c of drawnCircles) {
            let dx = cx - c.cx;
            let dy = cy - c.cy;
            let dist = Math.sqrt(dx*dx + dy*dy);
            if (dist < (r + c.r) * 0.9) {
              collision = true;
              break;
            }
          }
          
          if (collision) {
            shiftAttempt++;
            let sign = (shiftAttempt % 2 === 0) ? -1 : 1;
            let shiftMag = Math.ceil(shiftAttempt / 2) * (r * 2.2); 
            cx = baseCx + (sign * shiftMag);
          }
        }
        
        drawnCircles.push({ cx, cy, r });
        svg += `<circle cx="${cx}" cy="${cy}" r="${r}" fill="${color}" opacity="${opacity}"/>`;
      }
    };

    computedLayers.forEach(comp => {
      const rebar = comp.layer[comp.main_dir];
      if (!rebar || rebar.diam <= 0) return;

      const color = comp.color || 'var(--color-primary)';
      const dScaled = rebar.diam * scale;
      const rCenterY = isTop 
        ? startY + (comp.bottom_edge_dist * scale) + dScaled / 2
        : startY + scaledH - (comp.bottom_edge_dist * scale) - dScaled / 2;

      if (comp.main_dir === 'x') {
        drawCircles(comp, rebar, rCenterY, dScaled, color, '1.0');
      } else {
        svg += `<line x1="${startX}" y1="${rCenterY}" x2="${startX + scaledB}" y2="${rCenterY}" stroke="${color}" stroke-width="${dScaled}" opacity="0.8"/>`;
      }
    });
  };

  drawRebars(computed.top, true);
  drawRebars(computed.bottom, false);

  svg += `</svg>`;
  return svg;
}

export function drawInteractionDiagram(dir, vars, width = 600, height = 400) {
  const m_bot = vars[`M_Rd_${dir}_bot`] ? vars[`M_Rd_${dir}_bot`].value : 0;
  const m_top = vars[`M_Rd_${dir}_top`] ? vars[`M_Rd_${dir}_top`].value : 0;
  const n_plus = vars[`N_Rd_plus_${dir}`] ? vars[`N_Rd_plus_${dir}`].value : 0;
  const n_minus = vars[`N_Rd_minus_${dir}`] ? vars[`N_Rd_minus_${dir}`].value : 0;
  
  const m_h2_bot = vars[`M_Rd_h2_${dir}_bot`] ? vars[`M_Rd_h2_${dir}_bot`].value : 0;
  const n_h2_bot = vars[`N_Rd_h2_${dir}_bot`] ? vars[`N_Rd_h2_${dir}_bot`].value : 0;
  const m_h2_top = vars[`M_Rd_h2_${dir}_top`] ? vars[`M_Rd_h2_${dir}_top`].value : 0;
  const n_h2_top = vars[`N_Rd_h2_${dir}_top`] ? vars[`N_Rd_h2_${dir}_top`].value : 0;

  const margin = 80;
  const drawWidth = width - 2 * margin;
  const drawHeight = height - 2 * margin;

  const maxM = Math.max(m_bot, m_top, m_h2_bot, m_h2_top, 10);
  
  const nMin = Math.min(n_minus, n_h2_bot, n_h2_top, 0);
  const nMax = Math.max(n_plus, n_h2_bot, n_h2_top, 10);
  const nSpan = Math.max(nMax - nMin, 10);
  const nPad = nSpan * 0.15;
  
  const yAxisMin = nMin - nPad;
  const yAxisMax = nMax + nPad;
  const yAxisSpan = yAxisMax - yAxisMin;

  const xAxisMin = -maxM * 1.25;
  const xAxisMax = maxM * 1.25;
  const xAxisSpan = xAxisMax - xAxisMin;

  // Scaling
  const scaleX = drawWidth / xAxisSpan;
  const scaleY = drawHeight / yAxisSpan;

  const getPtX = (m) => margin + (m - xAxisMin) * scaleX;
  const getPtY = (n) => margin + drawHeight - (n - yAxisMin) * scaleY;
  const getPt = (m, n) => `${getPtX(m)},${getPtY(n)}`;

  const cx = getPtX(0);
  const cy = getPtY(0);

  let svg = `<svg viewBox="0 0 ${width} ${height}" width="100%" xmlns="http://www.w3.org/2000/svg">`;

  // Draw axes
  svg += `<line x1="${margin}" y1="${cy}" x2="${width - margin}" y2="${cy}" stroke="var(--color-border)" stroke-width="1.5" />`;
  svg += `<line x1="${cx}" y1="${height - margin}" x2="${cx}" y2="${margin}" stroke="var(--color-border)" stroke-width="1.5" />`;

  // Axis labels
  svg += `<text x="${width - margin + 10}" y="${cy + 5}" fill="var(--color-text-muted)" font-size="12" font-family="sans-serif">M [kNm]</text>`;
  svg += `<text x="${cx - 20}" y="${margin - 10}" fill="var(--color-text-muted)" font-size="12" font-family="sans-serif" text-anchor="middle">N [kN]</text>`;

  // Draw polygon
  let polyPts = [];
  polyPts.push(getPt(0, n_plus));
  if (m_bot > 0) polyPts.push(getPt(m_bot, 0));
  if (vars[`M_Rd_h2_${dir}_bot`]) polyPts.push(getPt(m_h2_bot, n_h2_bot));
  if (Math.abs(n_minus) > 0) polyPts.push(getPt(0, n_minus));
  if (vars[`M_Rd_h2_${dir}_top`]) polyPts.push(getPt(-m_h2_top, n_h2_top));
  if (m_top > 0) polyPts.push(getPt(-m_top, 0));
  
  svg += `<polygon points="${polyPts.join(' ')}" fill="rgba(59, 130, 246, 0.1)" stroke="#3b82f6" stroke-width="2" />`;

  // Draw points
  const drawCircle = (m, n, labelM, labelN, labelPos = "auto") => {
    const ptX = getPtX(m);
    const ptY = getPtY(n);
    let circle = `<circle cx="${ptX}" cy="${ptY}" r="4" fill="#3b82f6" />`;
    
    // Position text depending on point
    let textAnchor = "middle";
    let dx = 0;
    let dy = 0;
    
    if (labelPos === "auto") {
      if (m > 0 && n === 0) { textAnchor = "start"; dx = 8; dy = 4; }
      else if (m < 0 && n === 0) { textAnchor = "end"; dx = -8; dy = 4; }
      else if (m === 0 && n > 0) { dy = -10; }
      else if (m === 0 && n < 0) { dy = 15; }
      else if (m > 0 && n < 0) { textAnchor = "start"; dx = 8; dy = 12; }
      else if (m < 0 && n < 0) { textAnchor = "end"; dx = -8; dy = 12; }
    }

    circle += `<text x="${ptX + dx}" y="${ptY + dy}" fill="var(--color-text)" font-size="12" font-family="sans-serif" text-anchor="${textAnchor}">${labelM !== null ? labelM.toFixed(1) : ''}${labelN !== null ? (labelM !== null ? ', ' : '') + labelN.toFixed(1) : ''}</text>`;
    return circle;
  };

  if (m_top > 0) svg += drawCircle(-m_top, 0, -m_top, 0);
  if (n_plus > 0) svg += drawCircle(0, n_plus, 0, n_plus);
  if (m_bot > 0) svg += drawCircle(m_bot, 0, m_bot, 0);
  if (Math.abs(n_minus) > 0) svg += drawCircle(0, n_minus, 0, n_minus);
  if (vars[`M_Rd_h2_${dir}_bot`]) svg += drawCircle(m_h2_bot, n_h2_bot, m_h2_bot, n_h2_bot);
  if (vars[`M_Rd_h2_${dir}_top`]) svg += drawCircle(-m_h2_top, n_h2_top, -m_h2_top, n_h2_top);

  svg += `</svg>`;
  return svg;
}
