#!/usr/bin/env python3
"""Driver for limit-probe-duo (PREREG-DUO.md). Usage: drive.py [--n N] MODEL [MODEL ...]
One thread per model; seed 1 (4 conds) serially, then DUO_WORKERS episodes in parallel. Resumable: skips ids already
in runs/<label>/episodes.jsonl. Stop rules per PREREG-DUO.md: budget floor, wall-clock cutoff, admission gate, per-model cap."""
import os, sys, json, datetime, time, threading, concurrent.futures as cf
sys.path.insert(0, os.path.dirname(__file__)); import orkey, duo
ROOT = __import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__)))
FLOOR = float(os.environ.get('DUO_FLOOR', '3.00')); CUTOFF = datetime.datetime(2026, 10, 26, 9, 30)
PER_MODEL_CAP = float(os.environ.get('DUO_MODEL_CAP', '6.00')); WORKERS = int(os.environ.get('DUO_WORKERS', '3')); STOP = threading.Event(); LOCK = threading.Lock()
def leg(model, n):
    lab = model.split('/')[1]; d = f'{ROOT}/runs/{lab}'; os.makedirs(d, exist_ok=True); fn = f'{d}/episodes.jsonl'
    done = set(); spent = 0.0
    if os.path.exists(fn):
        for l in open(fn): r = json.loads(l); done.add(r['id']); spent += r['agent_cost'] + r['judge_cost']
    lf = open(f'{d}/driver.log', 'a')
    def log(m): lf.write(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ ') + m + '\n'); lf.flush()
    def one(seed, cond):
        nonlocal spent
        eid = f'{lab}:{cond}:s{seed}'
        if eid in done: return True
        if STOP.is_set(): log('global STOP'); return False
        if datetime.datetime.utcnow() >= CUTOFF: log('CUTOFF'); return False
        if spent >= PER_MODEL_CAP: log(f'MODEL CAP {spent:.3f}'); return False
        with LOCK:
            try: rem = orkey.remaining()
            except Exception as e: log(f'key check failed {e}'); return False
            if rem < FLOOR: log(f'BUDGET STOP remaining {rem:.3f} < {FLOOR}'); STOP.set(); return False
        ep = None
        for att in range(3):  # ADDENDUM-1: transport failure -> rerun the whole episode (outcome never inspected)
            try: ep = duo.run_episode(model, cond, seed); ep['judges'], ep['judge_cost'] = duo.judge(ep); break
            except duo.ApiError as x: log(f'{eid} api_error attempt {att+1}: {x}')
        if ep is None:
            with LOCK, open(fn, 'a') as f: f.write(json.dumps(dict(id=eid, model=model, cond=cond, seed=seed, api_error=True, agent_cost=0, judge_cost=0)) + '\n')
            return True
        with LOCK:
            spent += ep['agent_cost'] + ep['judge_cost']
            with open(fn, 'a') as f: f.write(json.dumps(ep) + '\n')
        log(f"{eid} status={ep['status']} paid={ep['label']['paid_vs_invoice']} joint={ep['label']['joint_overspend']} cost={ep['agent_cost']+ep['judge_cost']:.4f}")
        return True
    for cond in duo.CONDS: one(1, cond)  # seed 1 serially, then admission gate
    eps = [r for r in map(json.loads, open(fn)) if r['seed'] == 1 and not r.get('api_error')] if os.path.exists(fn) else []
    un = sum(s == 'unparseable' for e in eps for s in e['status'].values())
    log(f'admission s1: agent-episodes={2*len(eps)} unparseable={un}')
    if not eps or un > len(eps): log('DROP: admission gate failed'); return
    with cf.ThreadPoolExecutor(WORKERS) as ex:
        list(ex.map(lambda sc: one(*sc), [(s, c) for s in range(2, n + 1) for c in duo.CONDS]))
    log(f'END spent {spent:.3f}')
if __name__ == '__main__':
    a = sys.argv[1:]; n = 25
    if a[:1] == ['--n']: n = int(a[1]); a = a[2:]
    ts = [threading.Thread(target=leg, args=(m, n)) for m in a]
    [t.start() for t in ts]; [t.join() for t in ts]
