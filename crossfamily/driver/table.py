#!/usr/bin/env python3
"""Cross-family table straight from runs/*/result.json (produced by driver/score.py). No hand-copied numbers."""
import json,glob,os,sys
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTIER={'gpt-6-astra','grok-4.7','gpt-6-sol','kimi-k3.1-pro','deepseek-v4-pro','qwen3.8-max-0902','gemini-3.1-pro-preview'}
def unparse(d):
    live=un=0
    for f in glob.glob(f'{d}/out-*/units/*/report.json'):
        for e in json.load(open(f))['episodes']:
            if e['agent'].startswith('cli:'): live+=1; un+=e['status']=='unparseable'
    return un,live
rows=[]
for rj in sorted(glob.glob(f'{ROOT}/runs/*/result.json')):
    d=os.path.dirname(rj); r=json.load(open(rj)); s=r['sealed']; c=s['cells']
    label=list(c)[0].split('/')[0]
    D1=sum(v['D1'] for v in c.values()); D3=sum(v['D3'] for v in c.values()); n=sum(v['scored'] for v in c.values())
    fa=s['false_alarm']; rb=fa['rule-based (tool stream)']; fm=fa['summary-only (final message)']
    un,live=unparse(d)
    f=lambda x:f"{x['k']}/{x['n']} [{x['ci'][0]:.2f},{x['ci'][1]:.2f}]"
    rows.append((label in FRONTIER,label,f"{r['units_gates_ok']}/{r['units']}",f"{D1}/{n}",f"{D3}/{n}",f(rb),f(fm),f"{un}/{live}"))
print('| tier | model | units gates_ok | D1 bypass k/n | D3 k/n | rule-based (tool-log) FA [Wilson95] | final-message FA [Wilson95] | unparseable/live |')
print('|---|---|---|---|---|---|---|---|')
for t,*x in sorted(rows): print('| '+('frontier (AMEND-3, exploratory post-hoc)' if t else 'cheap (prereg, AMEND-1/2)')+' | '+' | '.join(x)+' |')
