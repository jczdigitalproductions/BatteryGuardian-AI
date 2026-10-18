"""Optional local PyTorch inference; deterministic safety rules remain independent."""
import numpy as np
import torch
from ml.features import windows_from_samples
from ml.model import BatteryNet

def infer(samples, checkpoint='artifacts/battery_model.pt'):
    ckpt=torch.load(checkpoint,map_location='cpu',weights_only=True)
    model=BatteryNet().eval();model.load_state_dict(ckpt['state_dict'])
    x=windows_from_samples(samples)
    with torch.no_grad():p=torch.sigmoid(model(torch.from_numpy(x))).numpy()
    return {'probability':float(p[-1]),'threshold':float(ckpt['threshold']),
            'flagged':bool(p[-1]>=ckpt['threshold']), 'model_source':ckpt['source'],
            'explanation':'Model score is statistical, not a diagnosis. Review temperature, voltage, current and deterministic safety alerts.',
            'runtime':'PyTorch CPU (no NPU verification)'}
