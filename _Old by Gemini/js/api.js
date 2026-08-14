/**
 * js/api.js – Thin client for the Python FastAPI backend.
 *
 * All computation has moved to Python. This module provides simple async
 * wrappers around the REST API endpoints so the rest of the JS code
 * has a clean, consistent interface.
 */

const BASE = '';  // Same origin — FastAPI serves both static files and API

// ---------------------------------------------------------------------------
// Project
// ---------------------------------------------------------------------------

export async function fetchProject() {
  const res = await fetch(`${BASE}/api/project`);
  if (!res.ok) throw new Error(`GET /api/project → ${res.status}`);
  return res.json();
}

export async function saveProject(projectState) {
  const res = await fetch(`${BASE}/api/project`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(projectState),
  });
  if (!res.ok) throw new Error(`POST /api/project → ${res.status}`);
  return res.json();
}

// ---------------------------------------------------------------------------
// Materials
// ---------------------------------------------------------------------------

export async function fetchMaterialTemplates() {
  const res = await fetch(`${BASE}/api/materials/templates`);
  if (!res.ok) throw new Error(`GET /api/materials/templates → ${res.status}`);
  return res.json();  // { concrete: {...}, steel: {...} }
}

/**
 * Calculates all CivilVar values for a material.
 * @param {Object} material – The material data object from project state
 * @returns {Promise<{equations: Array, extras: Array, all_property_keys: Array}>}
 */
export async function calculateMaterial(material) {
  const res = await fetch(`${BASE}/api/materials/calculate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ material }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(`POST /api/materials/calculate → ${res.status}: ${err.detail || ''}`);
  }
  return res.json();
}

/**
 * Gets the default properties for a new material grade.
 * @param {string} type  – 'concrete' or 'steel'
 * @param {string} grade – e.g. 'C30/37' or 'B500B'
 * @returns {Promise<Object>} properties dict
 */
export async function fetchDefaultProperties(type, grade) {
  const res = await fetch(`${BASE}/api/materials/default-properties`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ type, grade }),
  });
  if (!res.ok) throw new Error(`POST /api/materials/default-properties → ${res.status}`);
  return res.json();
}

// ---------------------------------------------------------------------------
// Plates
// ---------------------------------------------------------------------------

/**
 * Runs the full plate cross-section calculation.
 * @param {Object} plate     – Plate data object
 * @param {Array}  materials – All project materials
 * @returns {Promise<{vars: Object, sections: Array}>}
 *   sections contain pre-rendered latex strings ready for KaTeX
 */
export async function calculatePlate(plate, materials) {
  const res = await fetch(`${BASE}/api/plates/calculate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ plate, materials }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(`POST /api/plates/calculate → ${res.status}: ${err.detail || ''}`);
  }
  return res.json();
}

/**
 * Creates a new default plate object.
 * @param {string} name      – Display name
 * @param {Array}  materials – Current project materials (to pick default concrete)
 * @returns {Promise<Object>} new plate dict
 */
export async function createNewPlate(name, materials = []) {
  const res = await fetch(`${BASE}/api/plates/new`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, materials }),
  });
  if (!res.ok) throw new Error(`POST /api/plates/new → ${res.status}`);
  return res.json();
}

/**
 * Creates a new default reinforcement layer object.
 * @param {string} mainDir – 'x' or 'y'
 * @returns {Promise<Object>} new layer dict
 */
export async function createNewLayer(mainDir = 'x') {
  const res = await fetch(`${BASE}/api/plates/new-layer?main_dir=${mainDir}`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error(`POST /api/plates/new-layer → ${res.status}`);
  return res.json();
}
