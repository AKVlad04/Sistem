// Elemente DOM
const fileInput = document.getElementById('file-input');
const preview = document.getElementById('image-preview');
const previewText = document.querySelector('.preview-area p');
const resultBox = document.getElementById('result-box');
const loading = document.getElementById('loading');
const badge = document.getElementById('status-badge');

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
            resultBox.classList.add('hidden');
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
    resultBox.classList.add('hidden');

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

            if (data.error) {
                alert("Eroare: " + data.error);
            } else {
                displayResult(data);
                loadStats(); // Actualizăm statistica
            }
        } catch (error) {
            alert("Eroare server: " + error);
        } finally {
            loading.classList.add('hidden');
        }
    };
}

// --- LOGICA NOUĂ: MODUL STANDBY ---
function setStandbyMode() {
    // Afișăm cutia, dar în modul neutru
    document.querySelector('.details').style.display = 'none';

    badge.textContent = "📡 AȘTEPTARE DETECTARE...";
    badge.className = "status-badge"; // Resetăm culorile
    badge.style.backgroundColor = "#95a5a6"; // Gri
    badge.style.animation = "pulse 2s infinite"; // Efect de pulsare (dacă ai adăugat CSS-ul)
}

// 3. Afișare Rezultate
function displayResult(data) {
    resultBox.classList.remove('hidden');

    // NOU: Dacă detectarea nu este validă (sub 75%), intrăm în Standby
    if (data.valid_detection === false) {
        setStandbyMode();
        return; // Oprim execuția pe fluxul roșu/verde
    }

    // Flux Normal (Peste 75%)
    document.querySelector('.details').style.display = 'block';
    badge.style.animation = "none"; // Oprim pulsarea

    // Badge Logic
    if (data.Access_Decision.includes("ACCEPTAT")) {
        badge.textContent = "✅ ACCES PERMIS";
        badge.className = "status-badge accept";
    } else {
        badge.textContent = "⛔ ACCES INTERZIS";
        badge.className = "status-badge reject";
    }

    // Fill details
    document.getElementById('res-vehicle').textContent = data.Vehicle_Type;
    document.getElementById('res-prob').textContent = data.Probability;
    document.getElementById('res-fee').textContent = data.Fee + " RON";
    document.getElementById('res-zone').textContent = data.Zone + " " + (data.Notes || "");
}

// 4. Încărcare Statistici (rămâne neschimbată)
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

// Load stats on start
loadStats();