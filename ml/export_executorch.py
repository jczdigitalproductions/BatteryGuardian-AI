"""Portable ExecuTorch export. Qualcomm QNN delegation is a separate vendor-specific step."""
import argparse
from pathlib import Path
import torch
from ml.model import BatteryNet

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--checkpoint',default='artifacts/battery_model.pt');ap.add_argument('--out',default='artifacts/battery_model.pte');a=ap.parse_args()
    try:
        from executorch.exir import to_edge
    except ImportError as exc:
        raise SystemExit('ExecuTorch is not installed in this environment. See docs/DEPLOYMENT.md') from exc
    model=BatteryNet().eval()
    model.load_state_dict(torch.load(a.checkpoint,map_location='cpu',weights_only=True)['state_dict'])
    exported=torch.export.export(model,(torch.zeros(1,8,4),))
    program=to_edge(exported).to_executorch()
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_bytes(program.buffer)
    print('Portable .pte exported. This is NOT Qualcomm QNN delegated and does NOT prove NPU execution:',a.out)
if __name__=='__main__':main()
