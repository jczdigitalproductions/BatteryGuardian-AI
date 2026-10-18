import argparse
from pathlib import Path
import torch
from ml.model import BatteryNet

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--checkpoint',default='artifacts/battery_model.pt');ap.add_argument('--out',default='artifacts/battery_model.onnx');a=ap.parse_args()
    checkpoint=torch.load(a.checkpoint,map_location='cpu',weights_only=True)
    model=BatteryNet().eval();model.load_state_dict(checkpoint['state_dict'])
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    torch.onnx.export(model,torch.zeros(1,8,4),a.out,input_names=['telemetry'],output_names=['fault_logit'],opset_version=17,
                      dynamo=False,dynamic_axes={'telemetry':{0:'batch'},'fault_logit':{0:'batch'}})
    print('Exported',a.out,'; NPU execution NOT verified')
if __name__=='__main__':main()
