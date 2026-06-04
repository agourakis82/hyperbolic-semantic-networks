import os,sys,json,numpy as np,pandas as pd,networkx as nx,contextlib,io
import powerlaw
def degseq(pre):
    G=nx.from_pandas_edgelist(pd.read_csv(f"data/processed/{pre}_edges_FINAL.csv"),'source','target')
    G=G.subgraph(max(nx.connected_components(G),key=len)).copy()
    return np.array([d for _,d in G.degree()])
def quiet_fit(data):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return powerlaw.Fit(data, discrete=True)
def clauset_p(data, n_boot=500, seed=20260604):
    rng=np.random.RandomState(seed)
    fit=quiet_fit(data); pl=fit.power_law
    alpha,xmin,Dobs=pl.alpha,pl.xmin,pl.D
    data=np.asarray(data); n=len(data)
    below=data[data<xmin]; ntail=int((data>=xmin).sum()); ptail=ntail/n
    ge=0
    for _ in range(n_boot):
        k=rng.binomial(n,ptail); nb=n-k
        st=pl.generate_random(k) if k>0 else np.array([])
        sb=rng.choice(below,nb,replace=True) if (nb>0 and len(below)>0) else np.array([])
        synth=np.concatenate([np.asarray(st),np.asarray(sb)])
        try: Ds=quiet_fit(synth).power_law.D
        except Exception: continue
        if Ds>=Dobs: ge+=1
    return dict(alpha=round(float(alpha),3),xmin=float(xmin),D=round(float(Dobs),4),p=round(ge/n_boot,3),n_boot=n_boot,plausible_powerlaw=bool(ge/n_boot>=0.1))
out={}
for lang,pre in [("EN","english"),("ES","spanish"),("ZH","chinese"),("NL","dutch")]:
    out[lang]=clauset_p(degseq(pre))
    print(lang, out[lang], flush=True)
json.dump(out,open("/tmp/alpha_gof.json","w"),indent=2)
print("DONE")
