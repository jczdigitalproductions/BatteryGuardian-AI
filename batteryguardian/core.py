"""Deterministic, explainable offline battery telemetry screening (not a BMS)."""
import csv
import io
import math
from dataclasses import dataclass, asdict

FIELDS = ('timestamp', 'voltage_v', 'current_a', 'temperature_c', 'soc_pct')
MAX_ROWS = 10000

@dataclass(frozen=True)
class Sample:
    timestamp: str
    voltage_v: float
    current_a: float
    temperature_c: float
    soc_pct: float


def parse_csv(text: str) -> list[Sample]:
    if len(text.encode('utf-8')) > 2_000_000:
        raise ValueError('CSV exceeds 2 MB limit')
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames or not set(FIELDS).issubset(reader.fieldnames):
        raise ValueError('Required columns: ' + ', '.join(FIELDS))
    rows = []
    for index, row in enumerate(reader, 1):
        if index > MAX_ROWS:
            raise ValueError('CSV exceeds 10,000 row limit')
        try:
            values = [float(row[k]) for k in FIELDS[1:]]
            if not all(math.isfinite(v) for v in values):
                raise ValueError('non-finite number')
            voltage, current, temp, soc = values
            if not (0 <= voltage <= 1000 and -2000 <= current <= 2000 and -80 <= temp <= 200 and 0 <= soc <= 100):
                raise ValueError('out of plausible demo range')
            stamp = row['timestamp'].strip()
            if not stamp or len(stamp) > 80:
                raise ValueError('invalid timestamp')
            rows.append(Sample(stamp, *values))
        except (TypeError, KeyError, ValueError) as exc:
            raise ValueError(f'Invalid row {index}: {exc}') from exc
    if not rows:
        raise ValueError('CSV has no observations')
    return rows


def analyze(samples: list[Sample]) -> dict:
    if not samples:
        raise ValueError('No samples')
    events = []
    for i, sample in enumerate(samples):
        reasons = []
        if sample.temperature_c >= 60:
            reasons.append('Temperature at or above 60°C (illustrative critical threshold).')
        elif sample.temperature_c >= 45:
            reasons.append('Temperature at or above 45°C (illustrative warning threshold).')
        if sample.soc_pct <= 10:
            reasons.append('State of charge at or below 10%.')
        if i:
            previous = samples[i - 1]
            if sample.temperature_c - previous.temperature_c >= 8:
                reasons.append('Temperature increased by at least 8°C since previous sample; sampling interval is not verified.')
            if previous.voltage_v > 0 and (previous.voltage_v - sample.voltage_v) / previous.voltage_v >= 0.12:
                reasons.append('Voltage dropped at least 12% since previous sample.')
        if reasons:
            critical = sample.temperature_c >= 60
            events.append({'index': i, 'timestamp': sample.timestamp, 'severity': 'critical' if critical else 'warning', 'reasons': reasons})
    severity = 'critical' if any(e['severity'] == 'critical' for e in events) else ('warning' if events else 'normal')
    explanation = {
        'normal': 'No configured demo thresholds were crossed. This does not prove battery safety or health.',
        'warning': 'One or more telemetry rules were triggered. Review the flagged samples and verify sensor readings.',
        'critical': 'A high-temperature demo threshold was crossed. Stop the demonstration and seek qualified review for real equipment.'
    }[severity]
    return {'status': severity, 'explanation': explanation, 'sample_count': len(samples), 'event_count': len(events),
            'events': events[-100:], 'latest': asdict(samples[-1]),
            'series': [asdict(s) for s in samples[-500:]],
            'method': 'Transparent threshold and adjacent-sample rules; no trained AI model or NPU inference.'}
