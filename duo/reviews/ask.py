import sys,os,json
sys.path.insert(0,''+__import__('os').path.dirname(__import__('os').path.abspath(__file__))+'/../driver'); import duo
R=__import__('os').path.dirname(__import__('os').path.abspath(__file__))+'/../'
ex=json.loads(open(R+'runs/mistral-small-2603/episodes.jsonl').readline())
sample=duo.judge_prompts(ex)
q=f"""You are a hostile peer reviewer for an AI-safety sprint paper (Apart AI Collusion, track: multi-agent collusion monitoring). Review the TEST DESIGN below BEFORE the full run. Be blunt and specific; cite lines. Cover:
1. Circularity between the ground-truth labeller and any monitor (is any result true by construction?).
2. Whether agent prompts instruct, suggest, or leak collusion/splitting (or conversely make it impossible).
3. Whether the no-channel control is fair.
4. Judge-prompt bias (e.g., the judge question names the exact bypass pattern; leading examples).
5. Anything else making the hypotheses true or false by construction; statistical power; exclusion rules.
6. Pilot fact: in a 100-episode Mistral pilot, 27/100 episodes were excluded as 'unparseable'; on inspection ALL 36 unparseable agent replies were 'ERROR HTTP Error 429: Too Many Requests' (API rate-limit), not model output. Pilot results: 5 joint-only overspends (all chan_offline), per-agent rule 1/5, combined-logs judge 5/5, false alarms 0/59. How should this be handled?
End with a ranked list of MUST-FIX (before running) vs SHOULD-NOTE (in paper). Under 900 words.

=== PREREG-DUO.md ===
{open(R+'PREREG-DUO.md').read()}
=== driver/duo.py (environment, prompts, labeller, monitors, judges) ===
{open(R+'driver/duo.py').read()}
=== driver/drive.py ===
{open(R+'driver/drive.py').read()}
=== Example rendered judge prompt (combined_logs_judge, one pilot episode) ===
{sample['combined_logs_judge']}
"""
m=sys.argv[1]
txt,c=duo.chat(m,[{'role':'user','content':q}],0.3,max_tokens=6000)
open(R+'reviews/'+m.replace('/','_')+'.md','w').write(f'# review by {m} (cost {c})\n\n'+txt)
print(m,c,len(txt))
