import json,sys,time,urllib.request,os
sys.path.insert(0,os.path.dirname(__file__)); import orkey
out={}
for m in sys.argv[1:]:
    body=json.dumps({"model":m,"messages":[{"role":"system","content":"You are an agent. Reply ONLY with a JSON object."},{"role":"user","content":'Reply with exactly {"final": "ok"}'}]}).encode()
    t=time.time()
    try:
        d=json.load(urllib.request.urlopen(urllib.request.Request('https://openrouter.ai/api/v1/chat/completions',data=body,headers={'Content-Type':'application/json','Authorization':'Bearer '+orkey.key()}),timeout=120))
        c=d['choices'][0]['message']['content'] or ''
        try: ok=json.loads(c.strip().strip('`').removeprefix('json').strip()).get('final')=='ok'
        except Exception: ok=False
        out[m]={'model':d.get('model'),'content':c[:200],'parse_ok':ok,'usage':d.get('usage'),'sec':round(time.time()-t,1)}
    except Exception as e: out[m]={'error':str(e)[:300]}
    print(m,{k:out[m].get(k) for k in ('model','content','parse_ok','error')},(out[m].get('usage') or {}).get('cost'))
json.dump(out,open(os.path.dirname(__file__)+'/../runs/smoke/smoke-amend2.json','w'),indent=1)
