import os
import sys
from flask import Flask, request, jsonify, render_template
import base64
import csv

# --- 1. CONFIGURARE CĂI (Importuri Directe Robuste) ---
current_dir = os.path.dirname(os.path.abspath(__file__))

# Definim căile către sub-module
ACCESS_CONTROL_DIR = os.path.join(current_dir, 'src', 'access_control')
PREDICTION_SERVICE_DIR = os.path.join(current_dir, 'src', 'prediction_service')

# Adăugăm directoarele la sys.path pentru a putea importa modulele direct
if ACCESS_CONTROL_DIR not in sys.path:
    sys.path.append(ACCESS_CONTROL_DIR)

if PREDICTION_SERVICE_DIR not in sys.path:
    sys.path.append(PREDICTION_SERVICE_DIR)

# --- 2. IMPORTURI LOCALE ---
try:
    from decision_logic import load_monthly_counts, VEHICLE_LOG_FILE
    from predictor import predict_vehicle_access

    print("DEBUG: Importurile locale au reușit!")
except ImportError as e:
    print(f"CRITIC: Eroare la importuri locale: {e}")
    sys.exit(1)

# --- 3. CONFIGURARE FLASK ---
app = Flask(__name__)


@app.route('/')
def index():
    """ Încarcă interfața principală. """
    return render_template('index.html')


@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        if 'image' not in data:
            return jsonify({'error': 'Lipseste imaginea'}), 400

        image_data = data['image'].split(',')[1]
        image_bytes = base64.b64decode(image_data)

        temp_filename = 'temp_upload.jpg'
        temp_path = os.path.join(current_dir, temp_filename)

        with open(temp_path, 'wb') as f:
            f.write(image_bytes)

        result = predict_vehicle_access(temp_path)

        if os.path.exists(temp_path):
            os.remove(temp_path)

        return jsonify(result)

    except Exception as e:
        print(f"Eroare la predicție: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def stats():
    try:
        counts = load_monthly_counts()
        return jsonify(counts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/history', methods=['GET'])
def history():
    """Returnează ultimele N evenimente din log-ul CSV."""
    try:
        limit = request.args.get('limit', default=10, type=int)
        limit = max(1, min(limit, 50))

        if not os.path.exists(VEHICLE_LOG_FILE):
            return jsonify([])

        # Citim toate liniile non-goale
        with open(VEHICLE_LOG_FILE, 'r', newline='', encoding='utf-8') as f:
            raw_lines = [ln.strip('\n').strip('\r') for ln in f.readlines() if ln.strip()]

        if not raw_lines:
            return jsonify([])

        rows = []

        first = raw_lines[0].strip()
        has_header = first.lower().startswith('timestamp,')

        if has_header:
            header_cols = [c.strip() for c in first.split(',')]
            has_prob_col = any(c.lower() == 'probability' for c in header_cols)

            if has_prob_col:
                # Header complet -> DictReader
                with open(VEHICLE_LOG_FILE, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for r in reader:
                        ts = (r.get('Timestamp') or '').strip()
                        time_part = ts.split(' ')[1] if ' ' in ts else ts

                        prob = (r.get('Probability') or '').strip() or '-'

                        rows.append({
                            'time': time_part,
                            'vehicle': (r.get('Tip_Vehicul') or '').strip(),
                            'probability': prob,
                            'decision': (r.get('Decizie') or '').strip()
                        })
            else:
                # Header vechi (fără Probability) -> csv.reader pe poziții
                with open(VEHICLE_LOG_FILE, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    _ = next(reader, None)  # skip header
                    for parts in reader:
                        if not parts or len(parts) < 3:
                            continue
                        ts = (parts[0] or '').strip()
                        time_part = ts.split(' ')[1] if ' ' in ts else ts

                        vehicle = (parts[1] or '').strip() if len(parts) > 1 else ''
                        decision = (parts[2] or '').strip() if len(parts) > 2 else ''

                        # Dacă rândul are 6 coloane (note poate fi gol), probability e ultimul câmp
                        probability = '-'
                        if len(parts) >= 6:
                            probability = (parts[-1] or '').strip() or '-'

                        rows.append({
                            'time': time_part,
                            'vehicle': vehicle,
                            'probability': probability,
                            'decision': decision
                        })
        else:
            # Fără header deloc: parse manual
            for line in raw_lines:
                parts = [p.strip() for p in line.split(',')]
                if len(parts) < 3:
                    continue

                ts = parts[0]
                time_part = ts.split(' ')[1] if ' ' in ts else ts

                vehicle = parts[1] if len(parts) > 1 else ''
                decision = parts[2] if len(parts) > 2 else ''

                probability = '-'
                if len(parts) >= 6:
                    probability = (parts[-1] or '').strip() or '-'

                rows.append({
                    'time': time_part,
                    'vehicle': vehicle,
                    'probability': probability,
                    'decision': decision
                })

        return jsonify(rows[-limit:][::-1])

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("Aplicația pornește...")
    print("Deschide browserul la: http://127.0.0.1:5000")
    app.run(debug=True)