# Snapdragon / ExecuTorch deployment verification

## What is implemented

- PyTorch dense model training, validation/test split, confusion matrix rates, deterministic normalization.
- ONNX export and optional **portable CPU ExecuTorch** `.pte` export.
- Offline local inference through PyTorch CPU, independent deterministic safety alerts.

**Not implemented or verified:** Qualcomm QNN backend delegation in ExecuTorch, Hexagon NPU execution, measured Snapdragon latency, or an offline SLM. Do not describe this project as NPU accelerated until measured on the target hardware.

## Environment

Use Python 3.11+ with matching native ARM64 builds of PyTorch and dependencies. Check support for your specific Windows-on-Arm version; if PyTorch/ExecuTorch builds are unavailable, train/export on an x64 development PC and transfer the resulting files to the Snapdragon device. ExecuTorch's Qualcomm backend support is platform- and release-dependent; do not assume an Android Qualcomm build works on Windows ARM64.

```powershell
python -m pip install -r requirements-ml.txt
python -m ml.train --out artifacts
python -m ml.export_onnx
python -m scripts.benchmark
python -m batteryguardian.server
```

Optional, **only in a compatible environment with ExecuTorch installed**:

```powershell
python -m ml.export_executorch
```

For Qualcomm QNN delegation: consult the matching ExecuTorch Qualcomm backend documentation, SDK version, Windows-on-Arm platform support and Qualcomm AI Engine Direct SDK. If supported, implement and validate QNN partitioning, compile/delegate with the vendor-specific toolchain, run the model on the Snapdragon machine, capture backend partition/delegation logs and Hexagon utilization or profiler traces, and compare outputs with CPU reference. A `.pte` alone is not proof of delegation. If QNN backend is unsupported on Windows, use ONNX Runtime QNN or Windows ML as a **separate, verified backend**, not by relabeling CPU ExecuTorch as NPU.

## Required NPU evidence (fill on target PC)

| Field | Measured value |
|---|---|
| Snapdragon CPU / NPU SKU | NOT MEASURED |
| Windows build | NOT MEASURED |
| ExecuTorch / QNN / SDK versions | NOT MEASURED |
| Delegate partition log | NOT MEASURED |
| NPU profiler trace / utilization | NOT MEASURED |
| Reference vs NPU output parity | NOT MEASURED |
| Median and p95 inference ms | NOT MEASURED |
| Process peak working set MB | NOT MEASURED |
| Offline Wi-Fi disabled test (restart, inference, dashboard) | NOT TESTED |

## Data and safety

A real labeled battery dataset is NOT included. The default synthetic data is a **code-path demo** and cannot support accuracy claims for physical faults. Collect device-specific voltage, current, temperature, state of charge, timestamps, sensor specs, sampling frequency, and ground-truth fault labels with a documented fault taxonomy. Do not create unsafe battery faults for testing. Use licensed, nonhazardous historical records or safe simulators. Keep sessions grouped across splits; label windows by their final sample. Quantify FP and FN separately, test out-of-distribution devices, missing samples, timestamp jitter, calibration errors, class imbalance and early-warning lead time. Set operating thresholds based on engineering requirements, not synthetic metrics.

The existing threshold alerts always run independently; AI output is advisory only. No physical actuation, battery charging control, or claims of safety certification. No SLM is included; explanations are deterministic and grounded in measured signals.
