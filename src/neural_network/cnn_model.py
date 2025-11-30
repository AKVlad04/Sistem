import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, GlobalAveragePooling2D
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.applications import MobileNetV2
import os

current_script_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_script_path)))

DATA_DIR = os.path.join(project_root, 'data', 'processed')
TRAIN_DIR = os.path.join(DATA_DIR, 'train')
VAL_DIR = os.path.join(DATA_DIR, 'validation')
TEST_DIR = os.path.join(DATA_DIR, 'test')

MODEL_SAVE_PATH = os.path.join(project_root, 'config', 'vehicle_classifier_model.keras')

IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
NUM_CLASSES = 6
# MODIFICAT: Setăm epocile pentru faza de Fine-Tuning
EPOCHS = 30
INPUT_SHAPE = IMAGE_SIZE + (3,)


def build_cnn_model(input_shape, num_classes):
    """
    Construiește modelul MobileNetV2 cu Custom Head, configurat pentru Fine-Tuning.
    """
    # 1. Încarcă MobileNetV2 (bază)
    base_model = MobileNetV2(
        weights='imagenet',
        include_top=False,
        input_shape=input_shape
    )

    # 2A. ÎNGHEAȚĂ (Freeze) straturile inițiale
    for layer in base_model.layers:
        layer.trainable = False

    # 2B. FINE-TUNING: Dezgheață ultimele 40 de straturi
    fine_tune_at = -20
    for layer in base_model.layers[fine_tune_at:]:
        layer.trainable = True

    # 3. Custom Head (Clasificatorul nostru)
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(512, activation='relu')(x)
    x = Dropout(0.5)(x)
    predictions = Dense(num_classes, activation='softmax')(x)

    model = Model(inputs=base_model.input, outputs=predictions)

    # 4. COMPILAREA cu RATA DE ÎNVĂȚARE FOARTE MICĂ (pentru Fine-Tuning)
    custom_optimizer = Adam(learning_rate=0.000005)

    model.compile(optimizer=custom_optimizer,
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])

    return model


def run_training():
    if not os.path.exists(TRAIN_DIR):
        print(f"EROARE: Nu găsesc datele în {TRAIN_DIR}")
        return

    # --- 3. Generatoare de Date ---
    train_datagen = ImageDataGenerator(
        rescale=1. / 255,
        rotation_range=30,  # Rotire mai mare (era 10)
        width_shift_range=0.2,  # Deplasare mai mare (era 0.1)
        height_shift_range=0.2,
        shear_range=0.2,  # Deformare (nou)
        zoom_range=0.3,  # Zoom mai agresiv (era 0.1)
        horizontal_flip=True,
        brightness_range=[0.8, 1.2],  # Simulare zi/seară (nou)
        fill_mode='nearest'
    )

    val_test_datagen = ImageDataGenerator(rescale=1. / 255)

    print("Încărcare date antrenare...")
    train_generator = train_datagen.flow_from_directory(
        TRAIN_DIR, target_size=IMAGE_SIZE, batch_size=BATCH_SIZE, color_mode='rgb', class_mode='categorical'
    )
    print("Încărcare date validare...")
    validation_generator = val_test_datagen.flow_from_directory(
        VAL_DIR, target_size=IMAGE_SIZE, batch_size=BATCH_SIZE, color_mode='rgb', class_mode='categorical'
    )

    # --- 4. Construire sau Încărcare Model (Checkpointing FIX) ---

    # 4A. Definirea Optimizer-ului (necesar pentru re-compilare)
    custom_optimizer = Adam(learning_rate=0.00001)

    if os.path.exists(MODEL_SAVE_PATH):
        # NOU: ÎNCARCĂ MODELUL SALVAT CU GREUTĂȚILE DE 69%
        model = tf.keras.models.load_model(MODEL_SAVE_PATH)

        # FIX: Recompilăm pentru a aplica rata de învățare ultra-mică pe straturile dezghețate
        model.compile(optimizer=custom_optimizer,
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])

        print(
            f"\nCONTINUARE: Modelul salvat ({MODEL_SAVE_PATH}) a fost încărcat. Se continuă antrenarea (Fine-Tuning).")

    else:
        # START NOU: Construim modelul MobileNetV2 de la zero (cu greutățile ImageNet)
        model = build_cnn_model(INPUT_SHAPE, NUM_CLASSES)
        print("\nSTART NOU: Niciun model salvat găsit. Se începe Fine-Tuning de la ImageNet.")

    model.summary()

    # Callback pentru a salva cel mai bun model
    callbacks = [
        tf.keras.callbacks.ModelCheckpoint(
            MODEL_SAVE_PATH,
            monitor='val_loss',
            save_best_only=True,
            verbose=1
        )
    ]

    print(f"\n🚀 Începe ANTRENAREA de FINE-TUNING pentru {EPOCHS} epoci.")
    history = model.fit(
        train_generator,
        steps_per_epoch=train_generator.samples // BATCH_SIZE,
        epochs=EPOCHS,
        validation_data=validation_generator,
        validation_steps=validation_generator.samples // BATCH_SIZE,
        callbacks=callbacks
    )

    # --- 5. Evaluare Finală ---
    print("\n📊 Evaluare pe setul de TEST...")
    test_generator = val_test_datagen.flow_from_directory(
        TEST_DIR, target_size=IMAGE_SIZE, batch_size=BATCH_SIZE, color_mode='rgb', class_mode='categorical',
        shuffle=False
    )

    # Încărcăm cel mai bun model salvat pentru testare
    best_model = tf.keras.models.load_model(MODEL_SAVE_PATH)
    loss, accuracy = best_model.evaluate(test_generator)

    print(f"\n✅ REZULTAT FINAL:")
    print(f"Acuratețe (Accuracy): {accuracy * 100:.2f}%")
    print(f"Pierdere (Loss): {loss:.4f}")
    print(f"Model salvat în: {MODEL_SAVE_PATH}")
    print(f"Maparea claselor: {train_generator.class_indices}")


if __name__ == '__main__':
    # ⚠️ ATENȚIE: Verifică în consolă dacă modelul pornește din CONTINUARE sau START NOU.
    # Dacă pornește din CONTINUARE, acuratețea ar trebui să înceapă de la ~69%.
    run_training()