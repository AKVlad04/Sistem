# 📘 README – Etapa 3: Analiza și Pregătirea Setului de Date pentru Rețele Neuronale

**Disciplina:** Rețele Neuronale  
**Instituție:** POLITEHNICA București – FIIR  
**Student:** Savu Vladut George  
**Data:** 20.11.2025  

---

## Introducere

Acest document descrie activitățile realizate în **Etapa 3**, în care se analizează și se preprocesează setul de date necesar proiectului „Rețele Neuronale". Scopul etapei este pregătirea corectă a datelor pentru instruirea modelului RN, respectând bunele practici privind calitatea, consistența și reproductibilitatea datelor.

---

##  1. Structura Repository-ului Github (versiunea Etapei 3)

```
project-name/
├── README.md
├── docs/
│   └── datasets/          # descriere seturi de date, surse, diagrame
├── data/
│   ├── raw/               # date brute
│   ├── processed/         # date curățate și transformate
│   ├── train/             # set de instruire
│   ├── validation/        # set de validare
│   └── test/              # set de testare
├── src/
│   ├── preprocessing/     # funcții pentru preprocesare
│   ├── data_acquisition/  # generare / achiziție date (dacă există)
│   └── neural_network/    # implementarea RN (în etapa următoare)
├── config/                # fișiere de configurare
└── requirements.txt       # dependențe Python (dacă aplicabil)
```

---

##  2. Descrierea Setului de Date

### 2.1 Sursa datelor

* Origine: Set de date public de imagini, destinat antrenării unui model de Clasificare a vehiculelor.
* Modul de achiziție: Fișier extern
* Perioada / condițiile colectării: Nu este specificat, dar setul de date trebuie să fie divers (varietate de unghiuri, iluminare zi/noapte, condiții meteo) pentru a asigura robustetea modelului CNN.

### 2.2 Caracteristicile dataset-ului

* **Număr total de observații:** 9211
* **Număr de caracteristici (features):** 640x640
* **Tipuri de date: Imagini si Numerice**
* **Format fișiere:** JPG, TXT

### 2.3 Descrierea fiecărei caracteristici

|-------------------|---------|-------------|--------------------------|--------------------|
| **Caracteristică**| **Tip** | **Unitate** |       **Descriere**      | **Domeniu valori** |
|-------------------|---------|-------------|--------------------------|--------------------|
|	            |         | 	    |                          |		    |
|  Imagine Vehicul  |  Input  |   Pixeli    |Sursa principală de date, |      640x640       |
|	            |         | 	    |cu rezoluție uniformă.    |		    |
|-------------------|---------|-------------|--------------------------|--------------------|
|	            |         | 	    |                          |		    |
|   Etichetă YOLO   |  Label  |  Normalizat |Index clasă, x_center,    |       [0-4]        |
|                   |         |             |y_center, lățime, înălțime|                    |
|-------------------|---------|-------------|--------------------------|--------------------|


**Fișier recomandat: `data/README.md`**

---

##  3. Analiza Exploratorie a Datelor (EDA) – Sintetic

### 3.1 Statistici descriptive aplicate

* **Rezoluția imaginii:** Uniformă (640 x 640 pixels)
* **Distribuția pe Clase:** Analiza frecvenței Indexurilor de Clasă (0, 1, 2, 3, 4) în întregul set.
* Histograme

### 3.2 Analiza calității datelor

* **Detectarea etichetelor inconsistente sau eronate**
* **Identificarea imaginilor neclare sau obstruate**

### 3.3 Probleme identificate

*

---

##  4. Preprocesarea Datelor

### 4.1 Curățarea datelor

* **Eliminare duplicatelor**
* **Tratarea imaginilor corupte/outlier:** Eliminarea imaginilor neclare sau cu etichete YOLO eronate.

### 4.2 Transformarea caracteristicilor

* **Extracția Etichetei **
* **Redimensionare: ** Imaginile de 640 x 640 vor fi redimensionate la o dimensiune standardizată pentru CNN.
* **Normalizare (Min–Max): ** Scalarea valorilor pixelilor de la 0-255 la 0-1.

### 4.3 Structurarea seturilor de date

**Împărțire**
* 70% – train
* 15% – validation
* 15% – test

**Principii respectate:**
* **Stratificare pentru clasificare: ** Împărțirea se face pe baza Clasei Dominante obținute, menținând proporțiile.
* **Fără scurgere de informație: ** Parametrii de normalizare se calculează DOAR pe setul de train.

### 4.4 Salvarea rezultatelor preprocesării

* Date preprocesate în `data/processed/`
* Seturi train/val/test în foldere dedicate, organizate după Clasa Dominantă (ex: `data/train/Autoturism/`)

---

##  5. Fișiere Generate în Această Etapă

* `data/raw/` – date brute
* `data/processed/` – imaginile și etichetele finale
* `data/train/`, `data/validation/`, `data/test/` – seturi finale
* `src/preprocessing/` – codul Python care implementează logica de simplificare YOLO -> Clasificare
* `data/README.md` – descrierea dataset-ului
* `requirements.txt` - dependente Python

---

##  6. Stare Etapă (de completat de student)

- [ ] Structură repository configurată
- [ ] Dataset analizat (EDA realizată)
- [ ] Date preprocesate
- [ ] Seturi train/val/test generate
- [ ] Documentație actualizată în README + `data/README.md`

---
