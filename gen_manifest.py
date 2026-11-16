"""Menulis manifest.json kedua karakter + integrity.atlas dari atlas.png yang sudah jadi."""
import json, sys, os, hashlib, base64
root = sys.argv[1]
def sri(p): return "sha256-" + base64.b64encode(hashlib.sha256(open(p, "rb").read()).digest()).decode()
CLIPS = lambda atk: {
    "IDLE":   {"row": 0, "frames": 4, "fps": 7,   "loop": True},
    "WALK":   {"row": 1, "frames": 4, "fps": 9,   "loop": True},
    "ATTACK": {"row": 2, "frames": 4, "fps": atk, "loop": False},
    "HIT":    {"row": 3, "frames": 4, "fps": 9,   "loop": False},
    "BLOCK":  {"row": 4, "frames": 4, "fps": 8,   "loop": True},
    "KO":     {"row": 5, "frames": 4, "fps": 8,   "loop": False}}
DATA = {
  "mbah-ijuk": dict(name="Mbah Ijuk", cls="mage", hs=0.9, atk=11,
                    desc="Nenek berkebaya dan bersanggul, bersenjata sapu ijuk, menyembur api dari mulut."),
  "mak-sedot": dict(name="Mak Sedot", cls="brawler", hs=0.95, atk=12,
                    desc="Nenek berdaster dan berkerudung, bersenjata penyedot WC, lidah panjang seperti bunglon."),
}
for slug, d in DATA.items():
    folder = os.path.join(root, slug)
    m = {
        "pas": "1.0",
        "profile": "2d-frames@1",
        "id": f"io.github.nama.{slug}",
        "name": d["name"],
        "author": "nama",
        "license": "CC-BY-4.0",
        "binds_to": {"base_class": d["cls"]},
        "atlas": "atlas.png",
        "frame": {"w": 128, "h": 128},
        "anchor": {"x": 64, "y": 124},
        "height_scale": d["hs"],
        "clips": CLIPS(d["atk"]),
        "integrity": {"atlas": sri(os.path.join(folder, "atlas.png"))},
        "x-modul": "MODUL_STANDAR_ASET_KARAKTER_PAS_1.0_rev2",
        "x-deskripsi": d["desc"],
    }
    with open(os.path.join(folder, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(m, fh, ensure_ascii=False, indent=2); fh.write("\n")
    print(slug, m["integrity"]["atlas"])
