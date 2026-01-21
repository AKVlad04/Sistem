Modul 1: Data Acquisition & Generation
1. Metodă de Generare și Achiziție
Procesul de constituire a setului de date pentru acest proiect a urmat o abordare hibridă pentru a atinge pragul de 40% contribuție originală:

Extracție prin Smart Cropping (Original/Sintetic): Am utilizat un set de date brut (YOLO format) care conținea imagini de ansamblu. Contribuția originală a constat în dezvoltarea și rularea scriptului data_preparator.py, care a extras automat vehiculele individuale folosind coordonatele din fișierele de adnotare. Această metodă a generat un dataset nou, optimizat pentru clasificare CNN, mărind volumul de date de la 9k la peste 23k imagini.

Achiziție Manuală (Clasa Negativă): Pentru a rezolva problema detecțiilor false, am colectat manual imagini cu obiecte non-vehicul (pietoni, obstacole, fundal gol). Acestea au fost integrate în clasa "Altele", o componentă critică ce nu exista în sursa inițială.

2. Parametri Folosiți
Rezoluție de ieșire: Toate imaginile generate/achiziționate au fost redimensionate la 224x224 pixeli (RGB) pentru compatibilitate cu MobileNetV2.

Prag de suprafață (MIN_AREA_THRESHOLD): 0.01. Am filtrat orice vehicul care ocupa mai puțin de 1% din imaginea originală pentru a evita datele neclare.

Raport de Split: 70% Train, 15% Validation, 15% Test.

Diversitate: Achiziția manuală a inclus condiții variate de iluminare pentru a simula mediul real al unei bariere de campus.

3. Justificarea Relevanței Datelor
Datele sunt direct relevante pentru problema Controlului de Acces în Campus din următoarele motive:

Focalizare pe Subiect: Prin Smart Cropping, modelul învață caracteristicile vehiculului, nu contextul drumului, reducând timpul de procesare la < 1 secundă.

Siguranță (Clasa Altele): Includerea datelor originale de tip "non-vehicul" permite sistemului să rămână în Standby când în fața barierei nu se află o mașină, prevenind acționările accidentale.

Echilibru: Dataset-ul final acoperă toate categoriile din politicile de taxare (Autoturism, Camion, Moto etc.), permițând aplicarea corectă a logicii de business.