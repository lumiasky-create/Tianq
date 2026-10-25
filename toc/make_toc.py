"""Generate the TOC graphic (toc.svg) for the metal-free electrosynthesis of DMF."""
import math

W, H = 1100, 600

# ---------- element styles: (radius in Å for drawing, gradient stops light/base/dark) ----------
EL = {
    "H": (0.60, ("#ffffff", "#e9ecf1", "#9aa3af")),
    "C": (0.84, ("#9aa1ab", "#4f5662", "#1f232a")),
    "N": (0.80, ("#b9cfff", "#3f72e6", "#17306f")),
    "O": (0.78, ("#ffc2bb", "#e8494f", "#7d171c")),
    "S": (1.00, ("#ffffff", "#d3d9e1", "#7f8a98")),  # surface (metal-free carbon electrode)
}

# ---------- small vector helpers ----------
def add(a, b): return tuple(x + y for x, y in zip(a, b))
def sub(a, b): return tuple(x - y for x, y in zip(a, b))
def mul(a, k): return tuple(x * k for x in a)
def dot(a, b): return sum(x * y for x, y in zip(a, b))
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def norm(a): return mul(a, 1 / math.sqrt(dot(a, a)))

def rot(v, yaw=0, pitch=0, roll=0):
    """Rotate about y (yaw), then x (pitch), then z (roll); angles in degrees."""
    x, y, z = v
    a = math.radians(yaw); x, z = x*math.cos(a) + z*math.sin(a), -x*math.sin(a) + z*math.cos(a)
    a = math.radians(pitch); y, z = y*math.cos(a) - z*math.sin(a), y*math.sin(a) + z*math.cos(a)
    a = math.radians(roll); x, y = x*math.cos(a) - y*math.sin(a), x*math.sin(a) + y*math.cos(a)
    return (x, y, z)

def methyl_H(c, toward, ref, phase=0.0, d=1.09):
    """Three tetrahedral H positions on carbon c whose fourth bond points to `toward`."""
    a = norm(sub(toward, c))
    p = norm(cross(a, ref)); q = cross(a, p)
    out = []
    for k in range(3):
        t = math.radians(phase + 120 * k)
        perp = add(mul(p, math.cos(t)), mul(q, math.sin(t)))
        dirn = add(mul(a, -1/3), mul(perp, math.sqrt(8)/3))
        out.append(("H", add(c, mul(dirn, d))))
    return out

def planar(angle_deg, length):
    t = math.radians(angle_deg)
    return (length*math.cos(t), length*math.sin(t), 0.0)

# ---------- molecules (Å, y up) ----------
def dimethylamine():
    s3 = math.sqrt(3)
    d = [(1/s3, -1/s3, 1/s3), (-1/s3, -1/s3, -1/s3), (1/s3, 1/s3, -1/s3), (-1/s3, 1/s3, 1/s3)]
    N = (0, 0, 0)
    C1, C2, Hn = mul(d[0], 1.46), mul(d[1], 1.46), mul(d[2], 1.01)
    atoms = [("N", N), ("C", C1), ("C", C2), ("H", Hn)]
    atoms += methyl_H(C1, N, (0, 0, 1), 20) + methyl_H(C2, N, (0, 0, 1), 200)
    return atoms

def imine():
    N = (0, 0, 0)
    C2 = planar(-30, 1.28)            # =CH2
    Cm = planar(-30 + 118, 1.46)      # CH3
    atoms = [("N", N), ("C", C2), ("C", Cm)]
    for a in (-30 + 180 + 121, -30 + 180 - 121):
        atoms.append(("H", add(C2, planar(a + 180, 1.08))))
    atoms += methyl_H(Cm, N, (0, 0, 1), 30)
    return atoms

def water():
    O = (0, 0, 0)
    return [("O", O), ("H", planar(90 + 52, 0.96)), ("H", planar(90 - 52, 0.96))]

def formaldehyde():
    C = (0, 0, 0)
    return [("C", C), ("O", (0, -1.21, 0)),
            ("H", planar(90 + 61, 1.10)), ("H", planar(90 - 61, 1.10))]

def dmf():
    C = (0, 0, 0)
    O = planar(120, 1.23)
    Hc = planar(240, 1.10)
    N = planar(0, 1.35)
    Ma = add(N, planar(60, 1.45))
    Mb = add(N, planar(-60, 1.45))
    atoms = [("C", C), ("O", O), ("H", Hc), ("N", N), ("C", Ma), ("C", Mb)]
    atoms += methyl_H(Ma, N, (0, 0, 1), 90) + methyl_H(Mb, N, (0, 0, 1), 90)
    return atoms

# ---------- rendering ----------
def place(atoms, cx, cy, scale, yaw=0, pitch=0, roll=0, anchor="center"):
    """Rotate, scale and translate; anchor='bottom' puts the lowest sphere edge at cy."""
    pts = []
    for el, p in atoms:
        x, y, z = rot(p, yaw, pitch, roll)
        pts.append((el, x, y, z))
    xs = [x for _, x, _, _ in pts]
    ox = (min(xs) + max(xs)) / 2
    if anchor == "bottom":
        oy = min(y - EL[el][0] for el, _, y, _ in pts)
    else:
        ys = [y for _, _, y, _ in pts]; oy = (min(ys) + max(ys)) / 2
    return [(el, cx + (x - ox)*scale, cy - (y - oy)*scale, z, EL[el][0]*scale) for el, x, y, z in pts]

def spheres_svg(placed):
    out = []
    for el, x, y, z, r in sorted(placed, key=lambda t: t[3]):
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="url(#g{el})" '
                   f'stroke="{EL[el][1][2]}" stroke-opacity=".35" stroke-width="1"/>')
    return "\n".join(out)

def shadow(cx, cy, rx, ry=7, op=.28):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#1b2330" opacity="{op}" filter="url(#blur)"/>'

def arrow(x1, y1, x2, y2, color="#3a4352", w=4):
    ang = math.atan2(y2 - y1, x2 - x1)
    L, Wh = 18, 9
    bx, by = x2 - L*math.cos(ang), y2 - L*math.sin(ang)
    px, py = -math.sin(ang)*Wh, math.cos(ang)*Wh
    head = f"M{x2:.1f},{y2:.1f} L{bx+px:.1f},{by+py:.1f} Q{bx+L*.25*math.cos(ang):.1f},{by+L*.25*math.sin(ang):.1f} {bx-px:.1f},{by-py:.1f} Z"
    sx, sy = x2 - (L*.7)*math.cos(ang), y2 - (L*.7)*math.sin(ang)
    return (f'<line x1="{x1}" y1="{y1}" x2="{sx:.1f}" y2="{sy:.1f}" stroke="{color}" stroke-width="{w}" stroke-linecap="round"/>'
            f'<path d="{head}" fill="{color}"/>')

def grad_defs():
    g = []
    for el, (_, (hi, base, dark)) in EL.items():
        g.append(f'''<radialGradient id="g{el}" cx="0.5" cy="0.5" r="0.5" fx="0.36" fy="0.30">
  <stop offset="0" stop-color="{hi}"/><stop offset="0.45" stop-color="{base}"/>
  <stop offset="0.85" stop-color="{dark}" stop-opacity="0.95"/><stop offset="1" stop-color="{dark}"/></radialGradient>''')
    return "\n".join(g)

# ---------- scene ----------
SC = 34            # px per Å for adsorbates
SURF_R = 24        # surface sphere radius (px)
SURF_TOP = 482     # y of the top of the front surface row
TEXT = "#1f2633"
FONT = "Arial, Helvetica, 'Liberation Sans', sans-serif"

def surface():
    rows = []
    r = SURF_R
    # back row (smaller, lighter), middle row, front row
    for i, (yc, rr, xoff, op) in enumerate([(SURF_TOP + 10, r*.92, r, .75),
                                             (SURF_TOP + r + 4, r, 0, 1.0),
                                             (SURF_TOP + 2*r + 14, r*1.04, r, 1.0)]):
        n = int(W / (2*r)) + 3
        for k in range(-1, n):
            x = k * 2 * r + xoff
            rows.append(f'<circle cx="{x:.1f}" cy="{yc:.1f}" r="{rr:.1f}" fill="url(#gS)" opacity="{op}" '
                        f'stroke="#7f8a98" stroke-opacity=".25" stroke-width="1"/>')
    return "\n".join(rows)

def pill(cx, cy, parts, size=21):
    """Label on a rounded tag so it stays legible on top of the electrode surface."""
    n = sum(len(t) * (.66 if k == "sub" else 1) for t, k in parts)
    w = n * size * .58 + 26
    return (f'<rect x="{cx - w/2:.1f}" y="{cy - 17}" width="{w:.1f}" height="34" rx="17" fill="#ffffff" '
            f'fill-opacity=".93" stroke="#c9d2df" stroke-width="1.2"/>'
            + sub_text(cx, cy + size*.36, parts, size=size, anchor="middle", halo=False))

def sub_text(x, y, parts, size=21, anchor="start", weight="normal", fill=TEXT, halo=True):
    """parts: list of (text, kind) where kind in '', 'sub', 'sup'."""
    spans = []
    for t, kind in parts:
        if kind == "sub":
            spans.append(f'<tspan baseline-shift="-28%" font-size="{size*.68:.1f}">{t}</tspan>')
        elif kind == "sup":
            spans.append(f'<tspan baseline-shift="40%" font-size="{size*.68:.1f}">{t}</tspan>')
        else:
            spans.append(f'<tspan>{t}</tspan>')
    h = ' stroke="#ffffff" stroke-width="6" stroke-linejoin="round" paint-order="stroke"' if halo else ""
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}"{h}>{"".join(spans)}</text>')

def build():
    o = []
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
    o.append("<defs>")
    o.append(grad_defs())
    o.append('''<filter id="blur" x="-50%" y="-200%" width="200%" height="500%"><feGaussianBlur stdDeviation="5"/></filter>
<filter id="card" x="-10%" y="-10%" width="120%" height="130%">
  <feDropShadow dx="0" dy="6" stdDeviation="9" flood-color="#1b2a44" flood-opacity=".14"/></filter>
<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#ffffff"/><stop offset="0.62" stop-color="#f6f8fb"/><stop offset="1" stop-color="#e9edf3"/></linearGradient>
<linearGradient id="fadeX" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".04" stop-color="#fff"/>
  <stop offset=".96" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<mask id="surfMask"><rect width="1100" height="600" fill="url(#fadeX)"/></mask>
<linearGradient id="check" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#f26a6e"/><stop offset="1" stop-color="#d63a42"/></linearGradient>
<linearGradient id="cardHead" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#eef3fc"/><stop offset="1" stop-color="#f8fafd"/></linearGradient>
<clipPath id="cardClip"><rect x="606" y="20" width="470" height="300" rx="20"/></clipPath>''')
    o.append("</defs>")
    o.append(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')

    # ---- highlights (checklist) ----
    items = [
        [("Metal-free", "b"), (" electrocatalysis", "")],
        [("Tolerance of ", ""), ("crude feedstocks", "b")],
        [("FE", "b"), ("DMF", "bsub"), (" ~ ", ""), ("40%", "b")],
        [("Yield ~ ", ""), ("250", "b"), (" μmol cm", ""), ("−2", "sup"), (" h", ""), ("−1", "sup")],
    ]
    y0, dy, fs = 78, 66, 29
    for i, parts in enumerate(items):
        y = y0 + i*dy
        o.append(f'<circle cx="62" cy="{y-10}" r="17" fill="url(#check)"/>')
        o.append(f'<path d="M53,{y-10} l6,6.5 l12,-13" fill="none" stroke="#fff" stroke-width="4.2" '
                 f'stroke-linecap="round" stroke-linejoin="round"/>')
        spans = []
        for t, k in parts:
            fw = ' font-weight="bold"' if "b" in k else ""
            if "sub" in k:
                spans.append(f'<tspan{fw} baseline-shift="-25%" font-size="{fs*.66:.1f}">{t}</tspan>')
            elif k == "sup":
                spans.append(f'<tspan baseline-shift="38%" font-size="{fs*.66:.1f}">{t}</tspan>')
            else:
                spans.append(f'<tspan{fw}>{t}</tspan>')
        o.append(f'<text x="94" y="{y}" font-family="{FONT}" font-size="{fs}" fill="{TEXT}">{"".join(spans)}</text>')

    # ---- DMF card ----
    o.append('<rect x="606" y="20" width="470" height="300" rx="20" fill="#ffffff" filter="url(#card)"/>')
    o.append('<g clip-path="url(#cardClip)"><rect x="606" y="20" width="470" height="56" fill="url(#cardHead)"/></g>')
    o.append('<rect x="606" y="20" width="470" height="300" rx="20" fill="none" stroke="#cfd8e6" stroke-width="1.5"/>')
    o.append('<line x1="606" y1="76" x2="1076" y2="76" stroke="#dde4ee" stroke-width="1.5"/>')
    o.append(f'<text x="841" y="57" text-anchor="middle" font-family="{FONT}" font-size="27" font-weight="bold" fill="{TEXT}">'
             f'Dimethylformamide <tspan fill="#5a6577" font-weight="normal">(DMF)</tspan></text>')
    o.append(spheres_svg(place(dmf(), 745, 200, 40, yaw=-14, pitch=10, roll=-30)))
    # skeletal formula
    cx, cy, b = 940, 214, 46
    C = (cx, cy)
    Opt = (cx, cy - b)
    Hpt = (cx - b*math.cos(math.radians(30)), cy + b/2)
    Npt = (cx + b*math.cos(math.radians(30)), cy + b/2)
    M1 = (Npt[0] + b*math.cos(math.radians(30)), Npt[1] - b/2)
    M2 = (Npt[0], Npt[1] + b)
    ln = lambda a, c, **k: (f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{c[0]:.1f}" y2="{c[1]:.1f}" '
                            f'stroke="{TEXT}" stroke-width="3" stroke-linecap="round"/>')
    def shorten(a, c, s0, s1):
        d = math.dist(a, c); ux, uy = (c[0]-a[0])/d, (c[1]-a[1])/d
        return (a[0]+ux*s0, a[1]+uy*s0), (c[0]-ux*s1, c[1]-uy*s1)
    o.append(ln(*shorten(C, Opt, 0, 14)))
    o.append(ln(*shorten((C[0]+7, C[1]+4), (Opt[0]+7, Opt[1]), 4, 14)))
    o.append(ln(*shorten(C, Hpt, 0, 13)))
    o.append(ln(*shorten(C, Npt, 0, 13)))
    o.append(ln(*shorten(Npt, M1, 13, 0)))
    o.append(ln(*shorten(Npt, M2, 13, 0)))
    for lab, (x, y), col in (("O", Opt, "#d63a42"), ("H", Hpt, TEXT), ("N", Npt, "#2f5fcf")):
        o.append(f'<text x="{x:.1f}" y="{y+9:.1f}" text-anchor="middle" font-family="{FONT}" '
                 f'font-size="26" font-weight="bold" fill="{col}">{lab}</text>')

    # ---- electrode surface ----
    o.append(f'<g mask="url(#surfMask)">{surface()}</g>')

    # ---- adsorbates ----
    base = SURF_TOP + 4
    mols = [
        (dimethylamine(), 112, dict(yaw=25, pitch=-10, roll=8)),
        (imine(), 330, dict(yaw=-20, pitch=10, roll=-62)),
        (formaldehyde(), 612, dict(yaw=25, pitch=8, roll=0)),
        (dimethylamine(), 860, dict(yaw=-155, pitch=-10, roll=-8)),
    ]
    tops = []
    for atoms, x, kw in mols:
        pl = place(atoms, x, base, SC, anchor="bottom", **kw)
        xs = [p[1] for p in pl]
        o.append(shadow(x, base + 4, (max(xs) - min(xs)) / 2 * .8))
        o.append(spheres_svg(pl))
        tops.append(min(p[2] - p[4] for p in pl))

    # water (gas phase, above arrow 2)
    o.append(spheres_svg(place(water(), 462, 360, SC, yaw=0, pitch=-45, roll=0)))

    # arrows
    ay = 418
    o.append(arrow(190, ay, 252, ay))
    o.append(arrow(410, ay, 532, ay))
    o.append(arrow(736, 392, 736, 330))
    o.append(f'<text x="736" y="430" text-anchor="middle" font-family="{FONT}" font-size="40" fill="#3a4352">+</text>')

    # labels
    o.append(sub_text(512, 372, [("H", ""), ("2", "sub"), ("O", "")], size=23))
    o.append(pill(112, 548, [("(CH", ""), ("3", "sub"), (")", ""), ("2", "sub"), ("NH", "")]))
    o.append(pill(330, 548, [("CH", ""), ("3", "sub"), ("N=CH", ""), ("2", "sub")]))
    o.append(pill(612, 548, [("HCHO", "")]))
    o.append(pill(860, 548, [("(CH", ""), ("3", "sub"), (")", ""), ("2", "sub"), ("NH", "")]))

    o.append("</svg>")
    return "\n".join(o)

if __name__ == "__main__":
    import pathlib
    out = pathlib.Path(__file__).with_name("toc.svg")
    out.write_text(build(), encoding="utf-8")
    print("wrote", out)
