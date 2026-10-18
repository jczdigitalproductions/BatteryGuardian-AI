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

## Repository upload

```powershell
git init
git add .
git commit -m "Initial BatteryGuardian offline prototype"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/BatteryGuardian-AI.git
git push -u origin main
```

Create an empty repository on GitHub first, and replace `YOUR_USERNAME`. GitHub authentication may be required for pushing; the app itself does not need GitHub or internet.

## Engineering practices

Built with input validation, bounded payloads and results, deterministic explanations, local-only access, documented limitations, test coverage, and a minimal dependency footprint. Inspired by the uploaded engineering skill materials, which are **not redistributed** in this repository.

## License

MIT (see `LICENSE`).
