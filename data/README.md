## 3. Dataset și Contribuție Originală

### 3.1 Sursa și Caracteristicile Datelor

| Caracteristică | Valoare |
|----------------|---------|
| **Origine date** | Mixt: Dataset Public + Date Proprii (Captură/Augmentare/Smart Cropping) |
| **Sursa concretă** | Kaggle |
| **Număr total observații finale (N)** | 23.247 imagini |
| **Număr features** | 7 clase (output) / 224x224 px RGB (input) |
| **Tipuri de date** | Imagini RGB |
| **Format fișiere** | .jpg, .png, .jpeg |
| **Perioada colectării/generării** | Decembrie 2025 – Ianuarie 2026 |

### 3.2 Contribuția Originală (minim 40% OBLIGATORIU)

| Câmp | Valoare |
|------|---------|
| **Total observații finale (N)** | 23.247 imagini |
| **Observații originale (M)** | 14.036 imagini (create prin procesare proprie) |
| **Procent contribuție originală** | 60,37% |
| **Tip contribuție** | Smart Cropping (extracție obiecte), Re-etichetare manuală și Augmentare |
| **Locație cod generare** | `src/preprocessing/data_preparator.py` |
| **Locație date originale** | `data/processed/` |

**Descriere metodă generare/achiziție:**

Contribuția originală a constat în transformarea unui dataset brut de 9.211 imagini cu etichete multiple într-un set de date optimizat de 23.247 de eșantioane individuale prin procesul de Smart Cropping. Fiecare imagine complexă a fost descompusă în decupaje individuale pentru fiecare vehicul detectat, rezultând în medie 2,5 observații noi per imagine sursă. Suplimentar, am aplicat transformări de luminozitate și contrast pentru a simula variații de mediu critice pentru un sistem de control acces (noapte, ceață, supraexpunere), crescând robustețea modelului în condiții industriale reale.

### 3.3 Preprocesare și Split Date

| Set | Procent | Număr Observații |
|-----|---------|------------------|
| Train | 70% | 16.273 |
| Validation | 15% | 3.487 |
| Test | 15% | 3.487 |

**Preprocesări aplicate:**
- Resizing: Standardizare la 224x224 px pentru compatibilitate cu arhitectura MobileNetV2.
- Smart Cropping: Extragerea zonelor de interes (Bounding Boxes) din imaginile sursă pentru a elimina zgomotul vizual din fundal.
- Normalizare: Scalarea valorilor pixelilor în intervalul [-1, 1] utilizând funcția preprocess_input specifică MobileNetV2.
- Augmentare (Set Train): Aplicarea variațiilor de luminozitate (brightness range), contrast și rotații ușoare pentru a preveni overfitting-ul pe baza de date limitată.
