"""
Builds the animated SVGs used in the profile README.

Edit the TEXT section below, then run:   python scripts/build_svgs.py
It rewrites assets/hero.svg, assets/terminal.svg and assets/footer.svg.

Everything is plain SVG + SMIL/CSS animation, so GitHub renders it with
no external service that could go down.
"""
from pathlib import Path
from xml.sax.saxutils import escape

# ---------------------------------------------------------------- TEXT ---
NAME_LINE = "I'm Youssef,"
ROLES = [
    "an AI Builder.",
    "a Frontend Developer.",
    "a Linux & Network tinkerer.",
    "a Digital Forensics nerd.",
    "a Data Analyst (in R).",
]
TAGLINE = "Frontend · Systems · Networks · Data · Security"
META = "📍 Kuala Lumpur    🎓 Asia Pacific University    💼 Frontend Dev @ BarqSec"
STATUS_PILL = "Open to work · internships & collaborations"
NODES = ["React", "Python", "Linux", "Cisco", "SQL", "AI"]

# terminal: ("cmd", text) is typed, ("out", [(text, color), ...]) appears
TERMINAL = [
    ("cmd", "whoami"),
    ("out", [("Youssef Ghazy", "#ffffff"), (" — IT student @ Asia Pacific University, Kuala Lumpur", "#a8a8a8")]),
    ("cmd", "cat current_role.txt"),
    ("out", [("Frontend Developer @ ", "#a8a8a8"), ("BarqSec", "#fe6060"), (" · clean, cross-browser interfaces", "#a8a8a8")]),
    ("cmd", "ls ~/achievements"),
    ("out", [("UMHackathon-2026_4th-runner-up/", "#ff8b72"), ("   16_certifications/", "#a8a8a8"), ("   12_projects/", "#a8a8a8")]),
    ("cmd", "echo $SPOKEN_LANGUAGES"),
    ("out", [("Arabic · English · French", "#a8a8a8")]),
    ("cmd", "./philosophy.sh"),
    ("out", [("from pixel to packet", "#fe6060"), (" — I like knowing how the whole system behaves.", "#a8a8a8")]),
]

# --------------------------------------------------------------- THEME ---
BG, ACCENT, ACCENT2, MUTED, FAINT = "#050505", "#fe6060", "#ff8b72", "#a8a8a8", "#747474"
SANS = "'Kumbh Sans','Segoe UI','Helvetica Neue',Arial,sans-serif"
MONO = "'JetBrains Mono','Cascadia Code',Consolas,'SFMono-Regular',Menlo,monospace"

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"


def kt(times, total):
    """Turn absolute seconds into a SMIL keyTimes string (0..1)."""
    return ";".join(f"{min(t / total, 1):.4f}" for t in times)


def discrete(attr, events, total):
    """events = [(seconds, value), ...] starting at 0 -> looping discrete <animate>."""
    times = [t for t, _ in events]
    vals = ";".join(str(v) for _, v in events)
    return (f'<animate attributeName="{attr}" values="{vals}" keyTimes="{kt(times, total)}" '
            f'dur="{total:.2f}s" calcMode="discrete" repeatCount="indefinite"/>')


# ================================================================ HERO ===
def build_hero():
    W, H = 1200, 420
    fs, cw = 38, 38 * 0.6          # monospace: char width ~= 0.6em (forced via textLength)
    x0, y_role = 64, 246
    type_step, del_step, hold, gap = 0.075, 0.035, 1.8, 0.35

    # build one timeline for all roles
    width_events, starts, t = [], [], 0.0
    for role in ROLES:
        starts.append(t)
        n = len(role)
        for k in range(n + 1):
            width_events.append((t, round(k * cw, 1)))
            if k < n:
                t += type_step
        t += hold
        for k in range(n - 1, -1, -1):
            t += del_step
            width_events.append((t, round(k * cw, 1)))
        t += gap
    total = t

    clip_anim = discrete("width", width_events, total)
    cursor_anim = discrete("x", [(tt, round(x0 + w + 2, 1)) for tt, w in width_events], total)

    role_texts = []
    for i, role in enumerate(ROLES):
        ev = [(0, 0)] if starts[i] > 0 else []
        ev.append((starts[i], 1))
        if i + 1 < len(ROLES):
            ev.append((starts[i + 1], 0))
        anim = discrete("opacity", ev, total) if len(ROLES) > 1 else ""
        role_texts.append(
            f'<text x="{x0}" y="{y_role}" font-family="{MONO}" font-size="{fs}" font-weight="700" '
            f'fill="url(#accent)" textLength="{len(role) * cw:.1f}" lengthAdjust="spacing" '
            f'opacity="{1 if i == 0 else 0}">{escape(role)}{anim}</text>')

    # network graph on the right
    cx, cy, rx, ry = 975, 210, 135, 135
    import math
    pts = []
    for i in range(len(NODES)):
        a = math.radians(-90 + i * 360 / len(NODES))
        pts.append((round(cx + rx * math.cos(a), 1), round(cy + ry * math.sin(a), 1)))

    edges = []
    for i, (x, y) in enumerate(pts):          # spokes
        edges.append(f'<path id="sp{i}" d="M{cx},{cy} L{x},{y}" class="edge"/>')
    for i in range(len(pts)):                  # ring (mesh, like a WAN)
        (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % len(pts)]
        edges.append(f'<path id="rg{i}" d="M{x1},{y1} L{x2},{y2}" class="edge faint"/>')

    packets = []
    for i in range(len(pts)):
        d = 1.6 + (i % 3) * 0.35
        packets.append(
            f'<circle r="4" fill="{ACCENT}" filter="url(#glow)"><animateMotion dur="{d:.2f}s" '
            f'begin="{i * 0.45:.2f}s" repeatCount="indefinite" keyPoints="{"0;1" if i % 2 else "1;0"}" '
            f'keyTimes="0;1" calcMode="linear"><mpath href="#sp{i}"/></animateMotion></circle>')
        packets.append(
            f'<circle r="2.6" fill="{ACCENT2}" opacity="0.8"><animateMotion dur="3.2s" '
            f'begin="{i * 0.6:.2f}s" repeatCount="indefinite"><mpath href="#rg{i}"/></animateMotion></circle>')

    nodes = []
    for i, ((x, y), label) in enumerate(zip(pts, NODES)):
        w = max(64, len(label) * 10 + 28)
        nodes.append(
            f'<g class="node" style="animation-delay:{i * 0.5:.1f}s">'
            f'<rect x="{x - w / 2}" y="{y - 16}" width="{w}" height="32" rx="16" class="pill"/>'
            f'<text x="{x}" y="{y + 5.5}" text-anchor="middle" class="nlabel">{label}</text></g>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Youssef Ghazy — AI builder, frontend developer, systems and networks">
<title>Youssef Ghazy — Hybrid Developer in Kuala Lumpur</title>
<defs>
  <linearGradient id="accent" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="{ACCENT}"/><stop offset="1" stop-color="{ACCENT2}"/></linearGradient>
  <radialGradient id="orbA"><stop offset="0" stop-color="{ACCENT}" stop-opacity=".55"/><stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/></radialGradient>
  <radialGradient id="orbB"><stop offset="0" stop-color="{ACCENT2}" stop-opacity=".35"/><stop offset="1" stop-color="{ACCENT2}" stop-opacity="0"/></radialGradient>
  <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#ffffff" stroke-opacity=".045"/></pattern>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="24"/></clipPath>
  <clipPath id="typing"><rect x="{x0}" y="{y_role - fs}" width="0" height="{fs + 14}">{clip_anim}</rect></clipPath>
  <filter id="glow" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<style>
  .orb {{ animation: drift 14s ease-in-out infinite alternate; transform-box: fill-box; transform-origin: center; }}
  .orb.b {{ animation-duration: 18s; animation-direction: alternate-reverse; }}
  @keyframes drift {{ from {{ transform: translate(0,0) scale(1); }} to {{ transform: translate(-60px,40px) scale(1.15); }} }}
  .fade {{ opacity: 0; animation: up .9s cubic-bezier(.16,1,.3,1) forwards; }}
  @keyframes up {{ from {{ opacity: 0; transform: translateY(14px); }} to {{ opacity: 1; transform: none; }} }}
  .dot {{ animation: pulse 1.8s ease-out infinite; transform-box: fill-box; transform-origin: center; }}
  @keyframes pulse {{ 0% {{ opacity: .9; transform: scale(1); }} 100% {{ opacity: 0; transform: scale(3); }} }}
  .cursor {{ animation: blink 1s steps(1) infinite; }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
  .edge {{ stroke: {ACCENT}; stroke-opacity: .35; stroke-width: 1.4; fill: none; }}
  .edge.faint {{ stroke-opacity: .16; stroke-dasharray: 4 6; animation: dash 6s linear infinite; }}
  @keyframes dash {{ to {{ stroke-dashoffset: -100; }} }}
  .pill {{ fill: #0d0d10; stroke: {ACCENT}; stroke-opacity: .45; }}
  .nlabel {{ font: 600 14px {SANS}; fill: #f2f2f2; }}
  .node {{ animation: bob 4s ease-in-out infinite; }}
  @keyframes bob {{ 50% {{ transform: translateY(-5px); }} }}
  .ring {{ animation: spin 18s linear infinite; transform-origin: {cx}px {cy}px; }}
  @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
  @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} .fade {{ opacity: 1; }} }}
</style>
<g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="{BG}"/>
  <rect width="{W}" height="{H}" fill="url(#grid)"/>
  <circle class="orb" cx="980" cy="90" r="300" fill="url(#orbA)" opacity=".5"/>
  <circle class="orb b" cx="120" cy="420" r="260" fill="url(#orbB)" opacity=".6"/>

  <!-- left: intro -->
  <g class="fade">
    <rect x="{x0}" y="48" width="420" height="34" rx="17" fill="{ACCENT}" fill-opacity=".12" stroke="{ACCENT}" stroke-opacity=".34"/>
    <circle class="dot" cx="{x0 + 20}" cy="65" r="5" fill="{ACCENT}"/>
    <circle cx="{x0 + 20}" cy="65" r="5" fill="{ACCENT}"/>
    <text x="{x0 + 36}" y="70.5" font-family="{SANS}" font-size="16" font-weight="600" fill="#ffffff">{escape(STATUS_PILL)}</text>
  </g>
  <text class="fade" style="animation-delay:.15s" x="{x0 - 3}" y="170" font-family="{SANS}" font-size="70" font-weight="800" fill="#ffffff" letter-spacing="-1.5">{escape(NAME_LINE)}</text>
  <g clip-path="url(#typing)">{"".join(role_texts)}</g>
  <rect class="cursor" x="{x0}" y="{y_role - fs + 4}" width="4" height="{fs + 4}" rx="1" fill="{ACCENT}">{cursor_anim}</rect>
  <text class="fade" style="animation-delay:.35s" x="{x0}" y="304" font-family="{SANS}" font-size="24" font-weight="500" fill="{MUTED}">{escape(TAGLINE)}</text>
  <text class="fade" style="animation-delay:.5s" x="{x0}" y="356" font-family="{SANS}" font-size="19" fill="{FAINT}" xml:space="preserve">{escape(META)}</text>

  <!-- right: tiny animated network (frontend + systems + networks) -->
  <g class="fade" style="animation-delay:.25s">
    {"".join(edges)}
    {"".join(packets)}
    <circle class="ring" cx="{cx}" cy="{cy}" r="62" fill="none" stroke="url(#accent)" stroke-width="2" stroke-dasharray="10 14"/>
    <circle cx="{cx}" cy="{cy}" r="46" fill="#0d0d10" stroke="url(#accent)" stroke-width="2.5"/>
    <text x="{cx}" y="{cy + 10}" text-anchor="middle" font-family="{SANS}" font-size="30" font-weight="800" fill="url(#accent)">YG</text>
    {"".join(nodes)}
  </g>
  <rect width="{W}" height="{H}" rx="24" fill="none" stroke="#ffffff" stroke-opacity=".08"/>
</g>
</svg>
'''
    (ASSETS / "hero.svg").write_text(svg, encoding="utf-8")


# ============================================================ TERMINAL ===
def build_terminal():
    W, fs, lh = 1200, 21, 37
    cw = fs * 0.6
    x0, y0 = 36, 104
    type_step, after_cmd, after_out = 0.06, 0.35, 0.55
    H = y0 + lh * (len(TERMINAL) + 1) + 10

    items, t, y = [], 0.8, y0
    timeline = []
    for kind, payload in TERMINAL:
        if kind == "cmd":
            n = len(payload)
            timeline.append(("cmd", payload, y, t, [(t + k * type_step, round(k * cw + (6 if k == n else 0), 1)) for k in range(n + 1)]))
            t += n * type_step + after_cmd
        else:
            timeline.append(("out", payload, y, t, None))
            t += after_out
        y += lh
    end_y, t_end = y, t
    total = t_end + 7            # hold the finished screen, then loop
    fade_out = total - 0.5

    def show_anim(t_show):
        return discrete("opacity", [(0, 0), (t_show, 1), (fade_out, 0)], total)

    prompt_w = 5 * cw
    for i, (kind, payload, y, t_show, steps) in enumerate(timeline):
        if kind == "cmd":
            prompt = (f'<text x="{x0}" y="{y}" class="mono"><tspan fill="{ACCENT}">➜</tspan>'
                      f'<tspan fill="{ACCENT2}" font-weight="700">  ~</tspan></text>')
            ev = [(0, 0)] + steps + [(fade_out, 0)]
            items.append(
                f'<g opacity="0">{show_anim(t_show)}{prompt}'
                f'<clipPath id="c{i}"><rect x="{x0 + prompt_w}" y="{y - fs}" width="0" height="{fs + 8}">'
                f'{discrete("width", ev, total)}</rect></clipPath>'
                f'<text x="{x0 + prompt_w}" y="{y}" class="mono" fill="#ffffff" clip-path="url(#c{i})">{escape(payload)}</text></g>')
        else:
            spans = "".join(f'<tspan fill="{c}">{escape(s)}</tspan>' for s, c in payload)
            items.append(f'<text x="{x0}" y="{y}" class="mono" xml:space="preserve" opacity="0">{show_anim(t_show)}{spans}</text>')

    # final prompt + blinking block cursor
    items.append(
        f'<g opacity="0">{show_anim(t_end)}<text x="{x0}" y="{end_y}" class="mono"><tspan fill="{ACCENT}">➜</tspan>'
        f'<tspan fill="{ACCENT2}" font-weight="700">  ~</tspan></text>'
        f'<rect class="cursor" x="{x0 + prompt_w}" y="{end_y - fs + 2}" width="{cw:.1f}" height="{fs + 3}" fill="{ACCENT}"/></g>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Terminal: whoami — Youssef Ghazy, IT student at APU, Frontend Developer at BarqSec">
<title>youssef@kuala-lumpur: ~</title>
<style>
  .mono {{ font-family: {MONO}; font-size: {fs}px; }}
  .cursor {{ animation: blink 1s steps(1) infinite; }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
</style>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="#0a0a0c" stroke="#ffffff" stroke-opacity=".1"/>
<path d="M1 19a18 18 0 0 1 18-18h{W - 38}a18 18 0 0 1 18 18v33H1z" fill="#121216"/>
<line x1="1" y1="52" x2="{W - 1}" y2="52" stroke="#ffffff" stroke-opacity=".08"/>
<circle cx="32" cy="27" r="7" fill="#ff5f57"/><circle cx="56" cy="27" r="7" fill="#febc2e"/><circle cx="80" cy="27" r="7" fill="#28c840"/>
<text x="{W / 2}" y="32" text-anchor="middle" font-family="{SANS}" font-size="14" fill="{FAINT}">youssef@kuala-lumpur: ~ — zsh</text>
{"".join(items)}
</svg>
'''
    (ASSETS / "terminal.svg").write_text(svg, encoding="utf-8")


# ============================================================== FOOTER ===
def build_footer():
    W, H = 1200, 150

    def wave(amp, length, y, n=8):
        d = f"M0 {y}"
        for i in range(n):
            x = i * length
            d += f" Q{x + length / 4} {y - amp} {x + length / 2} {y} T{x + length} {y}"
        return d + f" V{H} H0Z"

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Thanks for visiting">
<defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{ACCENT}"/><stop offset="1" stop-color="{ACCENT2}"/></linearGradient></defs>
<style>
  .w {{ animation: slide 9s linear infinite; }}
  .w2 {{ animation-duration: 14s; animation-direction: reverse; }}
  @keyframes slide {{ to {{ transform: translateX(-300px); }} }}
  @media (prefers-reduced-motion: reduce) {{ .w {{ animation: none; }} }}
</style>
<text x="{W / 2}" y="44" text-anchor="middle" font-family="{SANS}" font-size="22" font-weight="700" fill="url(#g)">Thanks for stopping by — let’s build something useful.</text>
<path class="w w2" d="{wave(16, 300, 110)}" fill="url(#g)" opacity=".25"/>
<path class="w" d="{wave(12, 300, 118)}" fill="url(#g)" opacity=".5"/>
</svg>
'''
    (ASSETS / "footer.svg").write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    build_hero()
    build_terminal()
    build_footer()
    print("wrote", *(p.name for p in sorted(ASSETS.glob("*.svg"))))
