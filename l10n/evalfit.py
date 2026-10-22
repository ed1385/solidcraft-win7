import re,json,sys
sys.path.insert(0,'/home/claude'); from measure import *
import uharfbuzz as hb
fb=hb.Font(face); fb.set_variations({'wght':600})
def wb(t,size):
    buf=hb.Buffer(); buf.add_str(t); buf.guess_segment_properties(); hb.shape(fb,buf,{'kern':True})
    return sum(p.x_advance for p in buf.glyph_positions)/UPEM*size
R='/home/claude/src/solidcraft-0.18.2/'
en=json.load(open(R+'assets/locales/en.json'))
ru=json.load(open(sys.argv[1]))
ids={}
for k in sorted(en):
    if '{' not in en[k]: ids[en[k]]=k
def key(t): return ids.get(t,t)
def tr(t): k=key(t); return ru.get(k,en.get(k,t))
cmds={c[0]:c for c in json.load(open('cmds.json'))['cmds']}
# all command labels (including no-tab)
import glob
labels={}
for f in glob.glob(R+'crates/engine/src/**/*.rs',recursive=True):
    for m in re.finditer(r'CommandSpec::new\(\s*"([^"]+)",\s*"([^"]+)"',open(f).read()): labels[m.group(1)]=m.group(2)
secs=json.load(open('secs.json'))
def btnw(lbl):
    lines=ribbon_lines(lbl); return min(max(max(w(l,12) for l in lines)+10,54),96)
out={'buttons':[],'captions':[],'rows':[]}
used=set()
for tab,pan,n,idl in secs:
    ws=[]
    for i in idl[:n]:
        if tab=='SKETCH' and pan=='CONSTRAIN' and i.startswith('sketch.constraint.') : continue
        l=labels.get(i,i); t=tr(l); used.add(key(l)); ws.append(btnw(t))
        if not ribbon_ok(t): out['buttons'].append((key(l),l,t,' / '.join(ribbon_lines(t))))
    pw=max(sum(ws)+3*(len(ws)-1)+8,72) if ws else 72
    cap=tr(pan); cap=' '.join(x[:1].upper()+x[1:].lower() for x in cap.split())
    room=pw-8-12
    used.add(key(pan))
    if wb(cap,11.5)>room: out['captions'].append((key(pan),pan,cap,round(wb(cap,11.5)),round(room)))
for k,v in en.items():
    if k in used or '{' in v or k not in ru: continue
    if len(v)>40 or re.search(r'[.!?:;]\s|\.$',v): continue
    if w(v,12.5)<=108 and w(ru[k],12.5)>125: out['rows'].append((k,v,ru[k],round(w(ru[k],12.5))))
json.dump(out,open('fit.json','w'),ensure_ascii=False,indent=0)
print({k:len(v) for k,v in out.items()})
