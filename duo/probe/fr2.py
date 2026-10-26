import sys,json,urllib.request
sys.path.insert(0,''+__import__('os').path.dirname(__import__('os').path.abspath(__file__))+'/../driver'); import duo,orkey
m,lab,mt=sys.argv[1],sys.argv[2],int(sys.argv[3])
for l in open(f'runs-truncated/{lab}/episodes.jsonl'):
    e=json.loads(l)
    if e['cond'].startswith('nochan') and 'unparseable' in e['status'].values(): break
n=[k for k,v in e['status'].items() if v=='unparseable'][0]; bad=[x for x in e['raw'] if x['agent']==n and x['parsed'] is None][0]
trans=[f"[{x['turn']}] call {x['parsed']['tool']}({json.dumps(x['parsed'].get('args',{}))}) -> {json.dumps(le['result'])}" for x,le in zip([x for x in e['raw'] if x['agent']==n and x['parsed'] and 'tool' in x['parsed']], e['logs'][n])]
specs=duo.tool_specs(False); schema='\n'.join(f'- {a}: {d} args={json.dumps(b)}' for a,d,b in specs)
u='\n'.join([f'Task: {duo.TASK}','','Tools available (call by name):',schema,'','Transcript so far:']+trans+['',f"Turn {bad['turn']} of 8.",duo.REPLY_FORMAT])
body={'model':m,'temperature':0.7,'max_tokens':mt,'usage':{'include':True},'seed':e['seed']*1000+bad['turn']*10+(n=='B'),'reasoning':{'effort':'low'},'messages':[{'role':'system','content':duo.system_prompt(n,'B' if n=='A' else 'A',False)},{'role':'user','content':u}]}
r=json.load(urllib.request.urlopen(urllib.request.Request('https://openrouter.ai/api/v1/chat/completions',json.dumps(body).encode(),{'Authorization':'Bearer '+orkey.key(),'Content-Type':'application/json'}),timeout=600))
c=r['choices'][0]; us=r.get('usage',{})
print(m,mt,e['id'],c.get('finish_reason'),'completion',us.get('completion_tokens'),'reasoning',(us.get('completion_tokens_details') or {}).get('reasoning_tokens'),'rlen',len(c['message'].get('reasoning') or ''),repr((c['message'].get('content') or '')[:100]))
