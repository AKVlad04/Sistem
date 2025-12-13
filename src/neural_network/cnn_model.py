import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.applications import MobileNetV2
import os

# --- Căi ---
current_script_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_script_path)))

DATA_DIR = os.path.join(project_root, 'data', 'processed')
TRAIN_DIR = os.path.join(DATA_DIR, 'train')
VAL_DIR = os.path.join(DATA_DIR, 'validation')
TEST_DIR = os.path.join(DATA_DIR, 'test')
MODEL_SAVE_PATH = os.path.join(project_root, 'config', 'vehicle_classifier_model.keras')

# --- Parametri ---
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
NUM_CLASSES = 7  # (0-5 Vehicule + 6 Altele)
INPUT_SHAPE = IMAGE_SIZE + (3,)
EPOCHS = 30 # 30 de epoci sunt suficiente pentru datele crop-uite


def build_cnn_model(input_shape, num_classes):
    # 1. MobileNetV2 (Pre-antrenat)
    base_model = MobileNetV2(
        weights='imagenet',
        include_top=False,
        input_shape=input_shape
    )

    # 2. Înghețăm inițial tot
    for layer in base_model.layers:
        layer.trainable = False

    # 3. Dezgheață ultimele 30 de straturi pentru adaptare la vehiculele tale
    # (Asta este cheia pentru a trece de 90%)
    for layer in base_model.layers[-30:]:
        layer.trainable = True

    # 4. Custom Head
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(512, activation='relu')(x)
    x = Dropout(0.5)(x)  # Previne memorarea
    predictions = Dense(num_classes, activation='softmax')(x)

    model = Model(inputs=base_model.input, outputs=predictions)

    # 5. Compilare (Learning Rate MIC pentru fine-tuning)
    custom_optimizer = Adam(learning_rate=0.00001)

    model.compile(optimizer=custom_optimizer,
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])
    return model


def run_training():
    if not os.path.exists(TRAIN_DIR):
        print("EROARE: Nu există date procesate. Rulează data_preparator.py!")
        return

    # Augmentare ușoară pentru a ajuta generalizarea
    train_datagen = ImageDataGenerator(
        rescale=1. / 255,
        rotation_range=15,
        width_shift_range=0.1,
        height_shift_range=0.1,
        horizontal_flip=True,
        fill_mode='nearest'
    )
    val_test_datagen = ImageDataGenerator(rescale=1. / 255)

    print("--- Încărcare Date ---")
    train_generator = train_datagen.flow_from_directory(
        TRAIN_DIR, target_size=IMAGE_SIZE, batch_size=BATCH_SIZE, color_mode='rgb', class_mode='categorical'
    )
    validation_generator = val_test_datagen.flow_from_directory(
        VAL_DIR, target_size=IMAGE_SIZE, batch_size=BATCH_SIZE, color_mode='rgb', class_mode='categorical'
    )

    # Construim modelul mereu de la zero pentru consistență în acest pas
    model = build_cnn_model(INPUT_SHAPE, NUM_CLASSES)
    model.summary()

    callbacks = [
        tf.keras.callbacks.ModelCheckpoint(
            MODEL_SAVE_PATH, monitor='val_loss', save_best_only=True, verbose=1
        )
    ]

    print(f"\n🚀 Începe Antrenarea ({EPOCHS} epoci)...")
    model.fit(
        train_generator,
        steps_per_epoch=train_generator.samples // BATCH_SIZE,
        epochs=EPOCHS,
        validation_data=validation_generator,
        validation_steps=validation_generator.samples // BATCH_SIZE,
        callbacks=callbacks
    )

    print("\n--- Evaluare Finală ---")
    test_generator = val_test_datagen.flow_from_directory(
        TEST_DIR, target_size=IMAGE_SIZE, batch_size=BATCH_SIZE, color_mode='rgb', class_mode='categorical',
        shuffle=False
    )

    # Încărcăm cel mai bun model salvat
    best_model = tf.keras.models.load_model(MODEL_SAVE_PATH)
    loss, accuracy = best_model.evaluate(test_generator)

    print(f"\n🏆 REZULTAT FINAL:")
    print(f"Acuratețe: {accuracy * 100:.2f}%")
    print(f"Maparea claselor: {train_generator.class_indices}")


if __name__ == '__main__':
    run_training()