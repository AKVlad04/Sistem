# 📘 README – Etapa 4: Arhitectura Completă a Aplicației SIA bazată pe Rețele Neuronale

**Disciplina:** Rețele Neuronale  
**Instituție:** POLITEHNICA București – FIIR  
**Student:** Savu Vladut George
**Link Repository GitHub:** https://github.com/AKVlad04/Sistem-AI-de-Control-si-Taxare-Auto
**Data:** 11.12.2026
---

## Scopul Etapei 4

Această etapă corespunde punctului **5. Dezvoltarea arhitecturii aplicației software bazată pe RN** din lista de 9 etape - slide 2 **RN Specificatii proiect.pdf**.

### IMPORTANT - Ce înseamnă "schelet funcțional":

 **CE TREBUIE SĂ FUNCȚIONEZE:**
- [x] Toate modulele pornesc fără erori
- [x] Pipeline-ul complet rulează end-to-end (de la date → până la output UI)
- [x] Modelul RN este definit și compilat (arhitectura există)
- [x] Web Service/UI primește input și returnează output

---

##  Livrabile Obligatorii

### 1. Tabelul Nevoie Reală → Soluție SIA → Modul Software (max ½ pagină)

| **Nevoie reală concretă** | **Cum o rezolvă SIA-ul vostru** | **Modul software responsabil** |
|---------------------------|---------------------------------|--------------------------------|
|Fluidizarea traficului în  |Identificare automată a tipului  |   predictor.py + Web Service   |
|          campus           |   de vehicul în < 1 secundă     |                                |
| Aplicarea politicilor de  |  Decizie instantanee și calcul  |        decision_logic.py       |
|    taxare diferențiată    |  taxă pe baza clasei detectate  |                                |
|Eliminarea alarmelor false |    Filtrare pe bază de prag     |         predictor.py           |
|și a accesului neautorizat |       de confidență (75%)       |                                |
|---------------------------|---------------------------------|--------------------------------|

---

### 2. Contribuția Voastră Originală la Setul de Date – MINIM 40% din Totalul Observațiilor Finale

**Regula generală:** Din totalul de **N observații finale** în `data/processed/`, **minimum 40%** trebuie să fie **contribuția voastră originală**.

### Contribuția originală la setul de date:

**Total observații finale:** ~23,247 (după Smart Cropping din 9211 imagini originale)
**Observații originale:** ~14,000 (peste 60%)

**Tipul contribuției:**
[ ] Date generate prin simulare fizică  
[ ] Date achiziționate cu senzori proprii  
[X] Etichetare/adnotare manuală  
[X] Date sintetice prin metode avansate  

**Descriere detaliată:**
Contribuția originală depășește cerința de 40% prin două metode cheie:

Generarea extinsă (Smart Cropping): Din setul public de 9.211 imagini cu etichete YOLO, am rulat un script în data_preparator.py care decupează fiecare vehicul individual (Multi-Crop). Acest lucru a crescut numărul de observații clare și relevante de la 9.211 la ~23.000, transformând imaginile de detecție în imagini de clasificare. Această transformare profundă a datelor este considerată contribuție avansată.

Clasa Negativă ("Altele"): Am adăugat manual ~100 de imagini cu obiecte non-vehicul, clădiri și oameni pentru a crea clasa "Altele". Această clasă asigură că modelul poate distinge între o mașină (ACCES) și un obiect irelevant (AȘTEPTARE/RESPINS), rezolvând problema detecțiilor false.

**Locația codului:** `src/preprocessing/data_preparator.py`
**Locația datelor:** `data/processed/`

**Dovezi:**
- Tabelul din consola cnn_model.py (`docs/screenshots/`) arată că s-au antrenat 16337 imagini (train) din totalul de 23k.
```

---

### 3. Diagrama State Machine a Întregului Sistem (OBLIGATORIE)

**Cerințe:**
- **Minimum 4-6 stări clare** cu tranziții între ele
- **Formate acceptate:** PNG/SVG, pptx, draw.io 
- **Locație:** `docs/state_machine.*` (orice extensie)
- **Legendă obligatorie:** 1-2 paragrafe în acest README: "De ce ați ales acest State Machine pentru nevoia voastră?"

**Stări tipice pentru un SIA:**
```
IDLE → ACQUIRE_DATA → PREPROCESS → INFERENCE → DISPLAY/ACT → LOG → [ERROR] → STOP
                ↑______________________________________________|
```

**Notă pentru proiecte simple:**
Chiar dacă aplicația voastră este o clasificare simplă (user upload → classify → display), trebuie să modelați fluxul ca un State Machine. Acest exercițiu vă învață să gândiți modular și să anticipați toate stările posibile (inclusiv erori).

**Legendă obligatorie (scrieți în README):**
```markdown
### Justificarea State Machine-ului ales:

Am ales o arhitectură de tip Event-Driven Classification Loop pentru că proiectul vizează automatizarea accesului într-un campus universitar, unde latența deciziei și acuratețea sunt critice. Sistemul nu monitorizează continuu un semnal, ci reacționează instantaneu la prezența unui vehicul (upload imagine).

Stările principale sunt:
1.ACQUIRE_IMAGE & PREPROCESS: Modulul Web (app.py) primește imaginea brută și aplică Smart Cropping și redimensionarea la 224x224 RGB.
2.RN_INFERENCE: Rularea modelului antrenat (MobileNetV2) pentru a obține vectorul de probabilități.
3.CHECK_CONFIDENCE: Stare de filtrare critică. Dacă încrederea este sub 75%, sistemul nu se pronunță și trece în starea IDLE (AȘTEPTARE DETECTARE), pentru a nu oferi decizii nesigure.
4.DECISION_LOGIC: Aplică regulile de business (taxă, zonă) pe baza clasei detectate.

Tranzițiile critice sunt:
- [RN_INFERENCE] → [CHECK_CONFIDENCE]: Dacă confidența este sub 75%, sistemul trece direct înapoi la IDLE (simulând modul "Standby" al unui senzor).
- [APPLY_POLICY] → [ACTUATE_BARRIER]: Tranziția finală care leagă decizia software (ACCEPTAT/RESPINS) de interfața fizică (bariera/UI).

Starea IDLE (AȘTEPTARE), la care se revine direct din CHECK_CONFIDENCE (Low), este esențială pentru a gestiona erorile de fundal (persoane, sticle, copaci) fără a afișa o decizie incorectă sau o taxă falsă.
```

---

### 4. Scheletul Complet al celor 3 Module Cerute la Curs (slide 7)

Toate cele 3 module trebuie să **pornească și să ruleze fără erori** la predare. Nu trebuie să fie perfecte, dar trebuie să demonstreze că înțelegeți arhitectura.

| **Modul** | **Python (exemple tehnologii)**  | **Cerință minimă funcțională (la predare)** |
|-----------|----------------------------------|-------------|----------------------------------------------|
| **1. Data Logging / Acquisition** | `src/preprocessing/data_preparator.py` | **MUST:** Generat setul final de 23,247 imagini din datele raw + clasa "Altele". |
| **2. Neural Network Module** | `src/neural_network/cnn_model.py` | **MUST:** Modelul MobileNetV2 este definit și antrenat (Acuratețe > 91%). Poate fi încărcat de predictor.py|
| **3. Web Service / UI** | Flask (app.py) | **MUST:** Primește input (imagine) și returnează output (Decizie + Taxă), incluzând logica de Standby |

#### Detalii per modul:

#### **Modul 1: Data Logging / Acquisition**

**Funcționalități obligatorii:**
- [X] Cod rulează fără erori: `python src/preprocessing/data_preparator.py`
- [X] Generează CSV în format compatibil cu preprocesarea din Etapa 3
- [X] Include minimum 40% date originale în dataset-ul final
- [X] Documentație în cod: ce date generează, cu ce parametri

#### **Modul 2: Neural Network Module**

**Funcționalități obligatorii:**
- [X] Arhitectură RN definită și compilată fără erori
- [X] Model poate fi salvat și reîncărcat (din config/)
- [X] Include justificare pentru arhitectura aleasă (în docstring sau README)


#### **Modul 3: Web Service / UI**

**Funcționalități MINIME obligatorii:**
- [X] Propunere Interfață ce primește input de la user (formular, file upload, sau API endpoint)
- [X] Includeți un screenshot demonstrativ în `docs/screenshots/`

**Scop:** Prima demonstrație că pipeline-ul end-to-end funcționează: input user → preprocess → model → output.


## Structura Repository-ului la Finalul Etapei 4 (OBLIGATORIE)

**Verificare consistență cu Etapa 3:**

```
Sistem-AI-de-Control-si-Taxare-Auto/
├── data/
|   ├── logs/
│   ├── raw/
│   ├── processed/ # Date originale
│   ├── train/
│   ├── validation/
│   ├── test/
|   └── non_vehicle/
├── src/
│   ├── data_acquisition/
│   ├── preprocessing/-
│   ├── neural_network/
|   ├── access_control/
│   └── prediction_service/
├── docs/
|   ├── screenshots/
│   └── datasets/
├── static/
├── templates/
├── config/  # Trained model
├── README.md
├── README_Etapa3.md              # (deja existent)
├── README_Etapa4_Arhitectura_SIA.md              # ← acest fișier completat (în rădăcină)
└── requirements.txt
```

**Diferențe față de Etapa 3:**
- Adăugat `data/processed/` pentru contribuția dvs originală
- Adăugat `src/data_acquisition/` - MODUL 1
- Adăugat `src/neural_network/` - MODUL 2
- Adăugat `docs/screenshots/` pentru demonstrație UI

---

## Checklist Final – Bifați Totul Înainte de Predare

### Documentație și Structură
- [X] Tabelul Nevoie → Soluție → Modul complet (minimum 2 rânduri cu exemple concrete completate in README_Etapa4_Arhitectura_SIA.md)
- [X] Declarație contribuție 40% date originale completată în README_Etapa4_Arhitectura_SIA.md
- [X] Cod generare/achiziție date funcțional și documentat
- [X] Diagrama State Machine creată și salvată în `docs/state_machine.*`
- [X] Legendă State Machine scrisă în README_Etapa4_Arhitectura_SIA.md (minimum 1-2 paragrafe cu justificare)
- [X] Repository structurat conform modelului de mai sus (verificat consistență cu Etapa 3)

### Modul 1: Data Logging / Acquisition
- [X] Cod rulează fără erori
- [X] Produce minimum 40% date originale din dataset-ul final
- [X] CSV generat în format compatibil cu preprocesarea din Etapa 3
- [X] Documentație în `src/data_acquisition/README.md` cu:
  - [X] Metodă de generare/achiziție explicată
  - [X] Parametri folosiți (frecvență, durată, zgomot, etc.)
  - [X] Justificare relevanță date pentru problema voastră
- [X] Fișiere în `data/processed/` conform structurii

### Modul 2: Neural Network
- [X] Arhitectură RN definită și documentată în cod (docstring detaliat) - versiunea inițială 
- [X] README în `src/neural_network/` cu detalii arhitectură curentă

### Modul 3: Web Service / UI
- [X] Propunere Interfață ce pornește fără erori (comanda de lansare testată)
- [X] Screenshot demonstrativ în `docs/screenshots/ui_demo.png`
- [X] README în `src/app/` cu instrucțiuni lansare (comenzi exacte)

---

**Predarea se face prin commit pe GitHub cu mesajul:**  
`"Etapa 4 completă - Arhitectură SIA funcțională"`

**Tag obligatoriu:**  
`git tag -a v0.4-architecture -m "Etapa 4 - Skeleton complet SIA"`


