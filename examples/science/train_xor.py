"""Python reference for the UrduPy nonlinear XOR training example."""

import argparse
import hashlib
import json
import platform
from pathlib import Path

import torch


class عصبی_نیٹ(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.layers = torch.nn.Sequential(
            torch.nn.Linear(2, 16),
            torch.nn.Tanh(),
            torch.nn.Linear(16, 16),
            torch.nn.Tanh(),
            torch.nn.Linear(16, 1),
        )

    def forward(self, x):
        return self.layers(x).squeeze(-1)


def ڈیٹا_بناؤ(count, seed):
    # Opposite signs mean 1; matching signs mean 0. Separate seeds split the data.
    generator = torch.Generator(device="cpu").manual_seed(seed)
    inputs = torch.rand(count, 2, generator=generator, device="cpu") * 2 - 1
    targets = ((inputs[:, 0] > 0) != (inputs[:, 1] > 0)).float()
    return inputs, targets


def تربیت(*, epochs=600, seed=42, verbose=True):
    if epochs < 1:
        raise ValueError("epochs must be positive")
    original_threads = torch.get_num_threads()
    try:
        torch.set_num_threads(1)
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(seed)
            train_x, train_y = ڈیٹا_بناؤ(2048, seed + 1)
            model = عصبی_نیٹ().to(device="cpu", dtype=torch.float32)
            criterion = torch.nn.BCEWithLogitsLoss()
            optimizer = torch.optim.Adam(model.parameters(), lr=0.02)
            model.train()
            with torch.no_grad():
                initial_loss = criterion(model(train_x), train_y).item()
            history = [{"epoch": 0, "train_loss": initial_loss}]

            for epoch in range(1, epochs + 1):
                optimizer.zero_grad(set_to_none=True)
                loss = criterion(model(train_x), train_y)
                loss.backward()
                optimizer.step()
                if epoch % 100 == 0 or epoch == epochs:
                    with torch.no_grad():
                        current_loss = criterion(model(train_x), train_y).item()
                    history.append({"epoch": epoch, "train_loss": current_loss})
                    if verbose:
                        print(f"Epoch {epoch:4d}/{epochs}: train loss {current_loss:.6f}")

            # Evaluate only after the fixed training schedule; no test-based tuning.
            test_x, test_y = ڈیٹا_بناؤ(1024, seed + 2)
            model.eval()
            with torch.no_grad():
                test_logits = model(test_x)
                test_loss = criterion(test_logits, test_y).item()
                test_correct = ((test_logits >= 0) == test_y.bool()).sum().item()
                probes = torch.tensor([[-0.75, -0.75], [-0.75, 0.75],
                                       [0.75, -0.75], [0.75, 0.75]])
                probabilities = model(probes).sigmoid().tolist()
            report = {
                "task": "synthetic_sign_xor",
                "input_distribution": "two independent Uniform[-1, 1) coordinates",
                "target": "1 when coordinate signs differ, otherwise 0",
                "architecture": [2, 16, 16, 1],
                "hidden_activation": "tanh",
                "parameters": sum(p.numel() for p in model.parameters()),
                "optimizer": "Adam",
                "learning_rate": 0.02,
                "epochs": epochs,
                "seed": seed,
                "train_samples": 2048,
                "test_samples": 1024,
                "train_data_seed": seed + 1,
                "test_data_seed": seed + 2,
                "initial_train_loss": initial_loss,
                "final_train_loss": history[-1]["train_loss"],
                "test_loss": test_loss,
                "test_correct": test_correct,
                "test_accuracy": test_correct / 1024,
                "history": history,
                "xor_inputs": probes.tolist(),
                "xor_expected": [0, 1, 1, 0],
                "xor_probabilities": probabilities,
                "xor_predictions": [int(p >= 0.5) for p in probabilities],
                "device": "cpu",
                "dtype": "float32",
                "threads": 1,
                "python_version": platform.python_version(),
                "torch_version": str(torch.__version__),
                "platform": platform.platform(),
            }
            return model, report
    finally:
        torch.set_num_threads(original_threads)


def محفوظ_کرو(model, report, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    weights_path = output / "model.pt"
    torch.save(model.state_dict(), weights_path)
    # Save tensors only; loading does not depend on pickling the Urdu class.
    original_threads = torch.get_num_threads()
    try:
        torch.set_num_threads(1)
        with torch.random.fork_rng(devices=[]):
            restored = عصبی_نیٹ()
        restored.load_state_dict(torch.load(weights_path, map_location="cpu", weights_only=True))
        restored.eval()
        test_x, _ = ڈیٹا_بناؤ(report["test_samples"], report["test_data_seed"])
        with torch.no_grad():
            error = (model(test_x) - restored(test_x)).abs().max().item()
        if error != 0:
            raise RuntimeError(f"Checkpoint predictions changed: {error}")
    finally:
        torch.set_num_threads(original_threads)
    saved_report = dict(report)
    saved_report["checkpoint_max_abs_error"] = error
    saved_report["checkpoint_sha256"] = hashlib.sha256(weights_path.read_bytes()).hexdigest()
    saved_report["source_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (output / "metrics.json").write_text(
        json.dumps(saved_report, indent=2, ensure_ascii=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return weights_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--epochs", type=int, default=600)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("runs/xor"))
    args = parser.parse_args()
    if args.epochs < 1:
        parser.error("--epochs must be positive")
    model, report = تربیت(epochs=args.epochs, seed=args.seed)
    weights_path = محفوظ_کرو(model, report, args.output)
    print(f"Train loss: {report['initial_train_loss']:.6f} -> {report['final_train_loss']:.6f}")
    print(f"Held-out accuracy: {report['test_accuracy']:.2%} ({report['test_correct']}/1024)")
    print(f"XOR predictions: {report['xor_predictions']}; expected: {report['xor_expected']}")
    print(f"Saved: {weights_path} and {args.output / 'metrics.json'}; reload predictions match exactly")


if __name__ == "__main__":
    main()
