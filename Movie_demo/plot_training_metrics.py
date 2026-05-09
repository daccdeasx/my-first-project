import json
import math
from pathlib import Path
import matplotlib.pyplot as plt


def plot_metrics(history_path: Path, output_path: Path):
    if not history_path.exists():
        raise FileNotFoundError(f"未找到训练历史文件: {history_path}")

    with history_path.open("r", encoding="utf-8") as f:
        hist = json.load(f)

    mse = hist.get("loss", [])
    val_mse = hist.get("val_loss", [])
    mae = hist.get("mae", [])
    val_mae = hist.get("val_mae", [])
    rmse = [math.sqrt(v) for v in mse]
    val_rmse = [math.sqrt(v) for v in val_mse]

    epochs = range(1, len(mse) + 1)
    plt.figure(figsize=(8, 5))
    plt.plot(epochs, mse, label="Train MSE")
    plt.plot(epochs, val_mse, label="Val MSE")
    plt.plot(epochs, mae, label="Train MAE")
    plt.plot(epochs, val_mae, label="Val MAE")
    plt.plot(epochs, rmse, label="Train RMSE")
    plt.plot(epochs, val_rmse, label="Val RMSE")

    plt.xlabel("Epoch")
    plt.ylabel("Metric")
    plt.title("Recommendation Model Training Metrics")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150)
    print(f"已保存指标图: {output_path}")


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent
    logs_dir = base_dir / "logs"
    history_file = logs_dir / "training_history.json"
    output_file = logs_dir / "training_metrics.png"
    plot_metrics(history_file, output_file)





