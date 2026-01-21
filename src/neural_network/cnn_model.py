import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, CSVLogger, ModelCheckpoint
import os
import numpy as np

# --- 1. CONFIGURARE CĂI ---
current_script_path = os.path.abspath(__file__)
# Navigăm: src/neural_network/cnn_model.py -> src/neural_network -> src -> root
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_script_path)))

DATA_DIR = os.path.join(project_root, 'data', 'processed')
TRAIN_DIR = os.path.join(DATA_DIR, 'train')
VAL_DIR = os.path.join(DATA_DIR, 'validation')
TEST_DIR = os.path.join(DATA_DIR, 'test')

# Locații livrabile Etapa 5
MODEL_SAVE_PATH = os.path.join(project_root, 'config', 'vehicle_classifier_model.keras')
HISTORY_LOG_PATH = os.path.join(project_root, 'results', 'training_history.csv')

# Creare folder results dacă nu există
os.makedirs(os.path.join(project_root, 'results'), exist_ok=True)

# --- 2. PARAMETRI ---
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
NUM_CLASSES = 7
INPUT_SHAPE = IMAGE_SIZE + (3,)
EPOCHS = 50  # Creștem numărul maxim, EarlyStopping va opri procesul când e gata


def build_cnn_model(input_shape, num_classes):
    """
    Construiește arhitectura bazată pe MobileNetV2 cu Transfer Learning.
    """
    base_model = MobileNetV2(
        weights='imagenet',
        include_top=False,
        input_shape=input_shape
    )

    # Înghețăm straturile de bază (Transfer Learning)
    base_model.trainable = False

    # Fine-tuning: Dezghețăm ultimele straturi pentru adaptare la context industrial
    # Recomandat pentru a trece de 90% acuratețe
    for layer in base_model.layers[-30:]:
        layer.trainable = True

    # Custom Head (Nivel 1)
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(512, activation='relu')(x)
    x = Dropout(0.4)(x)  # Dropout pentru prevenirea overfitting-ului
    predictions = Dense(num_classes, activation='softmax')(x)

    model = Model(inputs=base_model.input, outputs=predictions)

    # Optimizer cu Learning Rate mic pentru stabilitate (Nivel 1)
    model.compile(
        optimizer=Adam(learning_rate=0.00001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    return model


def run_training():
    if not os.path.exists(TRAIN_DIR):
        print("EROARE: Datele procesate lipsesc!")
        return

    # --- 3. AUGMENTĂRI INDUSTRIALE (Nivel 2) ---
    train_datagen = ImageDataGenerator(
        rescale=1. / 255,
        brightness_range=[0.8, 1.2],  # Variații de iluminare (zi/noros)
        zoom_range=0.1,  # Slight perspective
        width_shift_range=0.1,
        height_shift_range=0.1,
        horizontal_flip=True,
        fill_mode='nearest'
    )

    # Validarea și testul primesc doar scalare
    val_test_datagen = ImageDataGenerator(rescale=1. / 255)

    print("\n--- Pregătire Data Generators ---")
    train_gen = train_datagen.flow_from_directory(
        TRAIN_DIR, target_size=IMAGE_SIZE, batch_size=BATCH_SIZE, class_mode='categorical'
    )
    val_gen = val_test_datagen.flow_from_directory(
        VAL_DIR, target_size=IMAGE_SIZE, batch_size=BATCH_SIZE, class_mode='categorical'
    )

    # --- 4. CALLBACKS AVANSATE (Nivel 2) ---

    # Oprire timpurie dacă modelul nu mai progresează
    early_stop = EarlyStopping(
        monitor='val_loss',
        patience=7,
        restore_best_weights=True,
        verbose=1
    )

    # Reducerea ratei de învățare pe platou (Scheduler)
    reduce_lr = ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.2,
        patience=4,
        min_lr=1e-7,
        verbose=1
    )

    # Salvare istoric epoci (pentru docs/loss_curve.png)
    csv_logger = CSVLogger(HISTORY_LOG_PATH, append=False)

    # Salvare cel mai bun model
    checkpoint = ModelCheckpoint(
        MODEL_SAVE_PATH, monitor='val_loss', save_best_only=True, verbose=1
    )

    callbacks_list = [early_stop, reduce_lr, csv_logger, checkpoint]

    # --- 5. ANTRENRE ---
    model = build_cnn_model(INPUT_SHAPE, NUM_CLASSES)

    print(f"\n🚀 Start Antrenare Finală...")
    model.fit(
        train_gen,
        epochs=EPOCHS,
        validation_data=val_gen,
        callbacks=callbacks_list
    )

    # --- 6. EVALUARE FINALĂ TEST SET ---
    print("\n--- Evaluare pe Setul de Test (Date Nevăzute) ---")
    test_gen = val_test_datagen.flow_from_directory(
        TEST_DIR, target_size=IMAGE_SIZE, batch_size=BATCH_SIZE, class_mode='categorical', shuffle=False
    )

    best_model = tf.keras.models.load_model(MODEL_SAVE_PATH)
    loss, acc = best_model.evaluate(test_gen)

    print(f"\nREZULTAT FINAL:")
    print(f"Acuratețe Test: {acc * 100:.2f}%")
    print(f"Mapare clase: {train_gen.class_indices}")


if __name__ == '__main__':
    run_training()