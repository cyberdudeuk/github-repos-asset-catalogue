"""v6 colour system. Derives text-safe ink and tint for each categorical hue in both themes, then verifies every pair it will be used in.
Outputs v6/palette.json and v6/palette.css. Exit code 1 if any check fails (so the build stops)."""
import json,sys,os
H=os.path.dirname(os.path.abspath(__file__))
def hx(h): h=h.lstrip('#'); return [int(h[i:i+2],16)/255 for i in (0,2,4)]
def tohex(c): return '#'+''.join(f"{max(0,min(255,round(x*255))):02x}" for x in c)
def lin(x): return x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4
def lum(h): r,g,b=[lin(x) for x in hx(h)]; return .2126*r+.7152*g+.0722*b
def cr(a,b): la,lb=lum(a),lum(b); return (max(la,lb)+.05)/(min(la,lb)+.05)
def mix(a,b,t): A,B=hx(a),hx(b); return tohex([A[i]*(1-t)+B[i]*t for i in range(3)])
L_SURF,L_BG,L_SUNK="#ffffff","#f3f5f6","#e8ecee"; D_SURF,D_BG,D_SUNK="#162228","#0f171b","#1c2a31"
HUES=[("blue","#2a78d6","#3987e5"),("orange","#eb6834","#d95926"),("aqua","#1baf7a","#199e70"),("yellow","#eda100","#c98500"),
      ("magenta","#e87ba4","#d55181"),("green","#008300","#008300"),("violet","#6250d6","#9085e9"),("red","#e34948","#e66767"),("slate","#5f7079","#8a9da5")]
out={}; fails=[]
def chk(name,a,b,need):
    r=cr(a,b)
    if r<need: fails.append(f"{name} {a} on {b} = {r:.2f} < {need}")
    return round(r,2)
for name,lc,dc in HUES:
    # light ink: darken toward black until >=4.5 on white AND on its own tint
    lsoft=mix(lc,"#ffffff",.86); ink=lc; t=0
    while (cr(ink,L_SURF)<4.6 or cr(ink,lsoft)<4.6 or cr(ink,L_BG)<4.6) and t<1: t+=.02; ink=mix(lc,"#000000",t)
    # light mark: the hue itself if >=3:1 on white, else darken to 3:1
    mark=lc; t=0
    while cr(mark,L_SURF)<3.05 and t<1: t+=.02; mark=mix(lc,"#000000",t)
    # dark: tint and ink (lighten toward white)
    dsoft=mix(dc,D_SURF,.78); dink=dc; t=0
    while (cr(dink,D_SURF)<4.6 or cr(dink,dsoft)<4.6 or cr(dink,D_BG)<4.6) and t<1: t+=.02; dink=mix(dc,"#ffffff",t)
    dmark=dc; t=0
    while cr(dmark,D_SURF)<3.05 and t<1: t+=.02; dmark=mix(dc,"#ffffff",t)
    # text on solid ink background (hub banners): white on light ink; dark bg text on dark ink
    on_l="#ffffff"; on_d="#0f171b"
    out[name]=dict(light=dict(mark=mark,ink=ink,soft=lsoft,on=on_l),dark=dict(mark=dmark,ink=dink,soft=dsoft,on=on_d))
    o=out[name]; ratios={}
    for th,S,B,K in (("light",L_SURF,L_BG,L_SUNK),("dark",D_SURF,D_BG,D_SUNK)):
        v=o[th]
        ratios[th]=dict(ink_surface=chk(f"{name}/{th} ink",v["ink"],S,4.5),ink_bg=chk(f"{name}/{th} ink-bg",v["ink"],B,4.5),ink_soft=chk(f"{name}/{th} ink-soft",v["ink"],v["soft"],4.5),
                        on_ink=chk(f"{name}/{th} on-ink",v["on"],v["ink"],4.5),mark_surface=chk(f"{name}/{th} mark",v["mark"],S,3.0),fg_soft=chk(f"{name}/{th} fg-soft","#14232b" if th=="light" else "#e3ecef",v["soft"],4.5))
    o["ratios"]=ratios
# field borders and migration group fills (assessment fixes)
extra=dict(light={"line-strong":"#6f7f87","keep":"#76848b","arch":"#7d8b91","w2":"#2f7d89","w3":"#4f8a93"},
           dark={"line-strong":"#71868f","keep":"#7d8d94","arch":"#6f828b","w2":"#3f97a3","w3":"#4e8e98"})
for k,v in extra["light"].items(): chk("light "+k,v,L_SURF,3.0); chk("light-bg "+k,v,L_BG,3.0)
for k,v in extra["dark"].items(): chk("dark "+k,v,D_SURF,3.0); chk("dark-bg "+k,v,D_BG,3.0)
# negative test: the checker must reject the v5 field border and v5 lineage stroke
neg=[]; chk("NEG v5 line","#c9d2d7",L_SURF,3.0); chk("NEG v5 keep","#8b979d",L_SURF,3.0)
negf=[f for f in fails if f.startswith("NEG")]; fails=[f for f in fails if not f.startswith("NEG")]
ok_neg=len(negf)==2
json.dump(dict(hues=out,extra=extra,fails=fails,negative_test_rejects_v5=ok_neg,negatives=negf),open(f"{H}/palette.json","w"),indent=1)
def css(th):
    return "".join(f"--{n}:{out[n][th]['mark']};--{n}-ink:{out[n][th]['ink']};--{n}-soft:{out[n][th]['soft']};--{n}-on:{out[n][th]['on']};" for n,_,_ in HUES)+"".join(f"--{k}:{v};" for k,v in extra[th].items())
open(f"{H}/palette.css","w").write(json.dumps(dict(light=css("light"),dark=css("dark"))))
for n in out: print(n, out[n]["light"], out[n]["dark"])
print("fails:",fails); print("negative test rejects v5 colours:",ok_neg,negf)
sys.exit(1 if fails or not ok_neg else 0)
