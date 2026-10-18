# Offline acceptance checklist

- [ ] Disable all network adapters and restart app
- [ ] Open http://127.0.0.1:8765 and load sample CSV
- [ ] Run `python -m ml.infer` through Python integration (CPU baseline)
- [ ] Record model file hash, platform version and battery dataset provenance
- [ ] Verify safety rules still trigger with no ML checkpoint present
- [ ] Capture measured process working set and energy impact on target device
- [ ] Capture NPU execution traces, not just claimed delegate selection
