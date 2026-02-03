# 📘 README – P3: Proiect SAF - Diagram State Machines

**Disciplina:** Sisteme Avansate de Fabricare  
**Instituție:** POLITEHNICA București – FIIR  
**Student:** Savu Vladut George  
**Data:** 04.12.2025  
---

## Scopul Etapei P3

Această etapă corespunde punctului **3. Dezvoltare proiect software** - slide 10 **SAF - Specificatii proiect.pdf**.

##  Livrabile Obligatorii

### 1. Tabelul Nevoie Reală → Soluție CPS → Modul Software (max ½ pagină)

| **Nevoie reală concretă** |   **Cum o rezolvă SIA-ul vostru**  | **Modul software responsabil** |
|---------------------------|------------------------------------|--------------------------------|
|   Reducerea timpului de   |  Identificare automată a tipului   |    **AI Prediction Service**   |
|   așteptare la barieră    |     de vehicul în < 1 secundă      | (`predictor.py` + MobileNetV2) |
|   Aplicarea automată a    | Decizie instantanee de acces și    |   **Decision Logic Module**    | 
|  politicilor de taxare    |calcul taxă pe baza clasei detectate|    (`decision_logic.py`)       |
|  Auditarea traficului și  | Înregistrarea automată (Timestamp, |**Data Logging & Web Dashboard**|
|     statistici pentru     |   Tip, Decizie) și generarea de    |     (`app.py` + CSV Logs)      |
|  managementul campusului  |   statistici lunare în timp real   |                                |


---


### 2. Diagrama State Machine a Întregului Sistem (OBLIGATORIE)

**Cerințe:**
- **Minimum 4-6 stări clare** cu tranziții între ele
- **Formate acceptate:** PNG/SVG, pptx, draw.io 
- **Legendă obligatorie:** 1-2 paragrafe în acest README: "De ce ați ales acest State Machine pentru nevoia voastră?"


**Exemple concrete per domeniu de inginerie:**

#### Clasificare imagini defecte/producție
```
IDLE (Așteptare vehicul) 
   ↓ [Senzor prezență / Upload UI]
ACQUIRE_IMAGE (Captură foto & Decodare Base64)
   ↓
VALIDATE_IMAGE (Verificare format & rezoluție)
   ├─ [Invalid/Corupt] → LOG_ERROR → DISPLAY_ERROR → IDLE
   └─ [Valid] → PREPROCESS (Smart Crop, Resize 224x224, Normalizare RGB)
                  ↓
              RN_INFERENCE (MobileNetV2 Forward Pass)
                  ↓
              CHECK_CONFIDENCE (Prag > 75%)
                  ├─ [Low Confidence] → TRIGGER_MANUAL_CHECK (Alertă Pază) → LOG_WARNING → IDLE
                  └─ [High Confidence] → IDENTIFY_CLASS (Ex: "Autoturism")
                                           ↓
                                     APPLY_POLICY (Verificare Reguli & Calcul Taxă)
                                           ↓
                                     LOG_TRANSACTION (CSV + Update Contor Lunar)
                                           ↓
                                     UPDATE_UI & ACTUATE_BARRIER (Deschide/Închide)
                                           ↓
                                         IDLE
```
**Legendă obligatorie (scrieți în README):**
```markdown
### Justificarea State Machine-ului ales:

Am ales o arhitectură de tip "Event-Driven Classification Loop" pentru că proiectul meu vizează automatizarea accesului într-un campus universitar, unde latența deciziei și acuratețea sunt critice. Sistemul nu monitorizează continuu un semnal, ci reacționează instantaneu la prezența unui vehicul (upload imagine).

Stările principale sunt:
1. [ACQUIRE_IMAGE] & [PREPROCESS]: Modulul Web (app.py) primește imaginea brută și o trimite la predictor.py, unde aplicăm Smart Cropping (bazat pe coordonate YOLO simulate) și redimensionarea la 224x224 RGB
2. [RN_INFERENCE]: Rularea modelului antrenat pentru a obține vectorul de probabilități pentru cele 6 clase
3. [DECISION_LOGIC]: Această stare transformă ieșirea brută a AI-ului într-o decizie de business. Aici interogăm dicționarul de politici (decision_logic.py) pentru a stabili dacă vehiculul are drept de acces și ce taxă se aplică

Tranzițiile critice sunt:
- [RN_INFERENCE] → [CHECK_CONFIDENCE]: Aceasta este cea mai importantă măsură de siguranță. Dacă modelul nu este sigur (confidență < 75%), sistemul NU ia o decizie automată, ci trece într-o stare de MANUAL_CHECK, prevenind accesul neautorizat sau taxarea eronată.
- [APPLY_POLICY] → [ACTUATE_BARRIER]: Tranziția finală care leagă lumea digitală de cea fizică, condiționată de validarea regulilor de acces.

Starea [LOG_WARNING] / [MANUAL_CHECK] este esențială deoarece modelele de vedere artificială pot fi influențate de condiții meteo nefavorabile (ploaie, noapte). În loc să respingem automat un vehicul (ceea ce ar crea cozi), sistemul solicită intervenția umană doar în cazurile incerte, menținând fluiditatea traficului pentru restul de 90%+ cazuri clare.
```


---

## Checklist Final – Bifați Totul Înainte de Predare

### Documentație și Structură
- [x] Tabelul Nevoie → Soluție → Modul complet (minimum 2 rânduri cu exemple concrete completate in README_Etapa4_Arhitectura_SIA.md)
- [x] Diagrama State Machine creată și salvată și postată alături de acest readme pe moodle la P3. State Machine pentru proiectul SAF
- [x] Legendă State Machine scrisă în acest readme (minimum 1-2 paragrafe cu justificare) 