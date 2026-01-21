// Elemente DOM
const fileInput = document.getElementById('file-input');
const preview = document.getElementById('image-preview');
const previewText = document.querySelector('.preview-area p');
const resultBox = document.getElementById('result-box');
const loading = document.getElementById('loading');
const badge = document.getElementById('status-badge');
const themeToggle = document.getElementById('theme-toggle');
const historyBody = document.getElementById('history-body');

const HISTORY_LIMIT = 10;

function hideResult() {
    resultBox.classList.add('hidden');
}

function showPreviewPlaceholder() {
    preview.src = '';
    preview.style.display = 'none';
    previewText.style.display = 'block';
}

// -------------------------
// Theme (Dark mode)
// -------------------------
function applyTheme(theme) {
    if (theme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        if (themeToggle) themeToggle.checked = true;
    } else {
        document.documentElement.removeAttribute('data-theme');
        if (themeToggle) themeToggle.checked = false;
    }
}

function toggleTheme() {
    const isDark = !!document.documentElement.getAttribute('data-theme');
    const next = isDark ? 'light' : 'dark';
    localStorage.setItem('theme', next);
    applyTheme(next);
}

function initTheme() {
    const saved = localStorage.getItem('theme');
    if (saved === 'dark' || saved === 'light') {
        applyTheme(saved);
        return;
    }
    // fallback: urmează preferința sistemului
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    applyTheme(prefersDark ? 'dark' : 'light');
}

// -------------------------
// Reset UI
// -------------------------
function resetUI() {
    const hasFile = !!fileInput.files && fileInput.files.length > 0;
    const hasPreview = preview.style.display !== 'none';
    const hasResult = !resultBox.classList.contains('hidden');

    if (hasFile || hasPreview || hasResult) {
        const ok = confirm('Sigur vrei să resetezi? Imaginea și rezultatul curent vor fi șterse.');
        if (!ok) return;
    }

    fileInput.value = '';
    showPreviewPlaceholder();
    hideResult();
    loading.classList.add('hidden');
}

// 1. Gestionare Upload Imagine
fileInput.addEventListener('change', function() {
    const file = this.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.style.display = 'block';
            previewText.style.display = 'none';
            // Ascundem rezultatul vechi
            hideResult();
        }
        reader.readAsDataURL(file);
    }
});

// 2. Trimitere la Server (API)
async function processImage() {
    if (!fileInput.files[0]) {
        alert("Te rog încarcă o imagine întâi!");
        return;
    }

    // UI Loading
    loading.classList.remove('hidden');
    hideResult();

    const reader = new FileReader();
    reader.readAsDataURL(fileInput.files[0]);

    reader.onload = async function() {
        const base64data = reader.result;

        try {
            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image: base64data })
            });

            const data = await response.json();

            if (data.error || data.Error) {
                alert("Eroare: " + (data.error || data.Error));
                return;
            }

            displayResult(data);
            loadStats();
            // pentru istoric: reîncărcăm din server (include și evenimentul nou dacă a fost logat)
            refreshHistory();
        } catch (error) {
            alert("Eroare server: " + error);
        } finally {
            loading.classList.add('hidden');
        }
    };
}

// 3. Afișare Rezultate
function displayResult(data) {
    // Cerință: când nu detectează (valid_detection=false), nu afișăm nimic.
    if (data.valid_detection === false) {
        hideResult();
        return;
    }

    // Flux Normal (valid_detection=true)
    resultBox.classList.remove('hidden');
    document.querySelector('.details').style.display = 'block';

    const decision = (data.Access_Decision || '').toUpperCase();
    const accepted = decision.includes("ACCEPTAT");

    if (accepted) {
        badge.textContent = "ACCES PERMIS";
        badge.className = "status-badge accept";
    } else {
        badge.textContent = "ACCES INTERZIS";
        badge.className = "status-badge reject";
    }

    // Fill common details
    document.getElementById('res-vehicle').textContent = data.Vehicle_Type ?? '-';
    document.getElementById('res-prob').textContent = data.Probability ?? '-';

    // Dacă e respins, nu afișăm taxă și nici info în plus.
    const feeRow = document.getElementById('res-fee').closest('.detail-row');
    const zoneRow = document.getElementById('res-zone').closest('.detail-row');

    if (!accepted) {
        feeRow.style.display = 'none';
        zoneRow.style.display = 'none';
        document.getElementById('res-fee').textContent = '-';
        document.getElementById('res-zone').textContent = '-';
        return;
    }

    feeRow.style.display = 'flex';
    zoneRow.style.display = 'flex';

    document.getElementById('res-fee').textContent = (data.Fee ?? '-') + (data.Fee !== undefined ? " RON" : "");

    const zone = (data.Zone ?? '').trim();
    const notes = (data.Notes ?? '').trim();
    document.getElementById('res-zone').textContent = (zone + " " + notes).trim() || '-';
}

// 4. Încărcare Statistici
async function loadStats() {
    const list = document.getElementById('stats-list');
    try {
        const res = await fetch('/api/stats');
        const data = await res.json();

        list.innerHTML = '';
        for (const [vehicle, count] of Object.entries(data)) {
            const li = document.createElement('li');
            li.innerHTML = `${vehicle}: <strong>${count}</strong>`;
            list.appendChild(li);
        }
    } catch (e) {
        console.error("Eroare stats:", e);
    }
}

// 5. Istoric
function escapeHtml(s) {
    return String(s)
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
}

function renderHistory(rows) {
    if (!historyBody) return;

    if (!rows || rows.length === 0) {
        historyBody.innerHTML = '<tr><td colspan="4" class="muted">Nu există evenimente încă.</td></tr>';
        return;
    }

    historyBody.innerHTML = rows.map(r => {
        const time = escapeHtml(r.time ?? '-');
        const vehicle = escapeHtml(r.vehicle ?? '-');
        const prob = escapeHtml(r.probability ?? '-');
        const decision = escapeHtml(r.decision ?? '-');
        return `<tr><td>${time}</td><td>${vehicle}</td><td>${prob}</td><td>${decision}</td></tr>`;
    }).join('');
}

async function refreshHistory() {
    try {
        const res = await fetch(`/api/history?limit=${HISTORY_LIMIT}`);
        const data = await res.json();

        if (data.error) {
            renderHistory([]);
            return;
        }

        renderHistory(data);
    } catch (e) {
        console.error('Eroare history:', e);
        renderHistory([]);
    }
}

// Init
initTheme();
loadStats();
refreshHistory();

