#!/usr/bin/env python3
"""AMEND-2 pre-registered: Fisher-Freeman-Halton (MC 200k, seed 20261025) on final-msg FA across families + Pearson chi2.
Usage: hetero.py name=k/n ...  (k = final-msg flags among live non-bypass scored, n = that count)"""
import sys,math,random
rows=[(a.split('=')[0],*map(int,a.split('=')[1].split('/'))) for a in sys.argv[1:]]
K=[r[1] for r in rows];N=[r[2] for r in rows];T=sum(N);F=sum(K)
def logp(ks): # log prob of table under hypergeometric (multivariate) null given margins
    return sum(math.lgamma(n+1)-math.lgamma(k+1)-math.lgamma(n-k+1) for k,n in zip(ks,N))-(math.lgamma(T+1)-math.lgamma(F+1)-math.lgamma(T-F+1))
def chi2(ks):
    s=0
    for k,n in zip(ks,N):
        e1=n*F/T;e0=n-e1
        s+=(k-e1)**2/e1+((n-k)-e0)**2/e0 if e1>0 and e0>0 else 0
    return s
obs=logp(K);rng=random.Random(20261025);R=200000;hit=0
pool=[1]*F+[0]*(T-F)
idx=[];c=0
for n in N: idx.append((c,c+n));c+=n
for _ in range(R):
    rng.shuffle(pool); ks=[sum(pool[a:b]) for a,b in idx]
    if logp(ks)<=obs+1e-9: hit+=1
x=chi2(K);df=len(rows)-1
# chi2 survival via regularized gamma
def gammaincc(s,x):
    # series for P then 1-P
    if x<s+1:
        t=1/s;tot=t;n=1
        while t>1e-15*tot: t*=x/(s+n);tot+=t;n+=1
        return 1-tot*math.exp(-x+s*math.log(x)-math.lgamma(s))
    b=x+1-s;c=1e300;d=1/b;h=d;i=1
    while True:
        an=-i*(i-s);b+=2;d=an*d+b;d=1/d if d else 1e300;c=b+an/c;de=d*c;h*=de;i+=1
        if abs(de-1)<1e-15: break
    return math.exp(-x+s*math.log(x)-math.lgamma(s))*h
print({'families':len(rows),'table':{r[0]:f'{r[1]}/{r[2]}' for r in rows},'ffh_mc_p':(hit+1)/(R+1),'mc_reps':R,'chi2':round(x,2),'df':df,'chi2_p':gammaincc(df/2,x/2)})
