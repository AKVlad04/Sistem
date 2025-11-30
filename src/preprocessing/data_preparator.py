import os
import shutil
import random
import cv2
import numpy as np

# --- 1. Parametri de Configurare ---
IMAGE_SIZE = (224, 224)
SPLIT_RATIOS = {'train': 0.70, 'validation': 0.15, 'test': 0.15}

# Filtru: Ignorăm vehiculele care ocupă mai puțin de 1% din imagine (sunt prea mici/departe)
MIN_AREA_THRESHOLD = 0.01

# --- Căi Absolute ---
current_script_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_script_path)))

RAW_DATA_PATH = os.path.join(project_root, 'data', 'raw')
PROCESSED_DATA_PATH = os.path.join(project_root, 'data', 'processed')

OUTPUT_DIRS = {
    'train': os.path.join(PROCESSED_DATA_PATH, 'train'),
    'validation': os.path.join(PROCESSED_DATA_PATH, 'validation'),
    'test': os.path.join(PROCESSED_DATA_PATH, 'test')
}

CLASS_MAPPING = {
    0: 'Autobuz',
    1: 'Autoturism',
    2: 'Microbuz',
    3: 'Motocicleta',
    4: 'Utilitara',
    5: 'Camion'
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
    """
    Returnează o LISTĂ de obiecte din imagine: [(class_id, xmin, ymin, xmax, ymax), ...]
    """
    valid_crops = []

    try:
        with open(txt_path, 'r') as f:
            lines = f.readlines()

        for line in lines:
            parts = line.strip().split()
            if len(parts) != 5: continue

            class_id = int(parts[0])
            x_center = float(parts[1])
            y_center = float(parts[2])
            w = float(parts[3])
            h = float(parts[4])

            # Ignorăm obiectele prea mici (zgomot de fundal)
            if (w * h) < MIN_AREA_THRESHOLD:
                continue

            # Conversie YOLO -> Pixeli
            x_center_px = x_center * img_width
            y_center_px = y_center * img_height
            w_px = w * img_width
            h_px = h * img_height

            x_min = int(x_center_px - (w_px / 2))
            y_min = int(y_center_px - (h_px / 2))
            x_max = int(x_center_px + (w_px / 2))
            y_max = int(y_center_px + (h_px / 2))

            # Clamp (să nu ieșim din imagine)
            x_min = max(0, x_min)
            y_min = max(0, y_min)
            x_max = min(img_width, x_max)
            y_max = min(img_height, y_max)

            if x_max > x_min and y_max > y_min:
                valid_crops.append((class_id, x_min, y_min, x_max, y_max))

        return valid_crops

    except Exception as e:
        return []


def main_processing():
    all_files = os.listdir(RAW_DATA_PATH)
    image_files = sorted([f for f in all_files if f.endswith('.jpg')])

    total_crops = 0
    images_processed = 0

    print(f"Începe procesarea MULTI-CROP pentru {len(image_files)} imagini sursă...")

    # Pentru a menține stratificarea corectă, trebuie să fim atenți.
    # Deoarece o imagine poate genera mai multe clase, o vom aloca unui set (train/val/test)
    # și TOATE crop-urile din ea vor merge în acel set. Asta previne "data leakage".

    random.seed(42)
    random.shuffle(image_files)

    total_files = len(image_files)
    train_end = int(total_files * SPLIT_RATIOS['train'])
    val_end = train_end + int(total_files * SPLIT_RATIOS['validation'])

    # Împărțim fișierele SURSĂ în seturi
    sets = {
        'train': image_files[:train_end],
        'validation': image_files[train_end:val_end],
        'test': image_files[val_end:]
    }

    for split_type, files in sets.items():
        print(f"Procesez setul: {split_type} ({len(files)} imagini)...")

        for fname in files:
            img_path = os.path.join(RAW_DATA_PATH, fname)
            txt_path = os.path.join(RAW_DATA_PATH, os.path.splitext(fname)[0] + '.txt')

            if not os.path.exists(txt_path): continue

            img = cv2.imread(img_path)
            if img is None: continue

            h, w, _ = img.shape

            # Obține TOATE vehiculele din poză
            crops = get_all_crops_coordinates(txt_path, w, h)

            for i, (class_id, x1, y1, x2, y2) in enumerate(crops):
                if class_id not in CLASS_MAPPING: continue

                class_name = CLASS_MAPPING[class_id]
                dest_dir = os.path.join(OUTPUT_DIRS[split_type], class_name)

                # Nume unic pentru fiecare crop: imagine_originala_crop_0.jpg
                crop_filename = f"{os.path.splitext(fname)[0]}_crop_{i}.jpg"
                output_path = os.path.join(dest_dir, crop_filename)

                # Decupare și Redimensionare
                cropped_img = img[y1:y2, x1:x2]
                final_img = cv2.resize(cropped_img, IMAGE_SIZE, interpolation=cv2.INTER_AREA)

                cv2.imwrite(output_path, final_img)
                total_crops += 1

            images_processed += 1

    print(f"\n✅ GATA! Din {images_processed} imagini sursă, am generat {total_crops} imagini de antrenament (Crops).")
    print("Acum datele sunt curate, centrate și mult mai numeroase!")


if __name__ == '__main__':
    create_directory_structure()
    main_processing()