"""WCAG contrast for every text/background token pair the page uses, in light and dark. Fails below 4.5:1 (text) / 3:1 (UI)."""
import re, sys
t = open(sys.argv[1]).read()
def block(sel_rx):
    m = re.search(sel_rx, t, re.S); return dict(re.findall(r"--([\w-]+):(#[0-9a-fA-F]{6})", m.group(1)))
light = block(r":root\{(.*?)\}"); dark = dict(light); dark.update(block(r':root\[data-theme="dark"\]\{(.*?)\}'))
def L(h):
    c = [int(h[i:i+2], 16) / 255 for i in (1, 3, 5)]; c = [x / 12.92 if x <= .03928 else ((x + .055) / 1.055) ** 2.4 for x in c]
    return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]
def cr(a, b): a, b = L(a), L(b); return (max(a, b) + .05) / (min(a, b) + .05)
TEXT = [("fg","bg"),("fg","surface"),("muted","surface"),("muted","bg"),("faint","surface"),("faint","bg"),("accent","surface"),("accent","bg"),("accent-ink","accent"),
        ("ok","ok-soft"),("info","info-soft"),("warn","warn-soft"),("bad","bad-soft"),("muted","mute-soft"),("bad","surface"),("info","surface"),("warn","surface"),("cons","surface"),("fg","accent-soft"),("muted","sunk"),("bg","fg"),("cons","mute-soft"),("muted","bg")]
HUES = ["blue","orange","aqua","yellow","magenta","green","violet","red","slate"]
TEXT += [(h+"-ink","surface") for h in HUES] + [(h+"-ink","bg") for h in HUES] + [(h+"-ink",h+"-soft") for h in HUES] + [("fg",h+"-soft") for h in HUES] + [(h+"-on",h+"-ink") for h in HUES] + [("muted",h+"-soft") for h in HUES]
TEXT += [] + [("fg","sunk"),("fg","warn-soft"),("fg","ok-soft"),("muted","sunk"),("fg","info-soft")]  # 7.1: tile, block and chip text
UI = [("line-strong","surface"),("line-strong","bg"),("line-strong","sunk"),("accent","surface")] + [(h,"surface") for h in HUES] + [(k,"surface") for k in ("w1","w2","w3","dec","cons","keep","arch","del")]
fail = 0
for theme, P in (("light", light), ("dark", dark)):
    for a, b in TEXT:
        r = cr(P[a], P[b]); ok = r >= 4.5; fail += not ok
        if not ok: print(f"FAIL {theme} text {a} on {b}: {r:.2f}")
    # heat cells: fg text on accent mixed at up to 35% over the surface (D14)
    mix = lambda a, b, w: "#" + "".join(f"{round(int(a[i:i+2],16)*w + int(b[i:i+2],16)*(1-w)):02x}" for i in (1, 3, 5))
    for wgt in (0.35, 0.2):
        r = cr(P["fg"], mix(P["accent"], P["surface"], wgt)); ok = r >= 4.5; fail += not ok
        if not ok: print(f"FAIL {theme} heat {wgt}: {r:.2f}")
    for a, b in UI:
        r = cr(P[a], P[b]); ok = r >= 3; fail += not ok
        if not ok: print(f"FAIL {theme} UI {a} on {b}: {r:.2f}")
    print(f"{theme}: checked {len(TEXT)} text pairs, {len(UI)} UI pairs and heat-cell text")
if len(sys.argv) > 2:
    import json; json.dump({"T-CON-01": {"status": "pass" if not fail else "fail", "text": f"text contrast at least 4.5:1 for {len(TEXT)} token pairs (including every hue ink and tint) and 3:1 for {len(UI)} borders, marks and diagram strokes, light and dark", "guards": "A-1, A-2, A-3, D14", "detail": f"{fail} failures"}}, open(sys.argv[2], "w"))
sys.exit(1 if fail else 0)
