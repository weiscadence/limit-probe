import json,os,re,sys,urllib.request
def key():
    return os.environ['OPENROUTER_API_KEY']
def remaining():
    r=urllib.request.urlopen(urllib.request.Request('https://openrouter.ai/api/v1/key',headers={'Authorization':'Bearer '+key()}),timeout=30)
    return float(json.load(r)['data']['limit_remaining'])
if __name__=='__main__':
    print(key() if sys.argv[1:]==['key'] else remaining())
