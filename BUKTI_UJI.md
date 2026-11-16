# BUKTI UJI — pas-paket-laga

Dijalankan 16-11-2026 di sandbox (Python 3 + Pillow). Semua perintah bisa diulang dari folder paket:

```bash
python3 alat/pas_validate.py conformance <standar-pas-1.0>/standar/conformance.json
python3 alat/gen_karakter.py karakter /tmp/topeng   # membuat ulang atlas + topeng uji
python3 alat/gen_manifest.py karakter
python3 alat/pas_validate.py paket karakter/mbah-ijuk /tmp/topeng
python3 alat/pas_validate.py paket karakter/mak-sedot /tmp/topeng
python3 alat/gen_arena.py alat/pasar_sumber_ai.jpg arena/pasar/background-pasar.png
python3 alat/gen_preview.py karakter arena/pasar/background-pasar.png previews
```

**Yang tidak diuji:** paket ini belum dimuat oleh engine/renderer PAS sungguhan, karena kode pemuat sprite (`src/lib/pas/`) tidak ada di arsip yang diterima. Pratinjau GIF adalah simulasi aturan mandat, bukan tangkapan engine.
Pemeriksaan "kaki menapak" dan "tubuh inti" memakai topeng lapisan tubuh yang dibuat skrip gambar (bukan menebak dari gambar akhir).

Catatan proses: pada putaran pertama pemeriksa menemukan 2 frame Mbah Ijuk yang menyentuh tepi kotak (semburan api `ATTACK` frame 3 dan sapu `KO` frame 2). Keduanya diperbaiki, lalu semua uji dijalankan ulang.

## 1. Kesesuaian pemeriksa terhadap standar/conformance.json
```
LULUS V01 Paket minimal valid (tanpa license & integrity → hanya peringatan)
LULUS V02 Paket lengkap valid: $schema, license, integrity, ekstensi x-*
LULUS V03 Non-humanoid pendek: height_scale 0.75, anchor di tepi frame
LULUS V04 Klip berbagi baris atlas → valid dengan peringatan
LULUS N01 Bukan objek (array)
LULUS N02 Kunci gameplay di akar: damage
LULUS N03 Kunci gameplay bersarang: clips.ATTACK.hitbox
LULUS N04 Kunci gameplay huruf besar: HP
LULUS N05 Kunci gameplay disembunyikan di ekstensi: x-meta.speed
LULUS N06 Kunci tak dikenal di akar
LULUS N07 State tak dikenal: ATTACK_HEAVY
LULUS N08 Kolom wajib hilang: id
LULUS N09 Versi lebih baru: pas 2.0
LULUS N10 id bukan domain-balik
LULUS N11 name kosong
LULUS N12 profile tidak didukung
LULUS N13 base_class bukan kelas engine
LULUS N14 atlas keluar folder paket (..)
LULUS N15 atlas URL absolut ke domain lain
LULUS N16 atlas format tak didukung (.gif)
LULUS N17 frame terlalu kecil
LULUS N18 frame pecahan
LULUS N19 anchor di luar kotak frame
LULUS N20 height_scale terlalu besar
LULUS N21 Klip KO hilang
LULUS N22 Klip tanpa loop
LULUS N23 integrity.atlas format salah
LULUS N24 Kunci gameplay + kunci tak dikenal sekaligus
LULUS A01 Atlas pas: 4 frame × 128, 6 baris × 128
LULUS A02 Atlas terlalu sempit (frame keluar gambar)
LULUS A03 Atlas terlalu pendek (baris KO hilang)
LULUS A04 Atlas melebihi 4096 px
KESESUAIAN: 32/32 kasus cocok
exit=0
```
## Paket mbah-ijuk
```
MANIFEST+ATLAS (aturan SPEC): {'ok': True, 'errors': [], 'warnings': []}
LULUS ATLAS-UKURAN - (512, 768)
LULUS D6-RGBA - RGBA
LULUS D6-SUDUT-TRANSPARAN - alpha sudut=[0, 0, 0, 0]
LULUS D1-ANCHOR - anchor=(64,124) frame=128x128
LULUS INTEGRITY - sha256-qsJQWb/C/xk3VVAw0+IlJWJUbBfx/U6WCfAt4lGF7ds=
TAMPILAN: 110/110 pemeriksaan lulus
exit=0
```
## Paket mak-sedot
```
MANIFEST+ATLAS (aturan SPEC): {'ok': True, 'errors': [], 'warnings': []}
LULUS ATLAS-UKURAN - (512, 768)
LULUS D6-RGBA - RGBA
LULUS D6-SUDUT-TRANSPARAN - alpha sudut=[0, 0, 0, 0]
LULUS D1-ANCHOR - anchor=(64,124) frame=128x128
LULUS INTEGRITY - sha256-u0ejuNMqIDQzUI/JIlBTZlOs0OKTHW4wR+HIR3BtCrI=
TAMPILAN: 110/110 pemeriksaan lulus
exit=0
```
## Arena
```
ukuran (800, 360) mode RGB
arena.json {'x-pas-arena': 'draft-1', 'name': 'Pasar Tradisional', 'image': 'background-pasar.png', 'size': {'w': 800, 'h': 360}, 'floor_y': 300, 'license': 'CC-BY-4.0'}
warna rata-rata baris 299 (latar): [106.1, 85.2, 72.1]  baris 300 (tepi lantai): [152.0, 131.0, 123.0]
lantai y>=301 seragam (simpangan baku RGB): [12.0, 9.8, 8.1]
LULUS ukuran 800x360
LULUS floor_y = 300
```
## Kunci manifest (cek kunci terlarang dan kolom)
```
mbah-ijuk ['anchor', 'atlas', 'author', 'binds_to', 'clips', 'frame', 'height_scale', 'id', 'integrity', 'license', 'name', 'pas', 'profile', 'x-deskripsi', 'x-modul']
mak-sedot ['anchor', 'atlas', 'author', 'binds_to', 'clips', 'frame', 'height_scale', 'id', 'integrity', 'license', 'name', 'pas', 'profile', 'x-deskripsi', 'x-modul']
```
## Dapat dibuat ulang (dua kali jalan, sidik sama)
```
bb47a3b8d32a203433508fc92250536653acd0e2931d6e3047e1c847706d0ab2  repro/mak-sedot/atlas.png
aac25059bfc2ff1937555030d3e2252562546c17f1fd4e9609f02de25185eddb  repro/mbah-ijuk/atlas.png
bb47a3b8d32a203433508fc92250536653acd0e2931d6e3047e1c847706d0ab2  pas-paket-laga/karakter/mak-sedot/atlas.png
aac25059bfc2ff1937555030d3e2252562546c17f1fd4e9609f02de25185eddb  pas-paket-laga/karakter/mbah-ijuk/atlas.png
b82c774719b183fb022ab16cfa917b534f09a07c41703fb2e47e3f6bc5c41b43  repro/bg.png
b82c774719b183fb022ab16cfa917b534f09a07c41703fb2e47e3f6bc5c41b43  pas-paket-laga/arena/pasar/background-pasar.png
```

## Uji negatif (pemeriksa harus menolak)
```
a) id disalin dari mandat apa adanya (io.github.NAMA...)
MANIFEST+ATLAS (aturan SPEC): {'ok': False, 'errors': ['PAS-E020'], 'warnings': []}
b) satu piksel atlas diubah setelah integrity dihitung
MANIFEST+ATLAS (aturan SPEC): {'ok': False, 'errors': ['PAS-E073'], 'warnings': []}
c) klip tambahan JUMP + x-catatan.speed
MANIFEST+ATLAS (aturan SPEC): {'ok': False, 'errors': ['PAS-E002', 'PAS-E003'], 'warnings': []}
```
