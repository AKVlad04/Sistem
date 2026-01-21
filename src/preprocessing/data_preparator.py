import os
import shutil
import random
import cv2
import numpy as np

# --- 1. CONFIGURARE ---
IMAGE_SIZE = (224, 224)
SPLIT_RATIOS = {'train': 0.70, 'validation': 0.15, 'test': 0.15}
MIN_AREA_THRESHOLD = 0.01  # Ignorăm vehiculele minuscula (sub 1% din poză)

# --- CĂI ---
current_script_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_script_path)))

RAW_DATA_PATH = os.path.join(project_root, 'data', 'raw')
NON_VEHICLE_PATH = os.path.join(project_root, 'data', 'non_vehicle')
PROCESSED_DATA_PATH = os.path.join(project_root, 'data', 'processed')

OUTPUT_DIRS = {
    'train': os.path.join(PROCESSED_DATA_PATH, 'train'),
    'validation': os.path.join(PROCESSED_DATA_PATH, 'validation'),
    'test': os.path.join(PROCESSED_DATA_PATH, 'test')
}

# --- DEFINIM CELE 7 CLASE ---
CLASS_MAPPING = {
    0: 'Autobuz',
    1: 'Autoturism',
    2: 'Microbuz',
    3: 'Motocicleta',
    4: 'Utilitara',
    5: 'Camion',
    6: 'Altele'  # Clasa nouă pentru a elimina erorile
}


def create_directory_structure():
    if os.path.exists(PROCESSED_DATA_PATH):
        print(f"Șterg directorul vechi: {PROCESSED_DATA_PATH}")
        shutil.rmtree(PROCESSED_DATA_PATH)

    os.makedirs(PROCESSED_DATA_PATH, exist_ok=True)
    for base_dir in OUTPUT_DIRS.values():
        for class_name in CLASS_MAPPING.values():
            os.makedirs(os.path.join(base_dir, class_name), exist_ok=True)
    print("Structura de directoare creată.")


def get_all_crops_coordinates(txt_path, img_width, img_height):
    """ Extrage coordonatele tuturor vehiculelor valide din imagine. """
    valid_crops = []
    try:
        with open(txt_path, 'r') as f:
            lines = f.readlines()
        for line in lines:
            parts = line.strip().split()
            if len(parts) != 5: continue

            class_id = int(parts[0])
            x_center, y_center, w, h = map(float, parts[1:])

            if (w * h) < MIN_AREA_THRESHOLD: continue

            x_center_px, y_center_px = x_center * img_width, y_center * img_height
            w_px, h_px = w * img_width, h * img_height

            x_min = max(0, int(x_center_px - w_px / 2))
            y_min = max(0, int(y_center_px - h_px / 2))
            x_max = min(img_width, int(x_center_px + w_px / 2))
            y_max = min(img_height, int(y_center_px + h_px / 2))

            if x_max > x_min and y_max > y_min:
                valid_crops.append((class_id, x_min, y_min, x_max, y_max))
        return valid_crops
    except:
        return []


def process_vehicles():
    print("--- Pasul 1: Procesare Vehicule (Smart Cropping) ---")
    all_files = os.listdir(RAW_DATA_PATH)
    image_files = sorted([f for f in all_files if f.endswith('.jpg')])

    random.seed(42)
    random.shuffle(image_files)

    total = len(image_files)
    train_end = int(total * SPLIT_RATIOS['train'])
    val_end = train_end + int(total * SPLIT_RATIOS['validation'])

    sets = {
        'train': image_files[:train_end],
        'validation': image_files[train_end:val_end],
        'test': image_files[val_end:]
    }

    count = 0
    for split_type, files in sets.items():
        for fname in files:
            img_path = os.path.join(RAW_DATA_PATH, fname)
            txt_path = os.path.join(RAW_DATA_PATH, os.path.splitext(fname)[0] + '.txt')

            if not os.path.exists(txt_path): continue

            img = cv2.imread(img_path)
            if img is None: continue

            h, w, _ = img.shape
            crops = get_all_crops_coordinates(txt_path, w, h)

            for i, (cid, x1, y1, x2, y2) in enumerate(crops):
                if cid not in CLASS_MAPPING: continue  # Ignoră clase necunoscute

                dest_dir = os.path.join(OUTPUT_DIRS[split_type], CLASS_MAPPING[cid])
                crop_img = img[y1:y2, x1:x2]

                # Resize direct la color (fără grayscale)
                final_img = cv2.resize(crop_img, IMAGE_SIZE, interpolation=cv2.INTER_AREA)

                out_name = f"{os.path.splitext(fname)[0]}_crop_{i}.jpg"
                cv2.imwrite(os.path.join(dest_dir, out_name), final_img)
                count += 1
    print(f"✅ Vehicule procesate: {count} imagini decupate.")


def process_non_vehicles():
    print("\n--- Pasul 2: Procesare Non-Vehicule (Clasa 'Altele') ---")
    if not os.path.exists(NON_VEHICLE_PATH):
        print("⚠️ ATENȚIE: Nu există folderul data/non_vehicle. Sari peste acest pas.")
        return

    files = [f for f in os.listdir(NON_VEHICLE_PATH) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]

    if not files:
        print("⚠️ Folderul non_vehicle este gol!")
        return

    random.seed(42)
    random.shuffle(files)

    total = len(files)
    train_end = int(total * SPLIT_RATIOS['train'])
    val_end = train_end + int(total * SPLIT_RATIOS['validation'])

    sets = {
        'train': files[:train_end],
        'validation': files[train_end:val_end],
        'test': files[val_end:]
    }

    count = 0
    for split_type, file_list in sets.items():
        dest_dir = os.path.join(OUTPUT_DIRS[split_type], 'Altele')
        for fname in file_list:
            img = cv2.imread(os.path.join(NON_VEHICLE_PATH, fname))
            if img is None: continue

            # Luăm toată poza, o redimensionăm
            final_img = cv2.resize(img, IMAGE_SIZE, interpolation=cv2.INTER_AREA)
            cv2.imwrite(os.path.join(dest_dir, fname), final_img)
            count += 1
    print(f"✅ Imagini 'Altele' procesate: {count}")


if __name__ == '__main__':
    create_directory_structure()
    process_vehicles()
    process_non_vehicles()
    print("\n🎉 Preprocesare completă! Acum rulează cnn_model.py")