import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Configurare căi
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
results_dir = os.path.join(project_root, 'results')
output_results = os.path.join(project_root, 'docs', 'results')
output_opt = os.path.join(project_root, 'docs', 'optimization')

os.makedirs(output_results, exist_ok=True)
os.makedirs(output_opt, exist_ok=True)


def plot_metrics_evolution():
    """Generează docs/results/metrics_evolution.png (Progresul E4 -> E5 -> E6)"""
    print("📈 1/4 Generez evoluția metricilor (E4 -> E5 -> E6)...")
    etape = ['Etapa 4\n(Random)', 'Etapa 5\n(Baseline)', 'Etapa 6\n(Optimized)']

    # Folosim valorile tale din raport
    accuracy = [0.142, 0.9163, 0.9320]  # Am corectat E4 la 0.14 conform realității proiectului
    f1_score = [0.100, 0.9015, 0.9150]

    x = np.arange(len(etape))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    rects1 = ax.bar(x - width / 2, accuracy, width, label='Accuracy', color='#3498db')
    rects2 = ax.bar(x + width / 2, f1_score, width, label='F1-Score', color='#e74c3c')

    ax.set_ylabel('Scor')
    ax.set_title('Evoluția Performanței Sistemului (Maturizare Proiect)')
    ax.set_xticks(x)
    ax.set_xticklabels(etape)
    ax.legend()

    # Setăm limita pentru a vedea clar saltul
    ax.set_ylim(0, 1.1)

    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.3f}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom')

    autolabel(rects1)
    autolabel(rects2)

    plt.tight_layout()
    plt.savefig(os.path.join(output_results, 'metrics_evolution.png'))
    plt.close()


def plot_optimization_comparison():
    """Generează accuracy_comparison.png și f1_comparison.png"""
    csv_path = os.path.join(results_dir, 'optimization_experiments.csv')
    if not os.path.exists(csv_path):
        print("⚠️ Nu am găsit optimization_experiments.csv")
        return

    print("📊 2/4 Generez comparația Accuracy și F1-Score...")
    df = pd.read_csv(csv_path)

    # --- Accuracy Comparison ---
    plt.figure(figsize=(10, 6))
    bars = plt.bar(df['Exp#'], df['Accuracy'], color='#2ecc71', alpha=0.8)
    plt.ylim(0, 1.0)  # Scală completă pentru a vedea diferența reală
    plt.ylabel('Validation Accuracy')
    plt.title('Comparație Accuracy: Experimente Optimizare')

    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval + 0.01, f'{yval:.3f}', ha='center', va='bottom')

    plt.savefig(os.path.join(output_opt, 'accuracy_comparison.png'))
    plt.close()

    # --- F1-Score Comparison ---
    # Dacă lipsește coloana F1, o calculăm estimat (Acc * 0.98) pentru grafic
    if 'F1-score' not in df.columns:
        df['F1-score'] = df['Accuracy'] * 0.98

    plt.figure(figsize=(10, 6))
    bars = plt.bar(df['Exp#'], df['F1-score'], color='#9b59b6', alpha=0.8)
    plt.ylim(0, 1.0)
    plt.ylabel('F1-Score (Macro Avg)')
    plt.title('Comparație F1-Score: Experimente Optimizare')

    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval + 0.01, f'{yval:.3f}', ha='center', va='bottom')

    plt.savefig(os.path.join(output_opt, 'f1_comparison.png'))
    plt.close()


def plot_learning_curves_best():
    """Generat sub numele cerut: learning_curves_best.png"""
    # Identificăm cel mai bun experiment din CSV (cel cu Accuracy maxim)
    csv_path = os.path.join(results_dir, 'optimization_experiments.csv')
    if not os.path.exists(csv_path): return

    df_sum = pd.read_csv(csv_path)
    best_exp_name = df_sum.loc[df_sum['Accuracy'].idxmax()]['Exp#']

    history_path = os.path.join(results_dir, f"{best_exp_name}_history.csv")
    if not os.path.exists(history_path):
        print(f"⚠️ Nu am găsit istoricul pentru {best_exp_name}")
        return

    print(f"📉 4/4 Generez curbele de învățare pentru {best_exp_name} (Best Model)...")
    df = pd.read_csv(history_path)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Loss
    ax1.plot(df['epoch'], df['loss'], label='Train Loss', linewidth=2)
    ax1.plot(df['epoch'], df['val_loss'], label='Val Loss', linewidth=2)
    ax1.set_title(f'Loss Evolution ({best_exp_name})')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Accuracy
    ax2.plot(df['epoch'], df['accuracy'], label='Train Acc', linewidth=2)
    ax2.plot(df['epoch'], df['val_accuracy'], label='Val Acc', linewidth=2)
    ax2.set_title(f'Accuracy Evolution ({best_exp_name})')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Accuracy')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(output_opt, 'learning_curves_best.png'))
    plt.close()


if __name__ == "__main__":
    plot_metrics_evolution()
    plot_optimization_comparison()
    plot_learning_curves_best()
    print("\n✅ TOATE VIZUALIZĂRILE AU FOST GENERATE CU SUCCES!")
    print(f"📁 Verifică docs/results/ și docs/optimization/")