#!/usr/bin/env python3
"""AMEND-1 driver: runs unmodified run_portable.py one seed at a time with a budget gate."""
import os,sys,subprocess,time,datetime,glob
sys.path.insert(0,os.path.dirname(__file__)); import orkey
ROOT=os.environ.get('LP_ROOT',os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PKG=ROOT+'/pkg/limit-probe-xfam'
leg=sys.argv[1]
CFG={'grok':('x-ai/grok-4.3','grok-4.3',1.00),'muse':('meta/muse-spark-1.3','muse-spark-1.3',1.40)}
model,label,reserve=CFG[leg]; FLOOR=0.60
out=f'{ROOT}/runs/{leg}/out-{label}'; logf=open(f'{ROOT}/runs/{leg}/driver.log','a')
def log(m):
    logf.write(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ ')+m+'\n'); logf.flush()
def grok_left():
    return 5-len(glob.glob(f'{ROOT}/runs/grok/out-grok-4.3/units/*/DONE'))
env=dict(os.environ,XFAM_BACKEND='openai',XFAM_BASE_URL='https://openrouter.ai/api/v1',XFAM_MODEL=model,XFAM_API_KEY=orkey.key())
for seed in range(1,6):
    if os.path.exists(f'{out}/units/{label}-s{seed}/DONE'): continue
    if datetime.datetime.utcnow()>=datetime.datetime(2026,10,25,11,40): log(f'CUTOFF: not starting s{seed} (12:00Z rule)'); break
    while True:
        try: rem=orkey.remaining(); break
        except Exception as e: log(f'key check failed {e}; retry 30s'); time.sleep(30)
    need=FLOOR+reserve+(reserve*0 if leg=='grok' else 1.00*grok_left())
    if rem<need: log(f'BUDGET STOP before s{seed}: remaining {rem:.3f} < need {need:.2f}'); break
    log(f'start s{seed} remaining {rem:.3f}')
    p=subprocess.run(['nice','-n','19',sys.executable,'run_portable.py','--label',label,'--out',out,'--seeds',str(seed)],cwd=PKG,env=env,capture_output=True,text=True)
    log(f's{seed} rc={p.returncode} stdout={p.stdout.strip()[-80:]} stderr_tail={p.stderr.strip()[-300:]!r}')
    if not os.path.exists(f'{out}/units/{label}-s{seed}/DONE'): log('unit not DONE, stopping'); break
log(f'END remaining {orkey.remaining():.3f}')
