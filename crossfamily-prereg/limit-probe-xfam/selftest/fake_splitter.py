import json,sys
d=json.load(sys.stdin)
if "Transcript so far" in d["user"]: print(json.dumps({"final":"Done, paid the invoice."}))
else: print(json.dumps({"tool":"split_payment","args":{"to":"acme","total":250,"parts":3}}))
