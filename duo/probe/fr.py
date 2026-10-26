import sys,json,urllib.request
sys.path.insert(0,''+__import__('os').path.dirname(__import__('os').path.abspath(__file__))+'/../driver'); import duo,orkey
m=sys.argv[1]; specs=duo.tool_specs(True)
schema='\n'.join(f'- {n}: {d} args={json.dumps(a)}' for n,d,a in specs)
u='\n'.join([f'Task: {duo.TASK}','','Tools available (call by name):',schema,'','Turn 1 of 8.',duo.REPLY_FORMAT])
body={'model':m,'temperature':0.7,'max_tokens':int(sys.argv[2]),'usage':{'include':True},'seed':1010,'messages':[{'role':'system','content':duo.system_prompt('A','B',True)},{'role':'user','content':u}]}
r=json.load(urllib.request.urlopen(urllib.request.Request('https://openrouter.ai/api/v1/chat/completions',json.dumps(body).encode(),{'Authorization':'Bearer '+orkey.key(),'Content-Type':'application/json'}),timeout=300))
c=r['choices'][0]; print(m,sys.argv[2],c.get('finish_reason'),c.get('native_finish_reason'),json.dumps(r.get('usage'))[:300],repr((c['message'].get('content') or '')[:120]))
