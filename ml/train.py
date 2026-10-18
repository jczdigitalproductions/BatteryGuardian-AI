"""Train on synthetic demo windows or on user-provided labeled SESSION CSVs."""
import argparse, json, random
from pathlib import Path
import numpy as np
import torch
from ml.model import BatteryNet
from ml.synthetic import generate
from ml.features import load_labeled_csv

def metrics(y, pred):
    y=np.asarray(y); pred=np.asarray(pred)
    tp=int(((y==1)&(pred==1)).sum()); tn=int(((y==0)&(pred==0)).sum())
    fp=int(((y==0)&(pred==1)).sum()); fn=int(((y==1)&(pred==0)).sum())
    return {'TP':tp,'TN':tn,'FP':fp,'FN':fn,'false_positive_rate':fp/max(fp+tn,1),
            'false_negative_rate':fn/max(fn+tp,1),'precision':tp/max(tp+fp,1),
            'recall':tp/max(tp+fn,1),'accuracy':(tp+tn)/max(len(y),1)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--train-files',nargs='+'); ap.add_argument('--val-files',nargs='+'); ap.add_argument('--test-files',nargs='+')
    ap.add_argument('--out',default='artifacts'); ap.add_argument('--epochs',type=int,default=25)
    args=ap.parse_args()
    supplied=[args.train_files,args.val_files,args.test_files]
    if any(supplied) and not all(supplied):
        ap.error('Supply all three disjoint session file groups')
    random.seed(17); np.random.seed(17); torch.manual_seed(17)
    if all(supplied):
        paths=[set(map(str, group)) for group in supplied]
        if any(paths[i]&paths[j] for i in range(3) for j in range(i+1,3)):
            ap.error('A session file cannot appear in multiple splits')
        def load(group):
            pairs=[load_labeled_csv(f) for f in group]
            return np.concatenate([x for x,_ in pairs]),np.concatenate([y for _,y in pairs])
        datasets=[load(group) for group in supplied]
        source='user-provided labeled session CSVs (not independently validated)'
    else:
        x,y=generate()
        datasets=[(x[:720],y[:720]),(x[720:960],y[720:960]),(x[960:],y[960:])]
        source='synthetic demonstration only; no real-world fault detection claim'
    model=BatteryNet()
    opt=torch.optim.Adam(model.parameters(),lr=.003)
    criterion=torch.nn.BCEWithLogitsLoss()
    xtr,ytr=datasets[0]
    for epoch in range(args.epochs):
        model.train()
        order=np.random.permutation(len(xtr))
        for ids in np.array_split(order,max(1,int(np.ceil(len(order)/64)))):
            inputs=torch.from_numpy(xtr[ids]); targets=torch.from_numpy(ytr[ids].astype('float32'))
            opt.zero_grad(); loss=criterion(model(inputs),targets);loss.backward();opt.step()
    model.eval()
    def probs(x):
        with torch.no_grad():return torch.sigmoid(model(torch.from_numpy(x))).numpy()
    xv,yv=datasets[1]
    pv=probs(xv)
    thresholds=np.arange(.1,.91,.05)
    # Choose threshold using validation only; target <=5% false-positive rate if possible.
    candidates=[(float(t),metrics(yv,pv>=t)) for t in thresholds]
    valid=[c for c in candidates if c[1]['false_positive_rate']<=.05]
    threshold=max(valid or candidates,key=lambda c:(c[1]['recall'],-c[1]['false_positive_rate']))[0]
    xt,yt=datasets[2];pt=probs(xt)
    result={'data_source':source,'threshold':threshold,'train_windows':len(xtr),'validation_windows':len(xv),
            'test_windows':len(xt),'validation':metrics(yv,pv>=threshold),'test':metrics(yt,pt>=threshold),
            'limitations':['Synthetic patterns are not representative of physical battery faults',
                           'Session-level leakage and distribution shift must be assessed on real data',
                           'This model is not a battery management system or safety interlock']}
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    torch.save({'state_dict':model.state_dict(),'threshold':threshold,'source':source},out/'battery_model.pt')
    (out/'evaluation.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
