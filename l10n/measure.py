import uharfbuzz as hb, json
FONT='/home/claude/src/solidcraft-0.18.2/assets/fonts/ibm-plex-sans/IBMPlexSans-Variable.ttf'
blob=hb.Blob.from_file_path(FONT); face=hb.Face(blob); font=hb.Font(face); UPEM=face.upem
font.set_variations({'wght':400})
cache={}
def w(text,size):
    if text not in cache:
        buf=hb.Buffer(); buf.add_str(text); buf.guess_segment_properties(); hb.shape(font,buf,{'kern':True})
        cache[text]=sum(p.x_advance for p in buf.glyph_positions)/UPEM
    return cache[text]*size
def ribbon_lines(label,width=86,size=12):
    label=' '.join(label.split()); end=0; toks=[]
    import re
    toks=re.findall(r'[^\s/]*[\s/]|[^\s/]+$',label)
    for t in toks:
        nxt=end+len(t)
        if end>0 and w(label[:nxt].strip(),size)>width: break
        end=nxt
    lines=[label[:end].strip()]; rest=label[end:].strip()
    if rest: lines.append(rest)
    return lines
def ribbon_ok(label):
    return all(w(l,12)<=86 for l in ribbon_lines(label))
def row_ok(label): return w(label,12.5)<=125
