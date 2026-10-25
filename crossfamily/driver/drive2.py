#!/usr/bin/env python3
"""AMEND-2 driver: queue of legs, each runs unmodified run_portable.py one seed at a time; floor gate per unit."""
import os,sys,subprocess,datetime,json,time
sys.path.insert(0,os.path.dirname(__file__)); import orkey
ROOT=os.environ.get('LP_ROOT',os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); PKG=ROOT+'/pkg/limit-probe-xfam'
FLOOR,RESERVE=0.75,0.40; CUTOFF=datetime.datetime(2026,10,25,17,30)
def run_leg(model):
    label=model.split('/')[1]; d=f'{ROOT}/runs/{label}'; os.makedirs(d,exist_ok=True); out=f'{d}/out-{label}'
    lf=open(f'{d}/driver.log','a')
    def log(m): lf.write(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ ')+m+'\n'); lf.flush()
    env=dict(os.environ,XFAM_BACKEND='openai',XFAM_BASE_URL='https://openrouter.ai/api/v1',XFAM_MODEL=model,XFAM_API_KEY=orkey.key())
    for seed in range(1,6):
        if os.path.exists(f'{out}/units/{label}-s{seed}/DONE'): continue
        if datetime.datetime.utcnow()>=CUTOFF: log(f'CUTOFF: not starting s{seed}'); return
        for _ in range(10):
            try: rem=orkey.remaining(); break
            except Exception as e: log(f'key check failed {e}'); time.sleep(30)
        else: log('key check failing, stop'); return 'STOPALL'
        if rem<FLOOR+RESERVE: log(f'BUDGET STOP before s{seed}: remaining {rem:.3f} < {FLOOR+RESERVE:.2f}'); return 'STOPALL'
        log(f'start s{seed} remaining {rem:.3f}')
        p=subprocess.run(['nice','-n','19',sys.executable,'run_portable.py','--label',label,'--out',out,'--seeds',str(seed)],cwd=PKG,env=env,capture_output=True,text=True)
        log(f's{seed} rc={p.returncode} stdout={p.stdout.strip()[-80:]} stderr_tail={p.stderr.strip()[-300:]!r}')
        if not os.path.exists(f'{out}/units/{label}-s{seed}/DONE'): log(f'DROP/STOP: unit s{seed} not DONE'); return
        if seed==1:
            r=json.load(open(f'{out}/units/{label}-s1/report.json'))
            live=[e for e in r['episodes'] if e['agent'].startswith('cli:')]; un=sum(e['status']=='unparseable' for e in live)
            gates=r['chain_ok'] and r['control']=='OK'
            log(f's1 admission: live={len(live)} unparseable={un} gates_ok={gates}')
            if not gates or un*2>len(live): log('DROP: AMEND-2 admission rule failed at s1'); return
    log(f'END remaining {orkey.remaining():.3f}')
for m in sys.argv[1:]:
    if run_leg(m)=='STOPALL': break
