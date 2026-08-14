/**
 * utils.js – Global utility functions (shared across all modules).
 * 
 * RESPONSIBILITY:
 * Provides cross-module helper functions: clipboard interactions (text & images),
 * toast notifications, modal dialogs (confirm, prompt, diagram viewer),
 * debounce, and UUID generation.
 */

// =============================================================================
// Clipboard Utilities
// =============================================================================

/**
 * Copies plain text to the system clipboard.
 *
 * @param {string} text - The text to copy
 * @returns {Promise<boolean>} true if copying succeeded, false otherwise
 */
export async function copyTextToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text);
    showToast('LaTeX-Code in Zwischenablage kopiert!');
    return true;
  } catch (err) {
    console.error('[utils] Failed to copy text to clipboard:', err);
    showToast('Kopieren fehlgeschlagen.', 'danger');
    return false;
  }
}

/**
 * Copies an SVG element to the clipboard as a high-DPI PNG image.
 * Falls back to downloading the PNG file if clipboard write is not supported.
 *
 * @param {SVGElement} svgElement - The SVG element to convert and copy
 * @param {string} [filename='diagram.png'] - Fallback download filename
 */
export async function copySvgAsPng(svgElement, filename = 'diagram.png') {
  if (!svgElement) {
    showToast('Kein SVG-Element zum Kopieren gefunden.', 'danger');
    return;
  }

  try {
    const svgString = new XMLSerializer().serializeToString(svgElement);
    const svgBlob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' });
    const URL = window.URL || window.webkitURL || window;
    const blobURL = URL.createObjectURL(svgBlob);
    
    const image = new Image();
    image.onload = () => {
      try {
        // Use bounding rect for dimensions, with sensible fallbacks
        const bbox = svgElement.getBoundingClientRect();
        const width = bbox.width || 400;
        const height = bbox.height || 250;
        
        const canvas = document.createElement('canvas');
        const scale = 2; // 2× DPI for sharp rendering in Word/PDF
        canvas.width = width * scale;
        canvas.height = height * scale;
        
        const context = canvas.getContext('2d');
        // Fill with the app's dark background to match the theme
        context.fillStyle = '#0d1324';
        context.fillRect(0, 0, canvas.width, canvas.height);
        
        context.scale(scale, scale);
        context.drawImage(image, 0, 0, width, height);
        
        canvas.toBlob(async (blob) => {
          if (!blob) {
            showToast('PNG-Erstellung fehlgeschlagen.', 'danger');
            return;
          }
          try {
            await navigator.clipboard.write([
              new ClipboardItem({ 'image/png': blob })
            ]);
            showToast('Diagramm als Bild kopiert! (Bereit zum Einfügen in Word)');
            URL.revokeObjectURL(blobURL);
          } catch (clipErr) {
            // Fallback: trigger a file download instead
            console.warn('[utils] Clipboard write failed, downloading instead:', clipErr);
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            showToast('Direktes Kopieren fehlgeschlagen. Bild heruntergeladen.', 'warning');
          }
        }, 'image/png');
      } catch (drawErr) {
        console.error('[utils] Error drawing SVG to canvas:', drawErr);
        showToast('Kopieren fehlgeschlagen.', 'danger');
      }
    };
    image.onerror = (e) => {
      console.error('[utils] Image load error:', e);
      showToast('Kopieren fehlgeschlagen.', 'danger');
    };
    image.src = blobURL;
  } catch (err) {
    console.error('[utils] Error in copySvgAsPng:', err);
    showToast('Kopieren fehlgeschlagen.', 'danger');
  }
}

// =============================================================================
// Toast Notifications
// =============================================================================

/** @type {number|null} Active timeout ID for the current toast, used to prevent overlap */
let toastTimeoutId = null;

/**
 * Displays a brief toast notification at the bottom of the screen.
 * Automatically hides after 3 seconds. Consecutive calls reset the timer.
 *
 * @param {string} message - The message to display
 * @param {'info'|'danger'|'warning'} [type='info'] - Visual style variant
 */
export function showToast(message, type = 'info') {
  // Create the toast element lazily on first use
  let toast = document.getElementById('app-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'app-toast';
    toast.className = 'toast';
    document.body.appendChild(toast);
  }
  
  toast.textContent = message;
  toast.className = 'toast show';
  
  // Apply a border color matching the notification type
  const borderColors = {
    danger: 'var(--color-danger)',
    warning: '#f59e0b',
    info: 'var(--color-primary)',
  };
  toast.style.borderColor = borderColors[type] || borderColors.info;
  
  // Clear any existing timer and set a new auto-hide timeout
  if (toastTimeoutId) {
    clearTimeout(toastTimeoutId);
  }
  toastTimeoutId = setTimeout(() => {
    toast.className = 'toast';
    toastTimeoutId = null;
  }, 3000);
}

// =============================================================================
// Debounce Helper
// =============================================================================

/**
 * Creates a debounced version of a function that delays invocation until
 * `wait` milliseconds have passed since the last call.
 *
 * @param {Function} func - The function to debounce
 * @param {number}   wait - Delay in milliseconds
 * @returns {Function} The debounced wrapper function
 */
export function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// =============================================================================
// ID Generation
// =============================================================================

/**
 * Generates a short, pseudo-random unique identifier.
 * Not cryptographically secure – suitable for UI element IDs.
 *
 * @returns {string} A string like "id_a1b2c3d4e"
 */
export function generateUUID() {
  return 'id_' + Math.random().toString(36).substr(2, 9);
}

// =============================================================================
// Confirmation Modal
// =============================================================================

/**
 * Shows a custom confirmation dialog (replacing the native `confirm()`).
 * The modal animates in/out and calls `onConfirm` only if the user clicks
 * the confirm button.
 *
 * @param {string}   title     - Dialog title
 * @param {string}   text      - Descriptive body text (supports HTML)
 * @param {Function} onConfirm - Callback invoked when the user confirms
 */
export function showConfirmModal(title, text, onConfirm) {
  const backdrop = document.createElement('div');
  backdrop.className = 'modal-backdrop';
  backdrop.innerHTML = `
    <div class="modal-container">
      <div class="modal-header">
        <h3>${title}</h3>
        <button class="btn-item-action close-modal-btn" style="color:var(--color-text-muted); font-size:1.2rem;">&times;</button>
      </div>
      <div class="modal-body">
        <p style="color: var(--color-text-muted); line-height: 1.5;">${text}</p>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary cancel-modal-btn">Abbrechen</button>
        <button class="btn btn-danger confirm-modal-btn">Löschen</button>
      </div>
    </div>
  `;
  document.body.appendChild(backdrop);
  
  // Animate in (delay needed for CSS transition to trigger)
  setTimeout(() => backdrop.classList.add('active'), 50);

  const confirmBtn = backdrop.querySelector('.confirm-modal-btn');
  setTimeout(() => confirmBtn?.focus(), 100);

  let isClosing = false;
  /** Closes the modal with immediate DOM cleanup */
  const close = () => {
    if (isClosing) return;
    isClosing = true;
    document.removeEventListener('keydown', handleKeydown);
    backdrop.classList.remove('active');
    if (backdrop.parentNode) {
      backdrop.parentNode.removeChild(backdrop);
    }
  };

  const handleKeydown = (e) => {
    if (isClosing) return;
    if (e.key === 'Enter') {
      e.preventDefault();
      e.stopPropagation();
      if (onConfirm) {
        try { onConfirm(); } catch (err) { console.error(err); }
      }
      close();
    } else if (e.key === 'Escape') {
      e.preventDefault();
      close();
    }
  };
  document.addEventListener('keydown', handleKeydown);

  backdrop.querySelector('.close-modal-btn').addEventListener('click', close);
  backdrop.querySelector('.cancel-modal-btn').addEventListener('click', close);
  backdrop.addEventListener('click', (e) => {
    if (e.target === backdrop) close();
  });
  confirmBtn.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (isClosing) return;
    if (onConfirm) {
      try {
        onConfirm();
      } catch (err) {
        console.error(err);
      }
    }
    close();
  });
}

// =============================================================================
// Prompt Modal
// =============================================================================

/**
 * Shows a custom prompt dialog (replacing the native `prompt()`).
 * The input field is auto-focused and pre-selected. Pressing Enter submits.
 *
 * @param {string}   title        - Dialog title
 * @param {string}   label        - Label text for the input field
 * @param {string}   defaultValue - Initial value in the input field
 * @param {Function} onConfirm    - Callback(value) invoked with the entered text
 */
export function showPromptModal(title, label, defaultValue, onConfirm) {
  const backdrop = document.createElement('div');
  backdrop.className = 'modal-backdrop';
  backdrop.innerHTML = `
    <div class="modal-container">
      <div class="modal-header">
        <h3>${title}</h3>
        <button class="btn-item-action close-modal-btn" style="color:var(--color-text-muted); font-size:1.2rem;">&times;</button>
      </div>
      <div class="modal-body">
        <div class="form-field">
          <label for="prompt-input">${label}</label>
          <input type="text" class="input-control" id="prompt-input" value="${defaultValue}">
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary cancel-modal-btn">Abbrechen</button>
        <button class="btn btn-primary confirm-modal-btn">Speichern</button>
      </div>
    </div>
  `;
  document.body.appendChild(backdrop);
  
  // Animate in
  setTimeout(() => backdrop.classList.add('active'), 50);

  /** Closes the modal with a fade-out animation */
  const close = () => {
    backdrop.classList.remove('active');
    setTimeout(() => backdrop.remove(), 250);
  };

  // Auto-focus and select the input content for quick editing
  const input = backdrop.querySelector('#prompt-input');
  setTimeout(() => {
    input.focus();
    input.select();
  }, 100);

  backdrop.querySelector('.close-modal-btn').addEventListener('click', close);
  backdrop.querySelector('.cancel-modal-btn').addEventListener('click', close);
  backdrop.addEventListener('click', (e) => {
    if (e.target === backdrop) close();
  });
  
  /** Validates and submits the input value */
  const submit = () => {
    const val = input.value.trim();
    if (val) {
      close();
      if (onConfirm) {
        try {
          onConfirm(val);
        } catch (err) {
          console.error('[showPromptModal] Error in onConfirm callback:', err);
        }
      }
    } else {
      // Visual feedback for empty input
      input.style.borderColor = 'var(--color-danger)';
    }
  };

  backdrop.querySelector('.confirm-modal-btn').addEventListener('click', submit);
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') submit();
  });
}

// =============================================================================
// Diagram Viewer Modal
// =============================================================================

/**
 * Shows a full-screen modal for viewing an SVG diagram with pan & zoom.
 * Uses the svg-pan-zoom library if available.
 *
 * @param {string} title   - Modal title
 * @param {string} svgHtml - The SVG markup to display (as an HTML string)
 */
export function showDiagramModal(title, svgHtml) {
  const backdrop = document.createElement('div');
  backdrop.className = 'modal-backdrop';
  backdrop.innerHTML = `
    <div class="modal-container" style="width: 90vw; height: 90vh; max-width: 1200px; display: flex; flex-direction: column;">
      <div class="modal-header">
        <h3>${title}</h3>
        <button class="btn-item-action close-modal-btn" style="color:var(--color-text-muted); font-size:1.2rem;">&times;</button>
      </div>
      <div class="modal-body" style="flex-grow: 1; padding: 0; overflow: hidden; position: relative;">
        <div id="modal-diagram-container" style="width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; background-color: var(--color-bg-panel);">
          ${svgHtml}
        </div>
      </div>
    </div>
  `;
  document.body.appendChild(backdrop);
  
  // Animate in
  setTimeout(() => backdrop.classList.add('active'), 50);

  /** Closes the modal with a fade-out animation */
  const close = () => {
    backdrop.classList.remove('active');
    setTimeout(() => backdrop.remove(), 250);
  };

  backdrop.querySelector('.close-modal-btn').addEventListener('click', close);
  
  // Initialize pan-zoom on the modal's SVG after it's rendered
  setTimeout(() => {
    if (window.svgPanZoom) {
      const svgEl = backdrop.querySelector('svg');
      if (svgEl) {
        svgEl.style.width = '100%';
        svgEl.style.height = '100%';
        window.svgPanZoom(svgEl, {
          zoomEnabled: true,
          controlIconsEnabled: false,
          zoomScaleSensitivity: 0.5,
          fit: true,
          center: true,
          minZoom: 0.5,
          maxZoom: 10
        });
      }
    }
  }, 100);
}
