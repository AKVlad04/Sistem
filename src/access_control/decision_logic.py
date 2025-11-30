import os
import json
from datetime import datetime
from collections import Counter

# --- CĂI ȘI CONSTANTE (Logare Statistici) ---
# Navigăm înapoi la rădăcina proiectului pentru a găsi folderul data/logs
current_script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_script_dir)  # Mergem înapoi la src
project_root = os.path.dirname(project_root)  # Mergem înapoi la rădăcina proiectului

LOGS_DIR = os.path.join(project_root, 'data', 'logs')
VEHICLE_LOG_FILE = os.path.join(LOGS_DIR, 'monthly_access_log.csv')
VEHICLE_COUNT_FILE = os.path.join(LOGS_DIR, 'monthly_counts.json')

# --- MAPARE CLASE (Index -> Nume) ---
# Obținută din antrenarea CNN: {'Autobuz': 0, 'Autoturism': 1, 'Camion': 2, 'Microbuz': 3, 'Motocicleta': 4, 'Utilitara': 5}
CLASS_MAP = {
    0: 'Autobuz',
    1: 'Autoturism',
    2: 'Camion',
    3: 'Microbuz',
    4: 'Motocicleta',
    5: 'Utilitara'
}

# --- DEFINIȚIA POLITICILOR DE ACCES (Configurare Dinamică) ---
# Taxele și regulile sunt definite aici.
ACCESS_POLICIES = {
    'Autoturism': {'Access': True, 'Fee_RON': 5.00, 'Zone': 'P1/P2', 'Notes': 'Taxa standard'},
    'Motocicleta': {'Access': True, 'Fee_RON': 0.00, 'Zone': 'A1 (Gratuit)', 'Notes': 'Acces Gratuit'},
    'Microbuz': {'Access': True, 'Fee_RON': 0.00, 'Zone': 'C (Transport)', 'Notes': 'Transport intern'},
    'Utilitara': {'Access': True, 'Fee_RON': 10.00, 'Zone': 'Service', 'Notes': 'Taxa livrari (Permis)'},
    'Camion': {'Access': False, 'Fee_RON': 50.00, 'Zone': 'Service', 'Notes': 'Timp limitat! Necesita autorizare'},
    'Autobuz': {'Access': True, 'Fee_RON': 10.00, 'Zone': 'C (Traseu)', 'Notes': 'Taxa Traseu'}
}


# --- FUNCȚII DE LOGARE ȘI MANAGEMENT STATISTIC ---

def load_monthly_counts():
    """ Încarcă contorul lunar din JSON, sau îl inițializează. """
    if os.path.exists(VEHICLE_COUNT_FILE):
        with open(VEHICLE_COUNT_FILE, 'r') as f:
            return json.load(f)
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
        policy_result['Vehicle_Type'],
        policy_result['Decision'],
        f"{policy_result['Fee_RON']:.2f} RON",
        policy_result['Notes']
    ]

    with open(VEHICLE_LOG_FILE, 'a') as f:
        if not file_exists:
            f.write("Timestamp,Tip_Vehicul,Decizie,Taxa_Aplicata,Nota\n")
        f.write(",".join(map(str, log_data)) + "\n")

    # --- 2. Actualizare Contorizare Lunară (Doar pentru vehicule cu acces) ---
    if policy_result['Access']:
        counts = load_monthly_counts()
        vehicle_type = policy_result['Vehicle_Type']

        if vehicle_type in counts:
            counts[vehicle_type] += 1

        save_monthly_counts(counts)

    return policy_result['Decision']


# --- FUNCȚIE PRINCIPALĂ DE DECIZIE ---

def get_policy_decision(predicted_class_index):
    """
    Returnează decizia complexă (Access, Fee, Notes) pe baza clasei detectate.
    """
    class_name = CLASS_MAP.get(predicted_class_index, "NECUNOSCUT")
    policy = ACCESS_POLICIES.get(class_name,
                                 {'Access': False, 'Fee_RON': 99.00, 'Zone': 'N/A',
                                  'Notes': 'Clasa necunoscuta / Neautorizata'})

    # Adaugăm numele clasei și decizia pentru logare
    policy['Vehicle_Type'] = class_name
    policy['Decision'] = "ACCEPTAT" if policy['Access'] else "RESPINS"

    return policy


# Funcția de testare a logicii (poți să o rulezi separat)
def test_full_policy_logic():
    print("--- Testare Logica de Acces Campus ---")
    simulated_detections = [1, 4, 2, 1, 3]  # Autoturism, Motocicleta, Camion, Autoturism, Microbuz

    for index in simulated_detections:
        policy_result = get_policy_decision(index)
        final_decision = log_access_event(policy_result)

        status = "✅ ACCEPTAT" if final_decision == "ACCEPTAT" else "❌ RESPINS"

        print(f"[{policy_result['Vehicle_Type']:<12}] -> {status:<15} | Taxa: {policy_result['Fee_RON']} RON")

    print("\n--- Contor Lunar Actualizat ---")
    print(json.dumps(load_monthly_counts(), indent=4))


if __name__ == '__main__':
    test_full_policy_logic()