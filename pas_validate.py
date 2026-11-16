"""Pemeriksa PAS 1.0 (port Python dari aturan SPEC.md) + pemeriksaan tampilan modul (D1-D6).
BUKAN validator referensi (yang resmi: src/lib/pas/validate.ts di engine). Dipakai untuk bukti
bahwa paket ini lolos aturan yang sama; kesesuaiannya diuji terhadap standar/conformance.json.
Pemakaian:
  python3 pas_validate.py conformance <conformance.json>
  python3 pas_validate.py paket <folder_paket>   (manifest.json + atlas)"""
import json, re, sys, os, hashlib, base64

FORBIDDEN = {"damage", "dmg", "hp", "health", "maxhp", "attack_power", "defense", "armor", "hitbox", "hurtbox", "pushbox",
             "collision", "hitstun", "blockstun", "startup", "active", "recovery", "priority", "speed", "reach", "range",
             "cooldown", "frame_data", "frame_events", "knockback", "win", "winner", "script", "code", "eval", "onload", "handler"}
STATES = ["IDLE", "WALK", "ATTACK", "HIT", "BLOCK", "KO"]
CLASSES = {"brawler", "swordsman", "gunslinger", "mage"}
TOP = {"$schema", "pas", "id", "name", "author", "license", "profile", "binds_to", "atlas", "frame", "anchor", "height_scale", "clips", "integrity"}
SUB = {"binds_to": {"base_class"}, "frame": {"w", "h"}, "anchor": {"x", "y"}, "integrity": {"atlas"}}
REQUIRED = ["pas", "id", "name", "profile", "binds_to", "atlas", "frame", "anchor", "height_scale", "clips"]
MAX_BYTES = 64 * 1024

def is_int(v): return isinstance(v, int) and not isinstance(v, bool)
def is_num(v): return isinstance(v, (int, float)) and not isinstance(v, bool)
def text_ok(v): return isinstance(v, str) and 1 <= len(v) <= 64 and v.strip() != ""

def walk_forbidden(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k.lower() in FORBIDDEN: return True
            if walk_forbidden(v): return True
    elif isinstance(o, list):
        return any(walk_forbidden(x) for x in o)
    return False

def validate_manifest(m, raw_size=None):
    errs, warns = [], []
    if raw_size is not None and raw_size > MAX_BYTES: return {"ok": False, "errors": ["PAS-E004"], "warnings": []}
    if not isinstance(m, dict): return {"ok": False, "errors": ["PAS-E001"], "warnings": []}
    E = lambda c: errs.append(c) if c not in errs else None
    if walk_forbidden(m): E("PAS-E002")
    # kunci tak dikenal (level atas dan sub-objek); x-* bebas
    def unknown(obj, allowed):
        # kunci terlarang sudah dilaporkan sebagai E002, tidak dihitung ulang sebagai E003
        return any(not (k in allowed or k.startswith("x-") or k.lower() in FORBIDDEN) for k in obj)
    if unknown(m, TOP): E("PAS-E003")
    for k, allowed in SUB.items():
        if isinstance(m.get(k), dict) and unknown(m[k], allowed): E("PAS-E003")
    if isinstance(m.get("clips"), dict):
        if unknown(m["clips"], set(STATES)): E("PAS-E003")
        for st in STATES:
            c = m["clips"].get(st)
            if isinstance(c, dict) and unknown(c, {"row", "frames", "fps", "loop"}): E("PAS-E003")
    if any(k not in m for k in REQUIRED): E("PAS-E005")
    if "pas" in m and m["pas"] != "1.0": E("PAS-E010")
    if "id" in m and not (isinstance(m["id"], str) and len(m["id"]) <= 128 and re.fullmatch(r"[a-z0-9]+(\.[a-z0-9-]+){2,}", m["id"])): E("PAS-E020")
    if "name" in m and not text_ok(m["name"]): E("PAS-E021")
    for k in ("author", "license"):
        if k in m and not text_ok(m[k]): E("PAS-E022")
    if "profile" in m and m["profile"] != "2d-frames@1": E("PAS-E030")
    if "binds_to" in m:
        b = m["binds_to"]
        if not (isinstance(b, dict) and b.get("base_class") in CLASSES): E("PAS-E031")
    if "atlas" in m:
        a = m["atlas"]
        if not (isinstance(a, str) and re.fullmatch(r"(?!/)(?!.*\.\.)(?!.*://)[A-Za-z0-9._/-]+\.(png|webp|PNG|WEBP)", a)): E("PAS-E040")
    fw = fh = None
    if "frame" in m:
        f = m["frame"]
        if isinstance(f, dict) and is_int(f.get("w")) and is_int(f.get("h")) and 16 <= f["w"] <= 1024 and 16 <= f["h"] <= 1024: fw, fh = f["w"], f["h"]
        else: E("PAS-E041")
    if "anchor" in m:
        an = m["anchor"]
        ok = isinstance(an, dict) and is_int(an.get("x")) and is_int(an.get("y"))
        if ok and fw is not None: ok = 0 <= an["x"] <= fw and 0 <= an["y"] <= fh
        if not ok: E("PAS-E042")
    if "height_scale" in m and not (is_num(m["height_scale"]) and 0.75 <= m["height_scale"] <= 1.3): E("PAS-E043")
    if "clips" in m:
        cl = m["clips"]
        if not isinstance(cl, dict) or any(s not in cl for s in STATES): E("PAS-E050")
        if isinstance(cl, dict):
            for s in STATES:
                c = cl.get(s)
                if c is None: continue
                if not (isinstance(c, dict) and is_int(c.get("row")) and 0 <= c["row"] <= 63 and is_int(c.get("frames")) and 1 <= c["frames"] <= 64
                        and is_num(c.get("fps")) and 1 <= c["fps"] <= 60 and isinstance(c.get("loop"), bool)): E("PAS-E051")
    if "integrity" in m:
        i = m["integrity"]
        if not (isinstance(i, dict) and isinstance(i.get("atlas"), str) and re.fullmatch(r"sha256-[A-Za-z0-9+/]{43}=", i["atlas"])): E("PAS-E060")
    if not errs:
        if "license" not in m: warns.append("PAS-W001")
        rows = [m["clips"][s]["row"] for s in STATES]
        if len(set(rows)) < len(rows): warns.append("PAS-W002")
        if "integrity" not in m: warns.append("PAS-W003")
    return {"ok": not errs, "errors": errs, "warnings": warns}

def validate_atlas_size(m, w, h):
    errs = []
    if w > 4096 or h > 4096: return ["PAS-E072"]
    need_w = max(m["clips"][s]["frames"] for s in STATES) * m["frame"]["w"]
    need_h = (max(m["clips"][s]["row"] for s in STATES) + 1) * m["frame"]["h"]
    if w < need_w or h < need_h: errs.append("PAS-E071")
    return errs

def sri(path): return "sha256-" + base64.b64encode(hashlib.sha256(open(path, "rb").read()).digest()).decode()

def run_conformance(path):
    c = json.load(open(path)); fails = 0; n = 0
    for case in c["manifest_cases"]:
        n += 1; m = case["manifest"]
        if isinstance(m, str):
            try: m = json.loads(m)
            except Exception: m = None
        r = validate_manifest(m); ex = case["expect"]
        ok = r["ok"] == ex["ok"] and sorted(r["errors"]) == sorted(ex["errors"]) and (ex["warnings"] is None or sorted(r["warnings"]) == sorted(ex["warnings"]))
        print(("LULUS " if ok else "GAGAL ") + case["id"], case["description"], "->", r)
        fails += not ok
    base = c["atlas_base_manifest"]
    for case in c["atlas_cases"]:
        n += 1; e = validate_atlas_size(base, case["width"], case["height"]); ok = sorted(e) == sorted(case["expect"]["errors"])
        print(("LULUS " if ok else "GAGAL ") + case["id"], case["description"], "->", e); fails += not ok
    print(f"KESESUAIAN: {n - fails}/{n} kasus cocok")
    return fails == 0

# ---------- pemeriksaan tampilan modul (D1-D6) ----------
FPS_RANGE = {"IDLE": (6, 8), "WALK": (8, 10), "ATTACK": (10, 12), "HIT": (8, 10), "BLOCK": (8, 10), "KO": (8, 10)}
LOOP = {"IDLE": True, "WALK": True, "BLOCK": True, "ATTACK": False, "HIT": False, "KO": False}

def check_display(folder, masks_dir=None):
    from PIL import Image
    m = json.load(open(os.path.join(folder, "manifest.json")))
    hasil = []
    def rec(kode, ok, ket): hasil.append((kode, ok, ket))
    im = Image.open(os.path.join(folder, m["atlas"]))
    fw, fh = m["frame"]["w"], m["frame"]["h"]; ax, ay = m["anchor"]["x"], m["anchor"]["y"]
    rec("ATLAS-UKURAN", im.size == (512, 768), f"{im.size}")
    rec("D6-RGBA", im.mode == "RGBA", im.mode)
    A = im.getchannel("A"); W, H = im.size
    corners = [A.getpixel(p) for p in [(0, 0), (W - 1, 0), (0, H - 1), (W - 1, H - 1)]]
    rec("D6-SUDUT-TRANSPARAN", all(v == 0 for v in corners), f"alpha sudut={corners}")
    rec("D1-ANCHOR", ax == fw // 2 and fh - 4 <= ay <= fh, f"anchor=({ax},{ay}) frame={fw}x{fh}")
    # bukti tiap frame
    body = Image.open(os.path.join(masks_dir, os.path.basename(folder.rstrip('/')) + "-body.png")).getchannel("A") if masks_dir else None
    core = Image.open(os.path.join(masks_dir, os.path.basename(folder.rstrip('/')) + "-core.png")).getchannel("A") if masks_dir else None
    for s in STATES:
        c = m["clips"][s]
        lo, hi = FPS_RANGE[s]
        rec(f"D5-FPS-{s}", lo <= c["fps"] <= hi, f"fps={c['fps']} (rentang {lo}-{hi})")
        rec(f"D4-LOOP-{s}", c["loop"] == LOOP[s], f"loop={c['loop']}")
        for f in range(c["frames"]):
            box = (f * fw, c["row"] * fh, (f + 1) * fw, (c["row"] + 1) * fh)
            cell = A.crop(box)
            px = cell.load()
            border = [px[x, y] for x in range(fw) for y in (0, 1)] + [px[x, y] for y in range(fh) for x in (0, 1, fw - 2, fw - 1)]
            rec(f"D2-TIDAK-TERPOTONG-{s}{f}", max(border) == 0, "tepi 2 px kotak transparan" if max(border) == 0 else "ada piksel di tepi kotak")
            below = max(px[x, y] for x in range(fw) for y in range(ay, fh)) if ay < fh else 0
            rec(f"D6-TANPA-BAYANGAN-{s}{f}", below == 0, f"alpha maks di bawah garis lantai={below}")
            if body is not None:
                bb = body.crop(box).point(lambda v: 255 if v > 0 else 0).getbbox()
                rec(f"D1-KAKI-MENAPAK-{s}{f}", bb is not None and bb[3] == ay, f"baris terbawah tubuh={bb[3] - 1 if bb else None} (harus {ay - 1})")
            if core is not None and not (s == "KO" and f >= 1):  # KO terduduk/terbaring dikecualikan (D2.4)
                cb = core.crop(box).point(lambda v: 255 if v > 0 else 0).getbbox()
                rec(f"D2-INTI-{s}{f}", cb is not None and cb[0] >= 24 and cb[2] <= 104, f"tubuh inti x={cb[0]}..{cb[2] - 1} (pita 24..103)")
    integ = m.get("integrity", {}).get("atlas")
    rec("INTEGRITY", integ == sri(os.path.join(folder, m["atlas"])), f"{integ}")
    return hasil

if __name__ == "__main__":
    if sys.argv[1] == "conformance":
        sys.exit(0 if run_conformance(sys.argv[2]) else 1)
    elif sys.argv[1] == "paket":
        folder = sys.argv[2]; masks = sys.argv[3] if len(sys.argv) > 3 else None
        raw = open(os.path.join(folder, "manifest.json"), "rb").read()
        m = json.loads(raw); r = validate_manifest(m, len(raw))
        from PIL import Image
        im = Image.open(os.path.join(folder, m["atlas"]))
        r["errors"] += validate_atlas_size(m, *im.size)
        if os.path.getsize(os.path.join(folder, m["atlas"])) > 8 * 1024 * 1024: r["errors"].append("PAS-E072")
        if "integrity" in m and m["integrity"]["atlas"] != sri(os.path.join(folder, m["atlas"])): r["errors"].append("PAS-E073")
        r["ok"] = not r["errors"]
        print("MANIFEST+ATLAS (aturan SPEC):", r)
        hasil = check_display(folder, masks)
        bad = [h for h in hasil if not h[1]]
        for kode, ok, ket in hasil:
            if not ok or not kode[-1].isdigit(): print(("LULUS " if ok else "GAGAL ") + kode, "-", ket)
        print(f"TAMPILAN: {len(hasil) - len(bad)}/{len(hasil)} pemeriksaan lulus")
        sys.exit(0 if r["ok"] and not bad else 1)
