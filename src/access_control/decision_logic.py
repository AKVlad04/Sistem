import os
import json
from datetime import datetime

# --- CĂI ȘI CONSTANTE (Logare Statistici) ---
# Navigăm înapoi la rădăcina proiectului pentru a găsi folderul data/logs
current_script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_script_dir))  # src -> root

LOGS_DIR = os.path.join(project_root, 'data', 'logs')
VEHICLE_LOG_FILE = os.path.join(LOGS_DIR, 'monthly_access_log.csv')
VEHICLE_COUNT_FILE = os.path.join(LOGS_DIR, 'monthly_counts.json')

# --- MAPARE CLASE (Index -> Nume) ---
# ⚠️ ACTUALIZAT pentru modelul nou cu 7 clase (Altele = 0)
CLASS_MAP = {
    0: 'Altele',
    1: 'Autobuz',
    2: 'Autoturism',
    3: 'Camion',
    4: 'Microbuz',
    5: 'Motocicleta',
    6: 'Utilitara'
}

# --- DEFINIȚIA POLITICILOR DE ACCES ---
ACCESS_POLICIES = {
    'Autoturism': {'Access': True, 'Fee_RON': 5.00, 'Zone': 'P1/P2', 'Notes': 'Taxa standard'},
    'Motocicleta': {'Access': True, 'Fee_RON': 0.00, 'Zone': 'A1 (Gratuit)', 'Notes': 'Acces Gratuit'},
    'Microbuz': {'Access': True, 'Fee_RON': 0.00, 'Zone': 'C (Transport)', 'Notes': 'Transport intern'},
    'Utilitara': {'Access': True, 'Fee_RON': 10.00, 'Zone': 'Service', 'Notes': 'Taxa livrari (Permis)'},
    'Camion': {'Access': False, 'Fee_RON': 50.00, 'Zone': 'Service', 'Notes': 'Timp limitat! Necesita autorizare'},
    'Autobuz': {'Access': True, 'Fee_RON': 10.00, 'Zone': 'C (Traseu)', 'Notes': 'Taxa Traseu'},
    # Politica pentru clasa nouă
    'Altele': {'Access': False, 'Fee_RON': 0.00, 'Zone': '-', 'Notes': 'Nu este un vehicul valid'}
}


# --- FUNCȚII DE LOGARE ȘI MANAGEMENT STATISTIC ---

def load_monthly_counts():
    """ Încarcă contorul lunar din JSON, sau îl inițializează. """
    if os.path.exists(VEHICLE_COUNT_FILE):
        try:
            with open(VEHICLE_COUNT_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass  # Dacă fișierul e corupt, îl recreăm
    return {cls: 0 for cls in CLASS_MAP.values()}


def save_monthly_counts(counts):
    """ Salvează contorul lunar actualizat în JSON. """
    os.makedirs(LOGS_DIR, exist_ok=True)
    with open(VEHICLE_COUNT_FILE, 'w') as f:
        json.dump(counts, f, indent=4)


def log_access_event(policy_result):
    """
    Înregistrează evenimentul în fișierul CSV și actualizează contorul lunar.
    """
    # --- 1. Logare CSV ---
    os.makedirs(LOGS_DIR, exist_ok=True)
    file_exists = os.path.exists(VEHICLE_LOG_FILE)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_data = [
        timestamp,
        policy_result.get('Vehicle_Type', 'Unknown'),
        policy_result.get('Decision', 'N/A'),
        f"{policy_result.get('Fee_RON', 0):.2f} RON",
        policy_result.get('Notes', '')
    ]

    try:
        with open(VEHICLE_LOG_FILE, 'a') as f:
            if not file_exists:
                f.write("Timestamp,Tip_Vehicul,Decizie,Taxa_Aplicata,Nota\n")
            f.write(",".join(map(str, log_data)) + "\n")
    except Exception as e:
        print(f"Eroare la scrierea log-ului CSV: {e}")

    # --- 2. Actualizare Contorizare Lunară (Doar pentru vehicule cu acces) ---
    if policy_result.get('Access'):
        counts = load_monthly_counts()
        vehicle_type = policy_result['Vehicle_Type']

        if vehicle_type in counts:
            counts[vehicle_type] += 1
        elif vehicle_type not in counts:
            counts[vehicle_type] = 1  # Adaugă cheia dacă lipsește

        save_monthly_counts(counts)

    return policy_result.get('Decision')


# --- FUNCȚIE PRINCIPALĂ DE DECIZIE ---

def get_policy_decision(predicted_class_index):
    """
    Returnează decizia complexă (Access, Fee, Notes) pe baza clasei detectate.
    """
    class_name = CLASS_MAP.get(predicted_class_index, "NECUNOSCUT")
    policy = ACCESS_POLICIES.get(class_name,
                                 {'Access': False, 'Fee_RON': 99.00, 'Zone': 'N/A', 'Notes': 'Clasa necunoscuta'})

    # Adaugăm numele clasei și decizia pentru logare
    policy['Vehicle_Type'] = class_name
    policy['Decision'] = "ACCEPTAT" if policy['Access'] else "RESPINS"

    return policy


# Funcția de testare a logicii
if __name__ == '__main__':
    print("--- Testare Logica de Acces Campus (7 Clase) ---")
    # Testăm indexul 0 (Altele) și 2 (Autoturism)
    test_indices = [0, 2]

    for index in test_indices:
        policy_result = get_policy_decision(index)
        log_access_event(policy_result)
        print(f"Index {index}: {policy_result['Vehicle_Type']} -> {policy_result['Decision']}")