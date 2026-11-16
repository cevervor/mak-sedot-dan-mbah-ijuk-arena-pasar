"""Pratinjau GIF: meniru aturan tampil di mandat (kanvas 800x360, lantai y=300, 30 detak/dtk,
skala 1,3 x height_scale, anchor ditempel ke lantai, Pemain 2 dicerminkan). Ini simulasi, bukan engine."""
import json, sys, os
from PIL import Image, ImageDraw
root, bgp, out = sys.argv[1], sys.argv[2], sys.argv[3]
STATES = ["IDLE", "WALK", "ATTACK", "HIT", "BLOCK", "KO"]
TICKS_PER_STATE = 36  # 1,2 detik per keadaan
bg = Image.open(bgp).convert("RGBA")
os.makedirs(out, exist_ok=True)
for slug in ["mbah-ijuk", "mak-sedot"]:
    m = json.load(open(os.path.join(root, slug, "manifest.json")))
    atlas = Image.open(os.path.join(root, slug, m["atlas"])).convert("RGBA")
    fw, fh = m["frame"]["w"], m["frame"]["h"]; ax, ay = m["anchor"]["x"], m["anchor"]["y"]
    s = 1.3 * m["height_scale"]
    frames = []
    for st in STATES:
        c = m["clips"][st]
        for tick in range(0, TICKS_PER_STATE, 2):
            t = tick / 30.0
            k = int(t * c["fps"])
            idx = k % c["frames"] if c["loop"] else min(k, c["frames"] - 1)
            cell = atlas.crop((idx * fw, c["row"] * fh, (idx + 1) * fw, (c["row"] + 1) * fh))
            cell = cell.resize((round(fw * s), round(fh * s)), Image.BILINEAR)
            img = bg.copy()
            for px, mirror in [(250, False), (550, True)]:
                spr = cell.transpose(Image.FLIP_LEFT_RIGHT) if mirror else cell
                axs = (fw - ax) * s if mirror else ax * s
                img.alpha_composite(spr, (round(px - axs), round(300 - ay * s)))
            d = ImageDraw.Draw(img)
            d.rectangle((8, 8, 300, 26), fill=(20, 16, 14, 190))
            d.text((14, 12), f"{m['name']} - {st}  frame {idx + 1}/{c['frames']}  ({c['fps']} fps, loop={str(c['loop']).lower()})", fill=(255, 240, 200, 255))
            d.text((210, 330), "P1 (asli)", fill=(255, 255, 255, 255)); d.text((510, 330), "P2 (dicerminkan)", fill=(255, 255, 255, 255))
            frames.append(img.convert("RGB").quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE))
    p = os.path.join(out, slug + ".gif")
    frames[0].save(p, save_all=True, append_images=frames[1:], duration=67, loop=0, optimize=True)
    print(p, len(frames), "frame", os.path.getsize(p) // 1024, "KB")
