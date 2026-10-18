"""Fixed 8-sample windows, oldest to newest; five telemetry features per sample."""
import numpy as np
from batteryguardian.core import parse_csv
FEATURES = ('voltage_v', 'current_a', 'temperature_c', 'soc_pct')
WINDOW = 8
MEAN = np.array([3.7, 0.0, 30.0, 60.0], dtype=np.float32)
SCALE = np.array([0.7, 15.0, 25.0, 40.0], dtype=np.float32)

def windows_from_samples(samples):
    if len(samples) < WINDOW:
        raise ValueError(f'At least {WINDOW} samples required')
    x = np.array([[getattr(s, k) for k in FEATURES] for s in samples], dtype=np.float32)
    if not np.isfinite(x).all():
        raise ValueError('Non-finite values')
    x = np.clip((x-MEAN)/SCALE, -8, 8)
    return np.stack([x[i:i+WINDOW] for i in range(len(x)-WINDOW+1)])

def load_labeled_csv(path):
    """Columns: timestamp, voltage_v, current_a, temperature_c, soc_pct, fault_label.
    Labels refer to the END of each 8-row window; 0 normal, 1 fault.
    One file must represent one continuous session. Split by session, not random rows.
    """
    import csv
    from pathlib import Path
    text=Path(path).read_text(encoding='utf-8')
    samples=parse_csv(text)
    rows=list(csv.DictReader(text.splitlines()))
    if 'fault_label' not in rows[0]:
        raise ValueError('Missing fault_label')
    labels=[]
    for r in rows:
        if r['fault_label'] not in ('0','1'):
            raise ValueError('fault_label must be 0 or 1')
        labels.append(int(r['fault_label']))
    return windows_from_samples(samples), np.asarray(labels[WINDOW-1:], dtype=np.int64)
