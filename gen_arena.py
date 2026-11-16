"""Membuat arena/pasar/background-pasar.png (800x360, lantai mulai tepat y=300).
Sumber lukisan: pasar_sumber_ai.jpg (dibuat dengan generator gambar AI, 1600x720,
lalu disunting AI untuk menambah pedagang/pembeli samar).
Langkah: skala agar tepi lantai sumber (y=524) jatuh di y=300, potong tengah 800 px,
buramkan latar (lebih kuat di pita tengah y 120-300), lalu gambar ulang lantai paving
dari y=300 ke bawah dengan Pillow agar garis lantai tepat."""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
SRC = sys.argv[1] if len(sys.argv) > 1 else "pasar_sumber_ai.jpg"
OUT = sys.argv[2] if len(sys.argv) > 2 else "background-pasar.png"
W, H, FLOOR = 800, 360, 300
src = Image.open(SRC).convert("RGB")
# tepi lantai sumber = lonjakan terang baris terbesar di 60-80% tinggi gambar (diukur otomatis)
_g = np.asarray(src.convert("L")).astype(float).mean(axis=1)
_lo, _hi = int(src.height * 0.6), int(src.height * 0.8)
EDGE_SRC = _lo + int(np.argmax(np.diff(_g[_lo:_hi]))) + 1
print("tepi lantai sumber y =", EDGE_SRC)
s = FLOOR / EDGE_SRC
im = src.resize((round(src.width * s), round(src.height * s)), Image.LANCZOS)
x0 = (im.width - W) // 2
im = im.crop((x0, 0, x0 + W, H))
# 1) seluruh latar agak buram (petarung lebih menonjol)
bg = im.filter(ImageFilter.GaussianBlur(1.6))
# 2) pita tengah y 120-300 dibuat tenang: blur lebih kuat + kontras/saturasi turun, tepi lembut
calm = im.filter(ImageFilter.GaussianBlur(4.5))
calm = ImageEnhance.Contrast(calm).enhance(0.8)
calm = ImageEnhance.Color(calm).enhance(0.8)
mask = Image.new("L", (W, H), 0)
md = ImageDraw.Draw(mask)
md.rectangle((0, 120, W, FLOOR), fill=200)
mask = mask.filter(ImageFilter.GaussianBlur(18))
m = np.asarray(mask).copy(); m[FLOOR:, :] = 0; mask = Image.fromarray(m)
bg = Image.composite(calm, bg, mask)
# 3) lantai semen/paving: ambil warna rata-rata lantai sumber, gambar paving + tekstur halus
arr = np.asarray(bg).astype(np.float32)
floor_src = np.asarray(im).astype(np.float32)[FLOOR:, :, :]
base = floor_src.reshape(-1, 3).mean(axis=0)
rng = np.random.default_rng(20261116)
fl = np.zeros((H - FLOOR, W, 3), np.float32)
for y in range(H - FLOOR):
    shade = 0.92 + 0.10 * (y / (H - FLOOR))  # sedikit lebih terang ke depan
    fl[y, :, :] = base * shade * np.array([1.04, 1.0, 0.94], np.float32)  # semen hangat
fl += rng.normal(0, 5, fl.shape)  # butir semen
# campur sedikit tekstur sumber agar menyatu dengan lukisan
fl = fl * 0.75 + np.asarray(Image.fromarray(floor_src.clip(0,255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1))).astype(np.float32) * 0.25
floor_img = Image.fromarray(fl.clip(0, 255).astype(np.uint8))
fd = ImageDraw.Draw(floor_img)
joint = tuple(int(c * 0.72) for c in base)
# garis paving horizontal (makin renggang ke depan = perspektif ringan)
ys = [0, 9, 21, 37, 59]
for yy in ys[1:]:
    fd.line((0, yy, W, yy), fill=joint, width=1)
# garis paving vertikal berselang-seling per lajur, menyebar dari titik hilang di tengah
for i, (ya, yb) in enumerate(zip(ys[:-1], ys[1:] + [H - FLOOR])):
    step = 40 + i * 14
    off = (i % 2) * step // 2
    for x in range(-step, W + step, step):
        xa = 400 + (x + off - 400) * (1 + ya / 60)
        xb = 400 + (x + off - 400) * (1 + yb / 60)
        fd.line((xa, ya, xb, yb), fill=joint, width=1)
# tepi lantai: garis terang tipis TEPAT di y=300 (baris pertama lantai)
edge = tuple(min(255, int(c * 1.18)) for c in base)
fd.line((0, 0, W, 0), fill=edge, width=1)
out = bg.copy()
out.paste(floor_img, (0, FLOOR))
# bayangan lembut di kaki latar tepat di atas lantai (masih bagian latar, y<300)
sh = Image.new("L", (W, H), 0); ImageDraw.Draw(sh).rectangle((0, FLOOR - 6, W, FLOOR - 1), fill=60)
sh = sh.filter(ImageFilter.GaussianBlur(3)); s2 = np.asarray(sh).copy(); s2[FLOOR:, :] = 0
out = Image.composite(Image.new("RGB", (W, H), (30, 22, 18)), out, Image.fromarray(s2))
out.save(OUT, optimize=True)
print("tersimpan", OUT, out.size)
