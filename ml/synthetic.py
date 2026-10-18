"""Synthetic, nonphysical demonstration data; NEVER claim clinical/industrial validation."""
import numpy as np

def generate(n=1200, seed=2026):
    rng=np.random.default_rng(seed)
    x=np.empty((n,8,4),dtype=np.float32)
    y=np.zeros(n,dtype=np.int64)
    for i in range(n):
        fault=int(i%2==0)
        temp=30+rng.normal(0,2,8)
        voltage=3.75+rng.normal(0,.035,8)
        current=2+rng.normal(0,.3,8)
        soc=65-np.arange(8)*.3+rng.normal(0,.2,8)
        if fault:
            # Independent fault patterns; labels deliberately correlated with faults.
            kind=i%3
            if kind==0: temp+=np.linspace(0,32,8)
            elif kind==1: voltage-=np.linspace(0,.9,8)
            else: current+=np.linspace(0,24,8)
        raw=np.stack([voltage,current,temp,soc],axis=-1).astype(np.float32)
        from ml.features import MEAN,SCALE
        x[i]=np.clip((raw-MEAN)/SCALE,-8,8)
        y[i]=fault
    order=rng.permutation(n)
    return x[order],y[order]
