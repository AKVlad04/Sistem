import pandas as pd
import matplotlib.pyplot as plt
import os

# --- Configurare Căi ---
current_dir = os.path.dirname(os.path.abspath(__file__))
history_path = os.path.join(current_dir, 'results', 'training_history.csv')
save_path = os.path.join(current_dir, 'docs', 'loss_curve.png')

# Asigură-te că folderul docs există
os.makedirs(os.path.join(current_dir, 'docs'), exist_ok=True)

try:
    # 1. Încărcare date
    history = pd.read_csv(history_path)
    print(f"✅ Istoric încărcat: {len(history)} epoci detectate.")

    # 2. Creare figură cu două sub-grafice
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))

    # Grafic pentru LOSS
    ax1.plot(history['loss'], label='Loss Antrenare', color='blue', linewidth=2)
    ax1.plot(history['val_loss'], label='Loss Validare', color='red', linestyle='--', linewidth=2)
    ax1.set_title('Evoluție Loss (Eroare)', fontsize=12)
    ax1.set_xlabel('Epoci')
    ax1.set_ylabel('Loss')
    ax1.legend()
    ax1.grid(True, linestyle=':', alpha=0.6)

    # Grafic pentru ACCURACY
    ax2.plot(history['accuracy'], label='Acuratețe Antrenare', color='green', linewidth=2)
    ax2.plot(history['val_accuracy'], label='Acuratețe Validare', color='orange', linestyle='--', linewidth=2)
    ax2.set_title('Evoluție Acuratețe', fontsize=12)
    ax2.set_xlabel('Epoci')
    ax2.set_ylabel('Accuracy')
    ax2.legend()
    ax2.grid(True, linestyle=':', alpha=0.6)

    # Ajustare layout și salvare
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.show()

    print(f"🚀 Succes! Graficul a fost salvat în: {save_path}")

except FileNotFoundError:
    print(f"❌ Eroare: Nu am găsit fișierul {history_path}. Rulează mai întâi antrenarea!")
except Exception as e:
    print(f"❌ A apărut o eroare: {e}")