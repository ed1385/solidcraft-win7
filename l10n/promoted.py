import re,json
R='/home/claude/src/solidcraft-0.18.2/crates/ui-egui/src/workspace.rs'
s=open(R).read()
consts={m.group(1):re.findall(r'"([^"]+)"',m.group(2)) for m in re.finditer(r'const (\w+): &\[&str\] = &\[(.*?)\];',s,re.S)}
body=s[s.index('pub const SECTIONS'):]; body=body[:body.index('];\n')]
secs=[]
for m in re.finditer(r'Section\s*\{(.*?)\}',body,re.S):
    b=m.group(1)
    tab=re.search(r'tab:\s*"([^"]+)"',b).group(1); pan=re.search(r'panel:\s*"([^"]+)"',b).group(1)
    pro=int(re.search(r'promoted:\s*(\d+)',b).group(1))
    im=re.search(r'ids:\s*(&\[(.*?)\]|(\w+))',b,re.S)
    ids=re.findall(r'"([^"]+)"',im.group(2)) if im.group(2) is not None else consts.get(im.group(3),[])
    secs.append((tab,pan,pro,ids))
json.dump(secs,open('/home/claude/secs.json','w'))
prom=[i for t,p,n,ids in secs for i in ids[:n]]
print(len(secs),len(prom)); print(sorted({t for t,*_ in secs})); print(sorted({p for _,p,*_ in secs}))
print(sum(1 for t,p,n,ids in secs if len(ids)<n),'sections short of ids')
