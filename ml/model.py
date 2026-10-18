import torch
from torch import nn

class BatteryNet(nn.Module):
    """Small dense binary classifier; input (batch,8,4), output raw logits."""
    def __init__(self):
        super().__init__()
        self.net=nn.Sequential(nn.Flatten(), nn.Linear(32,32), nn.ReLU(), nn.Linear(32,16), nn.ReLU(), nn.Linear(16,1))
    def forward(self, x):
        return self.net(x).squeeze(-1)
