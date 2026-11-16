"""Membuat atlas sprite PAS 1.0 untuk Mbah Ijuk dan Mak Sedot.
Atlas 512x768, kotak 128x128, 4 kolom x 6 baris: IDLE WALK ATTACK HIT BLOCK KO.
Menghadap kanan, latar transparan, tanpa bayangan lantai, kaki di garis anchor y=124.
Digambar 4x lebih besar lalu diperkecil (rata-rata kotak) agar halus.
Pemakaian: python3 gen_karakter.py <folder_keluaran_karakter>"""
import math, sys, os, json
from PIL import Image, ImageDraw, ImageFilter

SS = 4; C = 128; FLOOR = 124; ROWS = ["IDLE", "WALK", "ATTACK", "HIT", "BLOCK", "KO"]
OUT = (38, 24, 20); O = 1.0  # warna & tebal garis tepi (px kotak)
LAYERS = ["arm_back", "prop_back", "core", "prop_front", "arm_front", "fx"]

# ---------------- geometri ----------------
def add(a, b): return (a[0] + b[0], a[1] + b[1])
def sub(a, b): return (a[0] - b[0], a[1] - b[1])
def mul(a, k): return (a[0] * k, a[1] * k)
def norm(a):
    d = math.hypot(*a) or 1e-6; return (a[0] / d, a[1] / d)
def vdir(deg, L=1.0):  # 0 = ke bawah, 90 = ke kanan (depan), 180 = ke atas
    r = math.radians(deg); return (math.sin(r) * L, math.cos(r) * L)
def rot(p, c, deg):
    r = math.radians(deg); x, y = p[0] - c[0], p[1] - c[1]
    return (c[0] + x * math.cos(r) - y * math.sin(r), c[1] + x * math.sin(r) + y * math.cos(r))
def lerp(a, b, t): return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
def hull(pts):
    pts = sorted(set((round(x, 3), round(y, 3)) for x, y in pts))
    def cross(o, a, b): return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0: lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0: up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]
def ik(S, H, L1, L2, sign):
    d0 = math.hypot(H[0] - S[0], H[1] - S[1]); u = norm(sub(H, S))
    d = max(min(d0, L1 + L2 - 0.05), abs(L1 - L2) + 0.05)
    a = (L1 * L1 - L2 * L2 + d * d) / (2 * d); h = math.sqrt(max(L1 * L1 - a * a, 0))
    P = add(S, mul(u, a)); n = (-u[1], u[0])
    E = add(P, mul(n, h * sign)); Hn = add(S, mul(u, d))
    return E, Hn

# ---------------- daftar primitif ----------------
class Frame:
    def __init__(self): self.items = []
    def cap(self, layer, a, b, w, col, outline=True, absolute=False):
        self.items.append(("cap", layer, [a, b], w, col, outline, absolute))
    def circ(self, layer, c, r, col, outline=True, absolute=False):
        self.items.append(("circ", layer, [c], r, col, outline, absolute))
    def poly(self, layer, pts, col, outline=True, absolute=False):
        self.items.append(("poly", layer, list(pts), 0, col, outline, absolute))
    def line(self, layer, pts, w, col, absolute=False):
        self.items.append(("line", layer, list(pts), w, col, False, absolute))
    def glow(self, layer, pts, col, blur, absolute=False):
        self.items.append(("glow", layer, list(pts), blur, col, False, absolute))

def render(fr, T):
    """T: fungsi transform titik (kotak px) -> kotak px. Kembalikan dict layer -> Image SS."""
    imgs = {k: Image.new("RGBA", (C * SS, C * SS), (0, 0, 0, 0)) for k in LAYERS}
    for kind, layer, pts, w, col, outline, absolute in fr.items:
        tp = [(p if absolute else T(p)) for p in pts]
        tp = [(x * SS, y * SS) for x, y in tp]
        img = imgs[layer]
        translucent = len(col) == 4 and col[3] < 255
        tgt = Image.new("RGBA", img.size, (0, 0, 0, 0)) if (translucent or kind == "glow") else img
        d = ImageDraw.Draw(tgt)
        o = O * SS
        if kind == "cap":
            a, b = tp; ww = w * SS
            if outline:
                d.line([a, b], fill=OUT, width=int(round(ww + 2 * o)))
                for p in (a, b): d.ellipse((p[0] - ww / 2 - o, p[1] - ww / 2 - o, p[0] + ww / 2 + o, p[1] + ww / 2 + o), fill=OUT)
            d.line([a, b], fill=col, width=int(round(ww)))
            for p in (a, b): d.ellipse((p[0] - ww / 2, p[1] - ww / 2, p[0] + ww / 2, p[1] + ww / 2), fill=col)
        elif kind == "circ":
            (c,) = tp; r = w * SS
            if outline: d.ellipse((c[0] - r - o, c[1] - r - o, c[0] + r + o, c[1] + r + o), fill=OUT)
            d.ellipse((c[0] - r, c[1] - r, c[0] + r, c[1] + r), fill=col)
        elif kind == "poly":
            if outline:
                d.polygon(tp, fill=col, outline=OUT, width=int(round(o)))
            else:
                d.polygon(tp, fill=col)
        elif kind == "line":
            d.line(tp, fill=col, width=max(1, int(round(w * SS))), joint="curve")
        elif kind == "glow":
            d.polygon(tp, fill=col); tgt = tgt.filter(ImageFilter.GaussianBlur(w * SS))
        if tgt is not img:
            imgs[layer] = Image.alpha_composite(img, tgt)
    return imgs

def bottom_row(img):
    a = img.getchannel("A"); bb = a.point(lambda v: 255 if v > 0 else 0).getbbox()
    return None if bb is None else bb[3]

def build_frame(fr, theta=0.0, pivot=(64, 124), dx=0.0, ground=True):
    """Render dengan rotasi global (jatuh) + pembumian otomatis: titik terendah tubuh = garis lantai."""
    def T0(p): q = rot(p, pivot, theta); return (q[0] + dx, q[1])
    dy = 0.0
    if ground:
        test = render(fr, T0)
        body = Image.alpha_composite(Image.alpha_composite(test["core"], test["arm_back"]), test["arm_front"])
        b = bottom_row(body)
        dy = (FLOOR * SS - b) / SS
    def T(p): q = T0(p); return (q[0], q[1] + dy)
    imgs = render(fr, T)
    # potong semua yang di bawah garis lantai (tanpa bayangan/benda di bawah lantai)
    for k in imgs:
        px = imgs[k].load()
        for y in range(FLOOR * SS, C * SS):
            for x in range(C * SS):
                if px[x, y][3]: px[x, y] = (0, 0, 0, 0)
    comp = Image.new("RGBA", (C * SS, C * SS), (0, 0, 0, 0))
    for k in LAYERS: comp = Image.alpha_composite(comp, imgs[k])
    def down(im): return im.convert("RGBa").resize((C, C), Image.BOX).convert("RGBA")
    core = Image.alpha_composite(Image.alpha_composite(imgs["arm_back"], imgs["core"]), imgs["arm_front"])
    return down(comp), down(imgs["core"]), down(core)

# ---------------- bagian tubuh umum ----------------
def face(fr, H, r, phi, eye="open", mouth="smile", skin=(190, 135, 95), cheek=None, brow=0):
    L = lambda u, v: add(H, rot((u, v), (0, 0), phi))
    dark = (35, 22, 18)
    # hidung
    fr.circ("core", L(r - 0.6, 1.6), 2.2, skin)
    # mata
    e = L(4.6, -1.6)
    if eye == "open": fr.circ("core", e, 1.35, dark, outline=False)
    elif eye == "closed": fr.line("core", [L(2.8, -1.4), L(4.6, -0.6), L(6.4, -1.4)], 0.9, dark)
    elif eye == "wide":
        fr.circ("core", e, 2.3, (250, 250, 245), outline=True); fr.circ("core", L(5.2, -1.6), 1.1, dark, outline=False)
    elif eye == "squint": fr.line("core", [L(2.9, -2.6), L(6.2, -1.4), L(3.1, -0.4)], 0.9, dark)
    elif eye == "pain": fr.line("core", [L(6.2, -2.8), L(3.2, -1.5), L(6.2, -0.2)], 0.9, dark)
    elif eye == "x":
        fr.line("core", [L(3.2, -3.0), L(6.2, -0.2)], 0.9, dark); fr.line("core", [L(6.2, -3.0), L(3.2, -0.2)], 0.9, dark)
    elif eye == "spiral":
        pts = [L(4.6 + math.cos(t) * t / 4.2, -1.6 + math.sin(t) * t / 4.2) for t in [i * 0.5 for i in range(1, 22)]]
        fr.line("core", pts, 0.7, dark)
    # alis
    if eye not in ("x", "spiral"):
        fr.line("core", [L(2.6, -4.6 + brow), L(6.6, -4.2 - brow)], 0.9, (120, 110, 105))
    # keriput & pipi
    fr.line("core", [L(1.6, 2.4), L(2.6, 3.6)], 0.6, (140, 90, 60))
    if cheek: fr.circ("core", L(3.6, 3.0), 1.7, cheek, outline=False)
    m = L(6.8, 5.6)
    if mouth == "smile": fr.line("core", [L(5.2, 5.0), L(6.8, 6.0), L(8.2, 5.2)], 0.8, dark)
    elif mouth == "flat": fr.line("core", [L(5.4, 5.8), L(8.2, 5.8)], 0.8, dark)
    elif mouth == "o": fr.circ("core", m, 1.6, dark, outline=False)
    elif mouth == "open": fr.circ("core", L(7.4, 5.6), 2.4, (90, 20, 25), outline=True)
    elif mouth == "wavy": fr.line("core", [L(5.0, 6.0), L(6.0, 5.2), L(7.0, 6.0), L(8.0, 5.2)], 0.8, dark)
    elif mouth == "puff":
        fr.circ("core", L(4.6, 3.8), 4.6, skin, outline=True)
        fr.circ("core", L(4.0, 3.0), 1.8, (225, 140, 120), outline=False)
        fr.line("core", [L(8.6, 5.4), L(9.6, 5.8)], 0.9, dark)
    return L

def sandal(fr, layer, A, col):
    fr.poly(layer, [add(A, (-3.2, 0.6)), add(A, (5.4, 0.6)), add(A, (5.8, 3.0)), add(A, (-3.4, 3.0))], col)

def arm(fr, layer, S, target, col, skin, w=6.0, L1=14.0, L2=13.0, sign=1, hand=True):
    E, Hh = ik(S, target, L1, L2, sign)
    fr.cap(layer, S, E, w, col); fr.cap(layer, E, Hh, w - 0.6, col)
    if hand: fr.circ(layer, Hh, 2.8, skin)
    return Hh

def broom(fr, layer, T, B, absolute=False):
    u = norm(sub(B, T)); n = (-u[1], u[0]); Bh = sub(B, mul(u, 17))
    fr.cap(layer, T, Bh, 2.6, (156, 108, 62), absolute=absolute)
    pts = [add(Bh, mul(n, 2.6)), add(B, mul(n, 8.5)), add(B, mul(n, 4.5)), add(add(B, mul(u, 1.2)), mul(n, 1.0)),
           add(B, mul(n, -2.5)), add(add(B, mul(u, 1.0)), mul(n, -6.0)), add(B, mul(n, -8.5)), add(Bh, mul(n, -2.6))]
    fr.poly(layer, pts, (52, 42, 36), absolute=absolute)
    for k in (-5.5, -2.5, 0.5, 3.5, 6.0):
        fr.line(layer, [add(Bh, mul(n, k * 0.3)), add(B, mul(n, k))], 0.5, (105, 88, 70), absolute=absolute)
    fr.cap(layer, sub(Bh, mul(u, 2.2)), add(Bh, mul(u, 0.8)), 4.2, (214, 172, 58), absolute=absolute)

def plunger(fr, layer, E, Cp, absolute=False):
    """E = ujung gagang, Cp = pangkal mangkuk karet. Mulut mangkuk di ujung jauh (Cp + 7u)."""
    u = norm(sub(Cp, E)); n = (-u[1], u[0]); R = add(Cp, mul(u, 7.2))
    fr.cap(layer, E, add(Cp, mul(u, 1.0)), 3.0, (170, 118, 70), absolute=absolute)
    dome = [add(R, add(mul(n, 8.0 * math.cos(t)), mul(u, -7.2 * math.sin(t)))) for t in [i * math.pi / 14 for i in range(15)]]
    fr.poly(layer, dome + [add(R, mul(n, -9.0)), add(R, mul(n, 9.0))], (150, 28, 40), absolute=absolute)
    fr.line(layer, [add(R, add(mul(n, 4.5), mul(u, -4.2))), add(R, add(mul(n, 1.0), mul(u, -6.0)))], 1.0, (226, 96, 104), absolute=absolute)

def speed_lines(fr, pts_pairs, col=(250, 248, 235, 200), w=0.9):
    for a, b in pts_pairs: fr.line("fx", [a, b], w, col)

def smoke(fr, c, r, a=150): fr.circ("fx", c, r, (205, 205, 210, a), outline=False)

# ---------------- MBAH IJUK (mage) ----------------
MB = dict(skin=(190, 135, 95), skin_d=(160, 108, 72), hair=(214, 214, 220), keb=(88, 132, 78), keb_d=(62, 98, 56),
          lace=(238, 228, 198), jarik=(122, 80, 46), jarik_d=(92, 60, 34), motif=(214, 168, 88), sandal=(96, 62, 40))

def nenek_kebaya(fr, hip, lean, head_tilt, feet, hands, bun_off=(0, 0), face_kw=None, hairpin=True, back_hand_front=False):
    c = MB
    sh = add(hip, vdir(180 - lean, 28))           # bahu
    t = norm(sub(sh, hip)); n = (-t[1], t[0])     # n mengarah ke depan (kanan) saat tegak
    n = (-n[0], -n[1]) if n[0] < 0 and abs(lean) < 90 else n
    head = add(sh, vdir(180 - (lean * 0.55 + 14), 12.5))
    # kaki di balik kain jarik: satu bungkus kain (selubung cembung pinggul-lutut-mata kaki)
    knees, ankles = [], []
    for i, F in enumerate(feet):  # 0 = kaki belakang, 1 = kaki depan
        K, A = ik(add(hip, mul(n, -3 + i * 6)), F, 20, 19, -1)
        knees.append(K); ankles.append(A)
    for A in ankles: sandal(fr, "core", A, c["sandal"])
    ring = lambda p, r: [add(p, rot((r, 0), (0, 0), a)) for a in range(0, 360, 30)]
    skirt = hull(ring(add(hip, mul(n, -6)), 5.5) + ring(add(hip, mul(n, 6)), 5.5) + ring(knees[0], 6.5) + ring(knees[1], 6.5)
                 + ring(lerp(knees[0], ankles[0], 0.85), 5.0) + ring(lerp(knees[1], ankles[1], 0.85), 5.0))
    fr.poly("core", skirt, c["jarik"])
    # lipatan kain + motif batik
    fr.line("core", [lerp(hip, knees[1], 0.35), lerp(knees[0], knees[1], 0.5), lerp(lerp(knees[0], ankles[0], 0.85), lerp(knees[1], ankles[1], 0.85), 0.5)], 0.8, c["jarik_d"])
    fr.line("core", [lerp(knees[0], ankles[0], 0.85), lerp(knees[1], ankles[1], 0.85)], 1.6, c["jarik_d"])
    for a in (0.25, 0.55, 0.8):
        for k in (-4, 4):
            fr.circ("core", add(lerp(hip, lerp(ankles[0], ankles[1], 0.5), a), mul(n, k)), 1.1, c["motif"], outline=False)
    # badan kebaya + punuk bungkuk
    fr.circ("core", add(add(sh, mul(n, -6)), mul(t, -3)), 8.2, c["keb"])
    fr.poly("core", [add(hip, mul(n, -10.5)), add(hip, mul(n, 10.5)), add(sh, mul(n, 7.5)), add(sh, mul(n, -8.0))], c["keb"])
    fr.line("core", [add(sh, mul(n, 6.2)), add(hip, mul(n, 9.2))], 1.6, c["lace"])
    fr.cap("core", add(hip, mul(n, -10)), add(hip, mul(n, 10)), 2.4, c["keb_d"])  # stagen
    # lengan belakang
    shb = add(sh, mul(n, -3))
    hb = arm(fr, "arm_back", shb, hands[0], c["keb_d"], c["skin_d"])
    if back_hand_front: fr.circ("arm_front", hb, 2.8, c["skin"])
    # leher, sanggul, kepala
    fr.cap("core", sh, lerp(sh, head, 0.6), 5.5, c["skin"])
    phi = head_tilt
    L = lambda u, v: add(head, rot((u, v), (0, 0), phi))
    bun = add(L(-9.2, -4.2), bun_off)
    fr.circ("core", bun, 5.6, c["hair"])
    fr.line("core", [add(bun, (-2.5, -2)), add(bun, (2.5, 2))], 0.6, (170, 170, 180))
    if hairpin: fr.cap("core", add(bun, (-4.5, -5.0)), add(bun, (3.5, 2.5)), 1.0, (214, 172, 58))
    fr.circ("core", head, 10.0, c["hair"])
    fr.circ("core", L(2.0, 1.8), 8.1, c["skin"], outline=False)
    fr.line("core", [L(-4.5, -7.0), L(0.5, -8.8), L(5.5, -7.6)], 0.6, (170, 170, 180))
    kw = dict(eye="open", mouth="smile", skin=c["skin"], cheek=(214, 128, 112))
    kw.update(face_kw or {})
    face(fr, head, 10.0, phi, **kw)
    # lengan depan
    hf = arm(fr, "arm_front", add(sh, mul(n, 2)), hands[1], c["keb"], c["skin"])
    return dict(sh=sh, head=head, L=L, hf=hf, hb=hb, mouth=L(9.6, 5.6))

def fire(fr, M, x_end, wob=0.0):
    L = x_end - M[0]
    def cone(scale, col, yoff=0.0):
        top, bot = [], []
        for i in range(13):
            s = i / 12; x = M[0] + s * L
            h = (1.2 + s * 9.5) * scale * (1 + 0.18 * math.sin(s * 9 + wob))
            top.append((x, M[1] - h + yoff)); bot.append((x, M[1] + h * 0.85 + yoff))
        tip = (x_end + 1.0, M[1] + yoff)
        return top + [tip] + bot[::-1]
    fr.glow("fx", cone(1.25, (255, 120, 40, 160)), (255, 120, 40, 150), 2.0)
    fr.poly("fx", cone(1.0, (222, 62, 28)), (222, 62, 28), outline=False)
    fr.poly("fx", cone(0.68, (250, 150, 40)), (250, 150, 40), outline=False)
    fr.poly("fx", cone(0.36, (255, 236, 140)), (255, 236, 140), outline=False)

def ember(fr, c, r=1.1): fr.circ("fx", c, r, (255, 170, 60), outline=False)

def mbah_ijuk(row, f):
    fr = Frame(); th = 0.0; piv = (64, 124); dx = 0.0
    FB, FF = (56, 121), (72, 121)
    if row == "IDLE":
        bob = [0, 0.6, 1.2, 0.6][f]
        hip = (61, 84 + bob); lean = 22 + bob
        P = nenek_kebaya(fr, hip, lean, 4, [FB, FF], [(52, 82 + bob), (92, 75 + bob * 0.5)])
        broom(fr, "prop_back", (93, 41), (95, 124))
        m = P["mouth"]
        for k in range(3):
            s = (f + k) % 4
            smoke(fr, (m[0] + 1.5 + s * 1.2, m[1] - 3 - s * 5), 1.2 + s * 0.5, 170 - s * 35)
    elif row == "WALK":
        cyc = [((50, 121), (78, 121), 0.0, (100, 124)), ((58, 121), (68, 117), -1.2, (99, 124)),
               ((76, 121), (52, 121), 0.0, (100, 124)), ((66, 117), (60, 121), -1.2, (101, 124))][f]
        b, fr_, bob, BB = cyc
        hip = (63, 85 + bob); lean = 24
        P = nenek_kebaya(fr, hip, lean, 2, [b, fr_], [(54, 83 + bob), (93, 72 + bob)],
                         face_kw=dict(eye="open", mouth="flat"))
        broom(fr, "prop_back", (88, 46 + bob), BB)
        if f in (0, 2): speed_lines(fr, [((34, 70), (42, 70)), ((32, 80), (40, 80))], (250, 248, 235, 150))
    elif row == "ATTACK":
        if f == 0:   # tarik napas, dada membusung
            hip = (60, 83); P = nenek_kebaya(fr, hip, 4, -14, [FB, FF], [(40, 86), (74, 64)],
                                            face_kw=dict(eye="closed", mouth="o", brow=-0.6))
            broom(fr, "prop_back", (60, 46), (24, 112))
            m = P["mouth"]
            for k in range(3):
                fr.line("fx", [(m[0] + 18 - k * 3, m[1] - 8 + k * 6), (m[0] + 9 - k * 2, m[1] - 3 + k * 3), (m[0] + 3, m[1])], 0.9, (250, 248, 235, 190))
        elif f == 1:  # condong, pipi menggembung
            hip = (60, 85); P = nenek_kebaya(fr, hip, 36, 8, [(52, 121), (76, 121)], [(40, 80), (82, 82)],
                                            face_kw=dict(eye="squint", mouth="puff"))
            broom(fr, "prop_back", (58, 62), (18, 100))
            speed_lines(fr, [((28, 52), (40, 54)), ((26, 62), (38, 63)), ((30, 72), (40, 72))])
        elif f == 2:  # semburan api panjang
            hip = (61, 85); P = nenek_kebaya(fr, hip, 30, 4, [(50, 121), (78, 121)], [(40, 82), (86, 80)],
                                            face_kw=dict(eye="squint", mouth="open", brow=1.0))
            broom(fr, "prop_back", (58, 62), (18, 102))
            fire(fr, P["mouth"], 119, wob=0.0)
            for c in [(104, 42), (113, 46), (108, 70), (118, 64)]: ember(fr, c)
        else:         # sisa bara, mulut mengepul
            hip = (61, 85); P = nenek_kebaya(fr, hip, 26, 4, [(50, 121), (76, 121)], [(42, 82), (88, 79)],
                                            face_kw=dict(eye="open", mouth="o"))
            broom(fr, "prop_back", (60, 60), (22, 106))
            m = P["mouth"]
            for i, c in enumerate([(98, 50), (106, 56), (113, 49), (117, 60), (108, 64), (121, 53)]): ember(fr, c, 1.3 - i * 0.08)
            fr.poly("fx", [(m[0], m[1] - 1.5), (m[0] + 7, m[1] - 3), (m[0] + 9, m[1]), (m[0] + 6, m[1] + 2.5), (m[0], m[1] + 1.5)], (250, 150, 40))
            for k in range(3): smoke(fr, (m[0] + 2 + k * 3, m[1] - 4 - k * 5), 1.6 + k * 0.7, 160 - k * 30)
    elif row == "HIT":
        cfg = [dict(lean=-8, tilt=-28, bun=(-3, -3), B=((78, 50), (100, 120)), hip=(58, 84), eye="pain", mouth="open"),
               dict(lean=-4, tilt=-18, bun=(-4, 1), B=((84, 52), (108, 116)), hip=(58, 84), eye="pain", mouth="wavy"),
               dict(lean=4, tilt=-10, bun=(-3, 3), B=((92, 58), (114, 112)), hip=(59, 84), eye="wide", mouth="o"),
               dict(lean=12, tilt=-4, bun=(-2, 2), B=((92, 56), (110, 118)), hip=(60, 84), eye="wide", mouth="flat")][f]
        P = nenek_kebaya(fr, cfg["hip"], cfg["lean"], cfg["tilt"], [(52, 121), (68, 121)],
                         [(44, 74), lerp(cfg["B"][0], cfg["B"][1], 0.33)], bun_off=cfg["bun"], hairpin=(f != 1),
                         face_kw=dict(eye=cfg["eye"], mouth=cfg["mouth"], brow=1.2))
        broom(fr, "prop_back", cfg["B"][0], cfg["B"][1])
        h = P["head"]
        if f == 0:
            pts = [add((h[0] + 12, h[1] - 2), rot((7 if i % 2 == 0 else 3, 0), (0, 0), i * 36)) for i in range(10)]
            fr.poly("fx", pts, (255, 236, 140, 230), outline=False)
            speed_lines(fr, [((h[0] - 18, h[1] - 8), (h[0] - 26, h[1] - 10)), ((h[0] - 18, h[1] + 2), (h[0] - 27, h[1] + 2))])
        if f == 1:  # tusuk konde terlempar
            fr.cap("fx", (h[0] - 22, h[1] - 18), (h[0] - 15, h[1] - 22), 1.0, (214, 172, 58))
        if f >= 2: fr.circ("fx", (h[0] - 10, h[1] - 10), 1.4, (170, 210, 240, 220), outline=False)
    elif row == "BLOCK":
        j = [0, 0.7, 0, -0.7][f]
        hip = (60, 87); P = nenek_kebaya(fr, hip, 14, 6, [(50, 121), (72, 121)], [(76, 70 + j), (96, 66 + j)],
                                        back_hand_front=True, face_kw=dict(eye="squint", mouth="flat", brow=1.2))
        broom(fr, "prop_front", (62, 72 + j), (114, 60 + j))
        if f in (1, 2):
            h = P["head"]; fr.circ("fx", (h[0] - 9, h[1] - 7), 1.3, (170, 210, 240, 230), outline=False)
        if f == 1: speed_lines(fr, [((118, 50), (122, 46)), ((120, 72), (124, 75))], (255, 245, 210, 200))
    elif row == "KO":
        if f == 0:   # limbung
            hip = (60, 84); P = nenek_kebaya(fr, hip, -12, -12, [(56, 121), (70, 121)], [(40, 70), (86, 66)],
                                            face_kw=dict(eye="spiral", mouth="wavy"))
            broom(fr, "prop_back", (86, 52), (118, 100))
            th, piv = -8, (62, 124)
            h = P["head"]
            for i in range(3):
                a = i * 2.1; fr.circ("fx", (h[0] - 2 + math.cos(a) * 11, h[1] - 14 + math.sin(a) * 3), 1.4, (255, 220, 90, 240), outline=False)
        elif f == 1:  # jatuh terduduk
            hip = (58, 112); P = nenek_kebaya(fr, hip, -18, -16, [(84, 121), (90, 121)], [(40, 118), (78, 106)],
                                             face_kw=dict(eye="spiral", mouth="open"))
            broom(fr, "prop_back", (98, 110), (118, 86))
            speed_lines(fr, [((40, 122), (34, 118)), ((88, 122), (96, 118))], (230, 220, 200, 180))
        else:         # telentang lalu diam terkapar
            hip = (78, 84)
            P = nenek_kebaya(fr, hip, 0, 0, [(66, 117), (84, 118)], [(52, 100), (96, 98)],
                             face_kw=dict(eye=("closed" if f == 2 else "x"), mouth=("open" if f == 2 else "flat")))
            th, piv = -90, hip; dx = -8
            broom(fr, "prop_front", (22, 121.5), (108, 121.5), absolute=True)
            if f == 2:
                speed_lines(fr, [((hip[0] + 30, hip[1] - 20), (hip[0] + 26, hip[1] - 28))], (230, 220, 200, 0))
    return fr, th, piv, dx

# ---------------- MAK SEDOT (brawler) ----------------
MS = dict(skin=(184, 126, 88), skin_d=(152, 100, 68), dress=(214, 170, 52), dress_d=(176, 136, 36), flower=(248, 240, 220),
          hijab=(230, 214, 186), hijab_d=(190, 170, 140), sandal=(70, 110, 150), tongue=(228, 108, 138), tongue_d=(176, 66, 98))

def nenek_daster(fr, hip, lean, head_tilt, feet, hands, face_kw=None, back_hand_front=False, hijab_flap=0.0):
    c = MS
    sh = add(hip, vdir(180 - lean, 27))
    t = norm(sub(sh, hip)); n = (-t[1], t[0])
    head = add(sh, vdir(180 - (lean * 0.5 + 8), 12.5))
    # betis + sandal
    knees = []
    for i, F in enumerate(feet):
        hp = add(hip, mul(n, -4 + i * 8))
        K, A = ik(hp, F, 19, 19, -1); knees.append(K)
        fr.cap("core", lerp(K, A, 0.25), A, 5.6, c["skin_d"] if i == 0 else c["skin"])
        sandal(fr, "core", A, c["sandal"])
    # daster A-line
    kx = sorted(knees, key=lambda k: k[0])
    hemB = add(kx[0], (-7, 5)); hemF = add(kx[1], (7, 5))
    fr.poly("core", [add(sh, mul(n, -8.5)), add(sh, mul(n, 9)), add(hip, mul(n, 13)), hemF, hemB, add(hip, mul(n, -13))], c["dress"])
    fr.line("core", [hemB, hemF], 1.4, c["dress_d"])
    for p in [add(hip, mul(n, -6)), add(hip, mul(n, 5)), add(add(hip, mul(t, 11)), mul(n, 1)), lerp(hemB, hemF, 0.3), lerp(hemB, hemF, 0.72)]:
        p = add(p, (0, -3)) if p in (hemB, hemF) else p
        fr.circ("core", p, 1.5, c["flower"], outline=False); fr.circ("core", p, 0.6, c["dress_d"], outline=False)
    # lengan belakang
    hb = arm(fr, "arm_back", add(sh, mul(n, -4)), hands[0], c["dress_d"], c["skin_d"], w=6.4)
    if back_hand_front: fr.circ("arm_front", hb, 2.8, c["skin"])
    # kerudung (menutup leher & bahu) + kepala
    phi = head_tilt
    L = lambda u, v: add(head, rot((u, v), (0, 0), phi))
    fr.poly("core", [L(-11, -2), L(-12 - hijab_flap, 12), add(sh, mul(n, -10)), add(sh, mul(n, 9)), L(9, 9), L(9, 2)], c["hijab"])
    fr.circ("core", head, 11.0, c["hijab"])
    fr.circ("core", L(2.6, 1.6), 7.6, c["skin"], outline=False)
    fr.line("core", [L(-4, -9.5), L(-9.5, -2), L(-8, 8)], 0.7, c["hijab_d"])
    kw = dict(eye="open", mouth="smile", skin=c["skin"], cheek=(214, 122, 108)); kw.update(face_kw or {})
    face(fr, add(head, rot((1.2, 0.4), (0, 0), phi)), 9.2, phi, **kw)
    hf = arm(fr, "arm_front", add(sh, mul(n, 3)), hands[1], c["dress"], c["skin"], w=6.4)
    return dict(sh=sh, head=head, L=L, hf=hf, hb=hb, mouth=L(9.2, 6.4), t=t, n=n)

def tongue(fr, pts, w=3.6, tip=True):
    for a, b in zip(pts[:-1], pts[1:]): fr.cap("fx", a, b, w, MS["tongue"])
    fr.line("fx", pts, 0.6, MS["tongue_d"])
    if tip: fr.circ("fx", pts[-1], w * 0.85, MS["tongue"])

def mak_sedot(row, f):
    fr = Frame(); th = 0.0; piv = (64, 124); dx = 0.0
    FB, FF = (54, 121), (74, 121)
    if row == "IDLE":
        bob = [0, 0.5, 1.0, 0.5][f]
        hip = (62, 86 + bob)
        hand = (88, 84 + bob)
        P = nenek_daster(fr, hip, 10, 2, [FB, FF], [(50, 90 + bob), hand], face_kw=dict(mouth="flat"))
        a = [200, 110, 20, 290][f]
        u = vdir(a, 1)
        plunger(fr, "prop_back", add(hand, mul(u, -16)), add(hand, mul(u, 14)))
        fr.line("fx", [add(hand, rot((0, -21), (0, 0), a + 30 * k)) for k in range(5)], 0.8, (250, 248, 235, 170))
        m = P["mouth"]
        lick = [[add(m, (-1, 0)), add(m, (2.5, -1.5)), add(m, (3.5, -3.0))], [add(m, (-1, 0)), add(m, (3.0, 0.5))],
                [add(m, (-1, 0)), add(m, (2.5, 1.5)), add(m, (2.0, 3.5))], [add(m, (-1, 0)), add(m, (1.5, -0.5))]][f]
        tongue(fr, lick, 2.4)
    elif row == "WALK":
        cyc = [((44, 121), (84, 121), 0.0, 30), ((60, 121), (70, 115), -1.5, 5),
               ((84, 121), (44, 121), 0.0, -25), ((68, 115), (60, 121), -1.5, 5)][f]
        b, ff, bob, sw = cyc
        hip = (64, 86 + bob); hand = (82 + sw * 0.15, 88 + bob)
        nenek_daster(fr, hip, 12, 0, [b, ff], [(48 - sw * 0.1, 88 + bob), hand], face_kw=dict(mouth="smile"))
        u = vdir(sw, 1)
        plunger(fr, "prop_back", add(hand, mul(u, -14)), add(hand, mul(u, 13)))
        if f in (0, 2): speed_lines(fr, [((26, 74), (34, 74)), ((24, 86), (32, 86))], (250, 248, 235, 150))
    elif row == "ATTACK":
        if f == 0:   # plunger ditarik ke belakang
            hip = (60, 86); hand = (44, 76)
            nenek_daster(fr, hip, -4, -6, [(52, 121), (72, 121)], [(40, 82), hand], face_kw=dict(eye="squint", mouth="flat", brow=1.2))
            plunger(fr, "prop_front", (26, 78), (68, 72))
            speed_lines(fr, [((86, 66), (78, 66)), ((88, 76), (80, 76))])
        elif f == 1:  # hentakan ke depan
            hip = (64, 87); hand = (94, 74)
            nenek_daster(fr, hip, 24, 4, [(48, 121), (84, 121)], [(46, 84), hand], face_kw=dict(eye="squint", mouth="open", brow=1.4))
            plunger(fr, "prop_front", (76, 76), (108, 72.5))
            speed_lines(fr, [((40, 62), (52, 64)), ((38, 72), (50, 73)), ((40, 82), (52, 82))])
            pts = [add((124, 72), rot((3, 0), (0, 0), i * 60)) for i in range(6)]
            fr.line("fx", [(121, 62), (124, 58)], 0.9, (255, 245, 210, 220)); fr.line("fx", [(121, 82), (124, 86)], 0.9, (255, 245, 210, 220))
        elif f == 2:  # lidah melesat lurus ke kanan
            hip = (64, 87); hand = (90, 82)
            P = nenek_daster(fr, hip, 22, 2, [(48, 121), (84, 121)], [(46, 84), hand], face_kw=dict(eye="wide", mouth="open"))
            plunger(fr, "prop_back", (72, 88), (106, 92))
            m = P["mouth"]
            tongue(fr, [m, (m[0] + 12, m[1]), (m[0] + 26, m[1]), (120, m[1])], 3.6)
            speed_lines(fr, [((m[0] + 6, m[1] - 6), (m[0] + 24, m[1] - 6)), ((m[0] + 10, m[1] + 6), (m[0] + 28, m[1] + 6))])
        else:         # lidah tertarik kembali
            hip = (63, 87); hand = (86, 80)
            P = nenek_daster(fr, hip, 16, 0, [(50, 121), (80, 121)], [(46, 86), hand], face_kw=dict(eye="open", mouth="open"))
            plunger(fr, "prop_back", (70, 84), (102, 86))
            m = P["mouth"]
            tongue(fr, [m, (m[0] + 6, m[1] - 2), (m[0] + 12, m[1] + 1), (m[0] + 16, m[1] - 3), (m[0] + 14, m[1] - 7)], 3.2)
            fr.line("fx", [(m[0] + 22, m[1] - 2), (m[0] + 30, m[1] - 2)], 0.8, (250, 248, 235, 170))
    elif row == "HIT":
        cfg = [(-14, -20, (56, 84), "wide", 7.0, 2.0), (-10, -14, (56, 84), "wide", 5.0, 3.0),
               (-4, -8, (58, 85), "pain", 3.0, 1.5), (4, -2, (60, 86), "open", 1.5, 0.5)][f]
        lean, tilt, hip, eye, tl, flap = cfg
        P = nenek_daster(fr, hip, lean, tilt, [(48, 121), (68, 121)], [(36, 76), (80, 70)], hijab_flap=flap,
                         face_kw=dict(eye=eye, mouth="open", brow=1.4))
        plunger(fr, "prop_back", (70, 54), (94, 34 + f * 4))
        m = P["mouth"]
        tongue(fr, [m, add(m, (tl * 0.6, tl * 0.5)), add(m, (tl * 0.9, tl * 1.3))], 3.0)
        h = P["head"]
        if f == 0:
            pts = [add((h[0] + 14, h[1] + 4), rot((7 if i % 2 == 0 else 3, 0), (0, 0), i * 36)) for i in range(10)]
            fr.poly("fx", pts, (255, 236, 140, 230), outline=False)
            speed_lines(fr, [((h[0] - 20, h[1] - 6), (h[0] - 28, h[1] - 7)), ((h[0] - 20, h[1] + 6), (h[0] - 29, h[1] + 6))])
        if f in (1, 2): fr.circ("fx", (h[0] - 10, h[1] - 12), 1.5, (170, 210, 240, 230), outline=False)
    elif row == "BLOCK":
        j = [0, 0.7, 0, -0.7][f]
        hip = (60, 88)
        nenek_daster(fr, hip, 8, 4, [(48, 121), (72, 121)], [(76, 72 + j), (84, 70 + j)], back_hand_front=True,
                     face_kw=dict(eye="squint", mouth="flat", brow=1.4))
        plunger(fr, "prop_front", (70, 72 + j), (100, 70 + j))
        if f == 1: speed_lines(fr, [((118, 56), (122, 52)), ((118, 84), (122, 88))], (255, 245, 210, 210))
        if f in (1, 2): fr.circ("fx", (54, 40), 1.4, (170, 210, 240, 230), outline=False)
    elif row == "KO":
        if f == 0:   # berputar limbung
            hip = (62, 86)
            P = nenek_daster(fr, hip, 6, 14, [(56, 121), (70, 121)], [(36, 66), (92, 64)], hijab_flap=3,
                             face_kw=dict(eye="spiral", mouth="wavy"))
            plunger(fr, "prop_back", (86, 72), (98, 52))
            th, piv = 9, (64, 124)
            h = P["head"]
            fr.line("fx", [(h[0] - 14 + math.cos(a / 6) * 16, h[1] - 16 + math.sin(a / 6) * 4) for a in range(0, 30)], 0.9, (250, 248, 235, 200))
            for i in range(3): fr.circ("fx", (h[0] - 6 + i * 8, h[1] - 18 + (i % 2) * 3), 1.4, (255, 220, 90, 240), outline=False)
        elif f == 1:  # jatuh ke depan
            hip = (52, 86)
            nenek_daster(fr, hip, 20, 10, [(50, 121), (62, 116)], [(36, 70), (88, 76)], face_kw=dict(eye="wide", mouth="open"))
            th, piv = 40, (50, 124); dx = -6
            plunger(fr, "fx", (96, 34), (108, 18), absolute=True)
            speed_lines(fr, [((100, 40), (96, 46)), ((112, 38), (110, 44))])
        else:         # tengkurap, plunger menancap
            hip = (50, 86)
            nenek_daster(fr, hip, 0, 0, [(46, 121), (58, 121)], [(70, 100), (78, 104)],
                         face_kw=dict(eye=("closed" if f == 2 else "x"), mouth=("open" if f == 2 else "flat")))
            th, piv = 90, hip; dx = 8
            plunger(fr, "prop_back", (14, 80), (14, 116.8), absolute=True)
            if f == 2:
                speed_lines(fr, [((40, 120), (34, 116)), ((112, 120), (118, 116))], (230, 220, 200, 180))
    return fr, th, piv, dx

def make_atlas(fn):
    atlas = Image.new("RGBA", (4 * C, 6 * C), (0, 0, 0, 0))
    core_atlas = atlas.copy(); body_atlas = atlas.copy()
    for r, row in enumerate(ROWS):
        for f in range(4):
            fr, th, piv, dx = fn(row, f)
            comp, core, body = build_frame(fr, th, piv, dx)
            atlas.paste(comp, (f * C, r * C)); core_atlas.paste(core, (f * C, r * C)); body_atlas.paste(body, (f * C, r * C))
    return atlas, core_atlas, body_atlas

if __name__ == "__main__":
    outdir = sys.argv[1]
    for slug, fn in [("mbah-ijuk", mbah_ijuk), ("mak-sedot", mak_sedot)]:
        a, core, body = make_atlas(fn)
        os.makedirs(os.path.join(outdir, slug), exist_ok=True)
        a.save(os.path.join(outdir, slug, "atlas.png"), optimize=True)
        if len(sys.argv) > 2:  # topeng uji (tidak masuk paket)
            core.save(os.path.join(sys.argv[2], slug + "-core.png")); body.save(os.path.join(sys.argv[2], slug + "-body.png"))
        print("atlas", slug, a.size)
