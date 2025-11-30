import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input as mobilenet_preprocess
from tensorflow.keras.models import load_model
import numpy as np
import cv2
import os
import sys

# --- VERIFICARE CĂI ---
current_script_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_script_path)))
SRC_DIR = os.path.join(project_root, 'src')
TARGET_DIR = os.path.join(SRC_DIR, 'access_control')

if TARGET_DIR not in sys.path:
    # Adaugă directorul care conține modulul decision_logic.py
    sys.path.append(TARGET_DIR)

print(f"DEBUG: Directorul adăugat: {TARGET_DIR}")
print(f"DEBUG: sys.path conține directorul: {TARGET_DIR in sys.path}")
# --- SFÂRȘIT VERIFICARE ---

# Importăm direct fișierul, deoarece directorul său este acum în cale:
from decision_logic import get_policy_decision, log_access_event, load_monthly_counts, CLASS_MAP, LOGS_DIR

# ... (restul scriptului continuă)

# --- CĂI ȘI CONSTANTE ---
# Navigăm înapoi la rădăcina proiectului
project_root = os.path.dirname(SRC_DIR)

MODEL_PATH = os.path.join(project_root, 'config', 'vehicle_classifier_model.keras')
IMAGE_SIZE = (224, 224)
INPUT_SHAPE = IMAGE_SIZE + (3,)

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

        policy_result = get_policy_decision(predicted_index)
        log_access_event(policy_result)

        result = {
            "Vehicle_Type": policy_result['Vehicle_Type'],
            "Access_Decision": policy_result['Decision'],
            "Fee": policy_result['Fee_RON'],
            "Zone": policy_result['Zone'],
            "Notes": policy_result['Notes'],
            "Probability": f"{np.max(predictions) * 100:.2f}%"
        }
        return result

    except FileNotFoundError as e:
        return {"Error": str(e)}
    except Exception as e:
        return {"Error": f"Eroare la inferență: {e}"}


# --- Funcție de Testare și Afișare Statistici ---
def run_test_and_show_stats(sample_image_path):
    """ Simulează rularea aplicației și afișează logurile. """

    print("\n--- TESTARE ACCES VEHICUL ---")
    decision = predict_vehicle_access(sample_image_path)

    if 'Error' in decision:
        print(f"❌ EROARE: {decision['Error']}")
        return

    print(f"✅ DETECȚIE: {decision['Vehicle_Type']} ({decision['Probability']})")
    print(f"   Decizie: {decision['Access_Decision']}")
    print(f"   Taxă: {decision['Fee']} RON")
    print(f"   Zonă Alocată: {decision['Zone']}")

    print("\n--- STATISTICI CURENTE (Contorizare Lunară) ---")
    counts = load_monthly_counts()
    for vehicle, count in counts.items():
        print(f"   {vehicle:<15}: {count} vehicule")

    print(f"\nLogurile (CSV/JSON) sunt salvate în {LOGS_DIR}")


if __name__ == '__main__':
    # ⚠️ AICI SE CONFIGUREAZĂ IMAGINEA NOUĂ PENTRU TEST
    test_image_name = 'test_masina.jpg'
    sample_test_path = os.path.join(project_root, test_image_name)

    if not os.path.exists(sample_test_path):
        print(f"\nATENȚIE: Nu am găsit imaginea de test la calea: {sample_test_path}")
        print("Te rog să o adaugi în rădăcina proiectului și să o denumești 'test_masina.jpg'.")

    run_test_and_show_stats(sample_test_path)