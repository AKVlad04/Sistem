import os
import sys
from flask import Flask, request, jsonify, render_template
import base64

# --- 1. CONFIGURARE CĂI (Abordare Directă) ---
current_dir = os.path.dirname(os.path.abspath(__file__))

# Definim căile către sub-module
ACCESS_CONTROL_DIR = os.path.join(current_dir, 'src', 'access_control')
PREDICTION_SERVICE_DIR = os.path.join(current_dir, 'src', 'prediction_service')

# Le adăugăm pe TOATE la sys.path pentru a putea importa direct fișierele
if ACCESS_CONTROL_DIR not in sys.path:
    sys.path.append(ACCESS_CONTROL_DIR)

if PREDICTION_SERVICE_DIR not in sys.path:
    sys.path.append(PREDICTION_SERVICE_DIR)

# Debugging: Afișăm ce am făcut
print(f"DEBUG: Am adăugat la PATH: {ACCESS_CONTROL_DIR}")
print(f"DEBUG: Am adăugat la PATH: {PREDICTION_SERVICE_DIR}")

# --- 2. IMPORTURI LOCALE (Acum sunt directe) ---
try:
    # Acum importăm direct numele fișierului (fără prefixul folderului)
    from decision_logic import load_monthly_counts
    from predictor import predict_vehicle_access

    print("DEBUG: Importurile locale au reușit!")
except ImportError as e:
    print(f"CRITIC: Eroare la importuri locale: {e}")
    # Script de diagnosticare: Vedem ce fișiere există real
    print(f"Verificare fișiere în {ACCESS_CONTROL_DIR}:")
    if os.path.exists(ACCESS_CONTROL_DIR):
        print(os.listdir(ACCESS_CONTROL_DIR))
    else:
        print("FOLDERUL NU EXISTĂ!")
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


if __name__ == '__main__':
    print("🚀 Aplicația pornește...")
    print("Deschide browserul la: http://127.0.0.1:5000")
    app.run(debug=True)