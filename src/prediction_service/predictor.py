import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input as mobilenet_preprocess
from tensorflow.keras.models import load_model
import numpy as np
import cv2
import os
import sys

# --- VERIFICARE CĂI ---
current_script_path = os.path.abspath(__file__)
# Navigăm de la src/prediction_service -> src -> root
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_script_path)))
SRC_DIR = os.path.join(project_root, 'src')
TARGET_DIR = os.path.join(SRC_DIR, 'access_control')

if TARGET_DIR not in sys.path:
    # Adaugă directorul care conține modulul decision_logic.py
    sys.path.append(TARGET_DIR)

# --- CONSTANTE CRITICE ---
CONFIDENCE_THRESHOLD = 0.70  # Pragul de încredere (75%)
MODEL_PATH = os.path.join(project_root, 'config', 'vehicle_classifier_model.keras')
IMAGE_SIZE = (224, 224)
INPUT_SHAPE = IMAGE_SIZE + (3,)

# Importăm direct fișierul, deoarece directorul său este acum în cale:
from decision_logic import get_policy_decision, log_access_event, load_monthly_counts, CLASS_MAP, LOGS_DIR

# --- Încarcă Modelul O Singură Dată la Pornire ---
try:
    GLOBAL_MODEL = load_model(MODEL_PATH)
    print(f"Modelul încărcat cu succes din {MODEL_PATH}")
except Exception as e:
    print(f"Eroare la încărcarea modelului: {e}")
    GLOBAL_MODEL = None


def preprocess_input_image(image_path):
    """
    Încarcă o imagine, o redimensionează și o pregătește (normalizează) pentru MobileNetV2.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Eroare: Nu s-a putut încărca imaginea de la {image_path}")

    resized_img = cv2.resize(img, IMAGE_SIZE, interpolation=cv2.INTER_AREA)
    rgb_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB)
    input_array = np.expand_dims(rgb_img, axis=0)
    preprocessed_array = mobilenet_preprocess(input_array)

    return preprocessed_array


def predict_vehicle_access(image_path):
    """
    Rulează inferența pe model, aplică logica de acces și loghează evenimentul.
    """
    if GLOBAL_MODEL is None:
        return {"Error": "Modelul AI nu este încărcat."}

    try:
        input_data = preprocess_input_image(image_path)
        predictions = GLOBAL_MODEL.predict(input_data, verbose=0)

        predicted_index = np.argmax(predictions[0])
        max_probability = np.max(predictions)

        # --- LOGICA DE FILTRARE PE BAZA PRAGULUI ---
        if max_probability < CONFIDENCE_THRESHOLD:
            # Dacă încrederea e prea mică, returnăm semnal de Standby/Așteptare
            return {
                "valid_detection": False,
                "Vehicle_Type": CLASS_MAP.get(predicted_index, "N/A"),
                "Probability": f"{max_probability * 100:.2f}%"
            }

        # ---------------------------------------------
        # Dacă s-a trecut de prag (max_probability >= 75%)
        policy_result = get_policy_decision(predicted_index)
        log_access_event(policy_result)

        result = {
            "valid_detection": True,  # Semnal că avem decizie finală
            "Vehicle_Type": policy_result['Vehicle_Type'],
            "Access_Decision": policy_result['Decision'],
            "Fee": policy_result['Fee_RON'],
            "Zone": policy_result['Zone'],
            "Notes": policy_result['Notes'],
            "Probability": f"{max_probability * 100:.2f}%"
        }
        return result

    except FileNotFoundError as e:
        return {"Error": str(e)}
    except Exception as e:
        return {"Error": f"Eroare la inferență: {e}"}

# --- Funcție de Testare și Afișare Statistici (rămâne neschimbată) ---
# ... (restul fișierului rămâne același)