"""Measure CPU inference latency and process memory; never label these NPU measurements."""
import argparse,json,platform,statistics,time,tracemalloc
import torch
from ml.model import BatteryNet

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--iterations',type=int,default=300);ap.add_argument('--out',default='reports/cpu_benchmark.json');a=ap.parse_args()
    model=BatteryNet().eval();x=torch.zeros(1,8,4)
    for _ in range(30):model(x)
    tracemalloc.start(); samples=[]
    with torch.no_grad():
        for _ in range(a.iterations):
            t=time.perf_counter_ns();model(x);samples.append((time.perf_counter_ns()-t)/1e6)
    current,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
    result={'backend':'PyTorch CPU only','device':platform.platform(),'iterations':a.iterations,
            'median_ms':statistics.median(samples),'p95_ms':sorted(samples)[int(.95*(len(samples)-1))],
            'python_tracemalloc_peak_bytes':peak,'memory_note':'tracemalloc excludes native PyTorch allocator memory',
            'npu_verified':False}
    from pathlib import Path
    p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
