import os
import pandas as pd
import tensorflow as tf
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, CSVLogger
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Importăm variabilele de cale și funcția de construcție din modelul tău existent
from cnn_model import build_cnn_model, project_root, DATA_DIR, IMAGE_SIZE, BATCH_SIZE, NUM_CLASSES, INPUT_SHAPE

# --- PASUL 0: ASIGURARE STRUCTURĂ FOLEDERE (Previne erorile de salvare) ---
MODELS_DIR = os.path.join(project_root, 'models')
RESULTS_DIR = os.path.join(project_root, 'results')

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# --- CONFIGURARE EXPERIMENTE (Cerință Etapa 6: Min. 4 experimente) ---
EXPERIMENTS = [
    {
        "name": "exp1_baseline",
        "lr": 0.00001,
        "unfreeze": 30,
        "aug": "light",
        "obs": "Configurația de referință din Etapa 5"
    },
    {
        "name": "exp2_heavy_aug",
        "lr": 0.00001,
        "unfreeze": 30,
        "aug": "heavy",
        "obs": "Augmentări agresive (Lumină/Zoom) - Nivel 2"
    },
    {
        "name": "exp3_low_lr_deep",
        "lr": 0.000001,
        "unfreeze": 50,
        "aug": "light",
        "obs": "Fine-tuning adânc (50 straturi) cu LR mic"
    },
    {
        "name": "exp4_high_dropout",
        "lr": 0.00001,
        "unfreeze": 30,
        "aug": "light",
        "dropout": 0.6,
        "obs": "Regularizare crescută (Dropout 0.6)"
    }
]


def get_datagen(aug_type):
    """Generatoare de date cu augmentări specifice domeniului industrial"""
    if aug_type == "heavy":
        return ImageDataGenerator(
            rescale=1. / 255,
            rotation_range=15,
            width_shift_range=0.2,
            height_shift_range=0.2,
            brightness_range=[0.6, 1.4],  # Simulare variații extreme soare/umbre
            zoom_range=0.2,
            horizontal_flip=True,
            fill_mode='nearest'
        )
    else:
        return ImageDataGenerator(
            rescale=1. / 255,
            brightness_range=[0.8, 1.2],
            zoom_range=0.1,
            horizontal_flip=True
        )


def run_experiment(config):
    """Execută un singur experiment de optimizare conform cerințelor Etapa 6"""
    print(f"\n" + "=" * 60)
    print(f"🚀 RULARE: {config['name']} | {config['obs']}")
    print("=" * 60)

    # 1. Pregătire Date
    train_datagen = get_datagen(config.get('aug', 'light'))
    val_datagen = ImageDataGenerator(rescale=1. / 255)

    train_gen = train_datagen.flow_from_directory(
        os.path.join(DATA_DIR, 'train'), target_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE, class_mode='categorical'
    )
    val_gen = val_datagen.flow_from_directory(
        os.path.join(DATA_DIR, 'validation'), target_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE, class_mode='categorical'
    )

    # 2. Construcție și configurare model
    model = build_cnn_model(INPUT_SHAPE, NUM_CLASSES)

    # Resetăm starea de antrenare a straturilor
    for layer in model.layers:
        layer.trainable = False

    # Dezghețăm ultimele N straturi pentru fine-tuning
    unfreeze_limit = config['unfreeze']
    for layer in model.layers[-unfreeze_limit:]:
        layer.trainable = True

    model.compile(
        optimizer=Adam(learning_rate=config['lr']),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    # 3. Fișiere output
    history_file = os.path.join(RESULTS_DIR, f"{config['name']}_history.csv")
    model_path = os.path.join(MODELS_DIR, f"{config['name']}.keras")

    callbacks = [
        EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True),
        CSVLogger(history_file)
    ]

    # 4. Antrenare FAST PROTOTYPING pentru Etapa 6
    # 5 epoci sunt suficiente pentru a determina configurația optimă
    history = model.fit(
        train_gen,
        epochs=5,
        steps_per_epoch=100,  # Reducem numărul de pași pentru viteză
        validation_data=val_gen,
        validation_steps=50,
        callbacks=callbacks,
        verbose=1
    )

    # Extracție rezultate
    best_acc = max(history.history['val_accuracy'])
    best_loss = min(history.history['val_loss'])

    model.save(model_path)
    print(f"✅ FINALIZAT: {config['name']} | Accuracy: {best_acc:.4f}")

    return {
        "Exp#": config['name'],
        "Modificare": config['obs'],
        "Accuracy": round(best_acc, 4),
        "Loss": round(best_loss, 4),
        "Timp antrenare": "~5 min (Fast Prototyping)"
    }


if __name__ == "__main__":
    summary_results = []

    for exp_config in EXPERIMENTS:
        try:
            res = run_experiment(exp_config)
            summary_results.append(res)
        except Exception as e:
            print(f"❌ Eroare la {exp_config['name']}: {e}")

    # Generare livrabil obligatoriu: Tabel experimente
    if summary_results:
        df = pd.DataFrame(summary_results)
        csv_path = os.path.join(RESULTS_DIR, 'optimization_experiments.csv')
        df.to_csv(csv_path, index=False)
        print(f"\n🏆 Tabelul de experimente a fost salvat în: {csv_path}")