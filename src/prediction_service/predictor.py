import tensorflow as tf

# Încercăm importul specific pentru procesare imagini
try:
    from tensorflow.keras.applications.mobilenet_v2 import preprocess_input as mobilenet_preprocess
    from tensorflow.keras.models import load_model
except ImportError:
    # Fallback pentru versiuni vechi/noi de tensorflow
    from keras.applications.mobilenet_v2 import preprocess_input as mobilenet_preprocess
    from keras.models import load_model

import numpy as np
import cv2
import os
import sys

# --- 1. CONFIGURARE CĂI (Robustă) ---
# Determinăm calea curentă a acestui script (src/prediction_service/predictor.py)
current_script_path = os.path.dirname(os.path.abspath(__file__))

# Urcăm 2 nivele pentru a ajunge la rădăcina proiectului
project_root = os.path.dirname(os.path.dirname(current_script_path))

# Definim calea către access_control
ACCESS_CONTROL_DIR = os.path.join(project_root, 'src', 'access_control')

# Adăugăm folderul în sistem pentru ca Python să găsească decision_logic.py
if ACCESS_CONTROL_DIR not in sys.path:
    sys.path.append(ACCESS_CONTROL_DIR)
    print(f"DEBUG: Am adăugat în PATH: {ACCESS_CONTROL_DIR}")

# --- 2. IMPORTURI DIN ALTE MODULE ---
try:
    from decision_logic import get_policy_decision, log_access_event, CLASS_MAP

    print("✅ Import decision_logic reușit!")
except ImportError as e:
    print(f"❌ CRITIC: Nu pot importa decision_logic! Verifică dacă fișierul există în {ACCESS_CONTROL_DIR}")
    print(f"Eroare detaliată: {e}")
    # Nu oprim scriptul, dar predicția va crăpa mai târziu dacă nu rezolvăm

# --- 3. CONFIGURARE MODEL ---
MODEL_PATH = os.path.join(project_root, 'models', 'optimized_model.keras')
CONFIDENCE_THRESHOLD = 0.80
IMAGE_SIZE = (224, 224)

GLOBAL_MODEL = None

# Încercăm încărcarea modelului la start
print(f"🔄 Încerc încărcarea modelului din: {MODEL_PATH}")
if os.path.exists(MODEL_PATH):
    try:
        # TRUCUL MAGIC: compile=False ignoră erorile de optimizator vechi/nou
        GLOBAL_MODEL = load_model(MODEL_PATH, compile=False)
        print(f"🚀 SUCCESS: Modelul AI a fost încărcat corect!")
    except Exception as e:
        print(f"❌ EROARE LA LOAD_MODEL: {e}")
        print("Sfat: Verifică compatibilitatea TensorFlow sau re-antrenează modelul.")
else:
    print(f"❌ EROARE: Fișierul nu există la calea specificată.")
    # Încercăm fallback la vehicle_classifier_model.keras
    fallback_path = os.path.join(project_root, 'models', 'vehicle_classifier_model.keras')
    if os.path.exists(fallback_path):
        print(f"⚠️ Încerc modelul de rezervă: {fallback_path}")
        try:
            GLOBAL_MODEL = load_model(fallback_path, compile=False)
            print("🚀 Model de rezervă încărcat!")
        except:
            pass


def preprocess_input_image(image_path):
    """Pregătește imaginea pentru MobileNetV2"""
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Nu pot citi imaginea: {image_path}")

    # Resize la 224x224
    resized_img = cv2.resize(img, IMAGE_SIZE, interpolation=cv2.INTER_AREA)

    # Convertire BGR (OpenCV) la RGB (TensorFlow)
    rgb_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB)

    # Adăugare dimensiune batch (1, 224, 224, 3)
    input_array = np.expand_dims(rgb_img, axis=0)

    # Preprocesare specifică MobileNetV2 (-1 la 1 scaling)
    return mobilenet_preprocess(input_array)


def predict_vehicle_access(image_path):
    """Funcția principală apelată din app.py"""

    # Verificare critică
    if GLOBAL_MODEL is None:
        return {"Error": "Modelul AI nu este încărcat. Verifică consola serverului pentru erori."}

    try:
        # 1. Preprocesare
        input_data = preprocess_input_image(image_path)

        # 2. Predicție
        predictions = GLOBAL_MODEL.predict(input_data, verbose=0)
        predicted_index = np.argmax(predictions[0])
        max_probability = np.max(predictions)

        probability_str = f"{max_probability * 100:.2f}%"
        vehicle_name = CLASS_MAP.get(predicted_index, "Necunoscut")

        print(f"🔍 Detectat: {vehicle_name} ({probability_str})")

        # 3. Verificare Prag (Threshold)
        if max_probability < CONFIDENCE_THRESHOLD:
            return {
                "valid_detection": False,
                "Vehicle_Type": vehicle_name,
                "Probability": probability_str,
                "Message": "Grad de încredere scăzut. Poziționați vehiculul mai bine."
            }

        # 4. Decizie Business (Taxare/Acces)
        policy_result = get_policy_decision(predicted_index)
        policy_result['Probability'] = probability_str

        # 5. Logare
        log_access_event(policy_result)

        # 6. Returnare rezultat către UI
        return {
            "valid_detection": True,
            "Vehicle_Type": policy_result['Vehicle_Type'],
            "Access_Decision": policy_result['Decision'],
            "Fee": policy_result['Fee_RON'],
            "Zone": policy_result['Zone'],
            "Notes": policy_result['Notes'],
            "Probability": probability_str
        }

    except Exception as e:
        print(f"Eroare în timpul predicției: {e}")
        return {"Error": str(e)}