# 🔋 BatteryGuardian AI — Offline Snapdragon Copilot+ PC Demo

A **fully offline**, explainable battery telemetry monitoring prototype for Windows on Snapdragon (ARM64). Uses only the Python standard library; no cloud, accounts, API keys, external JS, or model downloads.

> **Scope:** This is a transparent rule-based anomaly detector with plain-English explanations, **not a trained ML/LLM system**. It runs on the Snapdragon **CPU**, not the Hexagon NPU. Do not claim NPU inference or predictive battery health. It demonstrates a dependable offline baseline that can be extended with an NPU-accelerated ONNX model later.

## Quick start (Windows ARM64)

1. Install **Windows ARM64 Python 3.11+** (installer can be obtained ahead of time).
2. Open PowerShell in the project directory:

```powershell
py -3 -m batteryguardian.server
```

If the `py` launcher is unavailable, use `python -m batteryguardian.server`.

3. Open **http://127.0.0.1:8765** and click **Load demonstration**. Disconnect Wi-Fi to verify offline operation.
4. To run tests:

```powershell
python -m unittest discover -s tests -v
```

## CSV schema

`timestamp,voltage_v,current_a,temperature_c,soc_pct`

The demo file is `data/demo.csv`. Import CSVs through the browser; uploads stay on the local loopback server. No external network requests. Up to 2 MB and 10,000 rows. Timestamps are labels; rows are processed in file order and not automatically sorted.

## Detection and explanation

- Temperature >= 45°C: warning; >= 60°C: critical.
- Temperature jump >= 8°C between consecutive observations: warning.
- Voltage drop >= 12% between consecutive observations: warning.
- State of charge <= 10%: warning.
- The UI explains the rules that fired and plots temperature history.

**All thresholds are illustrative, not validated for any battery chemistry, pack configuration, or sensor.** Temperature jump rules are not normalized by elapsed time. Severity is derived from individual observations, not from statistical risk probability. An absence of alerts does not establish safety. Do not connect this prototype to battery controls or rely on it to detect thermal runaway.

## Architecture

```text
Local CSV -> validated parser -> deterministic anomaly rules
                                  |-> event log (latest 100)
                                  |-> explanation + severity
                                  |-> offline HTML/JS dashboard
```

- Python HTTP server binds to **127.0.0.1 only**.
- Browser UI has no CDN or external dependencies.
- No telemetry is persisted by the server.
- JSON responses, text-only DOM insertion, CSV bounds checks, and a restrictive content security policy reduce avoidable risks.
- A GitHub Actions workflow runs unit tests on commits; **CI is online and separate from the offline runtime**.

## Snapdragon NPU upgrade path (not implemented)

1. Obtain a battery dataset with labeled faults and an appropriate sampling rate.
2. Train and validate a compact anomaly model, quantify false-positive/false-negative rates, and export to ONNX.
3. Test compatibility with Windows ML / ONNX Runtime QNN on the **specific** Snapdragon Copilot+ PC and verify that execution actually uses the Hexagon NPU.
4. Keep deterministic safety-related rules outside the model and provide evidence-based local explanations. Add an offline SLM only if hardware, model license, memory, and inference runtime support are verified.
5. Document measured latency, resource use, and an unplugged-network test.


## Engineering practices

Built with input validation, bounded payloads and results, deterministic explanations, local-only access, documented limitations, test coverage, and a minimal dependency footprint. Inspired by the uploaded engineering skill materials, which are **not redistributed** in this repository.

## License

MIT (see `LICENSE`).


## PyTorch + ExecuTorch research upgrade

This version adds a compact PyTorch model, synthetic demo training, held-out test metrics, ONNX export, optional portable ExecuTorch export, and CPU benchmarking. **It does not yet execute on the Hexagon NPU.** See [Snapdragon deployment and validation](docs/DEPLOYMENT.md) for precise limitations, target-device checklist, and real-data requirements.

```powershell
python -m pip install -r requirements-ml.txt
python -m ml.train
python -m ml.export_onnx
python -m scripts.benchmark
python -m unittest discover -s tests -v
```

If you have ExecuTorch installed in a compatible environment, `python -m ml.export_executorch` creates a portable `.pte` file (not Qualcomm delegated). Synthetic accuracy is not evidence of real battery-fault performance.

## Upgrade instructions: existing GitHub installation → PyTorch + ExecuTorch

These steps upgrade an existing checkout of `BatteryGuardian-AI` to the research ML version. **The project runs offline on the CPU; Hexagon NPU execution is not implemented or verified.** Back up any local modifications first.

### A. Replace the source files

1. Download `BatteryGuardian-AI-PyTorch-ExecuTorch.zip` and choose **Extract All** in Windows Explorer.
2. Open the extracted `BatteryGuardian-AI` folder. It should contain `README.md`, `batteryguardian/`, `ml/`, `tests/`, `scripts/`, `requirements-ml.txt`, and `docs/`.
3. Copy **the contents** of that folder into your existing local Git repository's `BatteryGuardian-AI` directory, preserving the folder structure and replacing old files when prompted. Do **not** copy the ZIP file into the repository or create a second nested `BatteryGuardian-AI` folder.
4. Keep your existing `.git` folder; do not overwrite or delete it. Review changes with `git status` and `git diff` before committing.

For a **new** GitHub repository, simply extract the ZIP, open PowerShell in the extracted project directory, and follow [Repository upload](#repository-upload).

### B. Install and validate the ML environment

Open PowerShell in the repository root. Use a Python environment with compatible PyTorch binaries (native Windows ARM64 packages may vary by version). Download dependencies **before** switching the machine offline:

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-ml.txt
python -m unittest discover -s tests -v
```

If PowerShell blocks activation, use `.venv\Scripts\python.exe` in place of `python` for subsequent commands. The `.venv` folder should remain untracked by Git.

### C. Train, evaluate, and export

```powershell
python -m ml.train
python -m ml.export_onnx
python -m scripts.benchmark
```

Training uses **synthetic** battery data; evaluation metrics are for demonstration only. The ONNX export requires the `onnx` dependency listed in `requirements-ml.txt`. Inspect the outputs under `artifacts/` and `reports/` and see `docs/DEPLOYMENT.md` for evaluation and hardware-evidence requirements.

If a compatible ExecuTorch build is separately installed, you may additionally run:

```powershell
python -m ml.export_executorch
```

This exports a **portable, non-QNN-delegated** ExecuTorch model. It does **not** establish Hexagon NPU acceleration. ExecuTorch installation and Qualcomm backend compatibility must be checked for your specific Snapdragon Windows machine.

### D. Run and test offline

```powershell
python -m batteryguardian.server
```

Open `http://127.0.0.1:8765`, select **Load demonstration**, and inspect the advisory ML results and independent rule-based warnings. To verify offline behavior, disconnect Wi-Fi and Ethernet, restart the app, and repeat the demonstration. Record the device SKU, OS build, model/runtime versions, median and p95 latency, memory use, and offline results; do not claim NPU execution without delegate/profiler evidence.

### E. Commit the upgrade to GitHub

After reviewing changes, run these commands **inside your existing repository**:

```powershell
git status
git add README.md batteryguardian ml tests scripts docs requirements-ml.txt artifacts reports checks
git commit -m "Add PyTorch battery anomaly detection and ExecuTorch export path"
git push origin main
```

If your default branch is not `main`, substitute its name. `git add` only stages paths that exist and are not ignored; if your checkout differs, use `git add -A` after reviewing `git status`. Never commit local virtual environments, credentials, proprietary battery records, or large unlicensed datasets. See [Snapdragon deployment and validation](docs/DEPLOYMENT.md) for the remaining **real-data validation, QNN/NPU delegation, and measured hardware testing** tasks.
