# MODUL STANDAR ASET KARAKTER — PAS 1.0 (profil `2d-frames@1`)

> **REKONSTRUKSI.** Berkas asli modul ini hilang. Isi di bawah disusun ulang pada 16-11-2026 hanya dari sumber yang tersedia:
> `standar-pas-1.0/standar/SPEC.md` (sidik SHA-256 cocok dengan `SHA256SUMS`), `standar-pas-1.0/BACA-SAYA.md`,
> `standar-pas-1.0/templat-karakter/manifest.json`, dan `DOSIER_AUDIT_STANDAR_ASET_PAS_v1`.
> Tidak ada aturan baru yang ditambahkan di luar sumber tersebut. Bila berkas asli ditemukan, berkas asli yang berlaku.
> **Status:** NOT_RC_NORMATIVE — belum disahkan pemilik.

## 1. Tujuan

Modul ini memandu kreator (manusia atau AI) membuat paket karakter yang bisa dipakai engine laga.
Kreator boleh berkarya berbeda-beda, tetapi karyanya wajib berbicara satu bahasa yang dipahami engine.

## 2. Batas otoritas

1. Paket PAS adalah kulit visual saja.
2. Paket dilarang menentukan damage, HP, kemenangan, prioritas, tabrakan, kecepatan, atau menjalankan kode.
3. Engine adalah satu-satunya otoritas laga.
4. Setiap paket menempel ke tepat satu kelas engine lewat `binds_to.base_class`.
5. Kelas menentukan cara bertarung; paket hanya menentukan rupa.
6. Bentuk tubuh bebas: humanoid, hewan, lendir, mesin, apa pun — selama bisa digambar sebagai frame di atlas.

## 3. Kelas engine

Ada empat kelas: `brawler`, `swordsman`, `gunslinger`, `mage`.
Kelas baru tidak bisa dibuat lewat paket.

## 4. Isi paket

Satu folder berisi `manifest.json` dan satu atlas `.png` atau `.webp`. `README.md` dan `previews/` boleh ada dan diabaikan engine.
Jalur atlas harus relatif, tidak diawali `/`, dan tidak memuat `..`.

## 5. Kolom manifest

| Kunci | Wajib | Aturan |
|---|---|---|
| `pas` | WAJIB | Tepat `"1.0"` |
| `id` | WAJIB | Domain-balik huruf kecil, ≥3 ruas, contoh `io.github.nama.karakter` |
| `name` | WAJIB | Teks 1–64 karakter |
| `author` | BOLEH | Teks 1–64 karakter |
| `license` | SEBAIKNYA | Mis. `CC-BY-4.0` |
| `profile` | WAJIB | Tepat `"2d-frames@1"` |
| `binds_to.base_class` | WAJIB | Salah satu dari empat kelas |
| `atlas` | WAJIB | Jalur relatif ke atlas |
| `frame.w`, `frame.h` | WAJIB | Bilangan bulat 16–1024 |
| `anchor.x`, `anchor.y` | WAJIB | Di dalam kotak frame. Titik kaki yang menapak lantai |
| `height_scale` | WAJIB | 0,75–1,30 |
| `clips` | WAJIB | Tepat enam state |
| `integrity.atlas` | SEBAIKNYA | `sha256-<base64>` dari berkas atlas |
| `x-…` | BOLEH | Catatan bebas, diabaikan engine |

Kunci lain ditolak (`PAS-E003`).

### 5.1 Kunci terlarang

`damage`, `dmg`, `hp`, `health`, `maxhp`, `attack_power`, `defense`, `armor`, `hitbox`, `hurtbox`, `pushbox`, `collision`, `hitstun`, `blockstun`, `startup`, `active`, `recovery`, `priority`, `speed`, `reach`, `range`, `cooldown`, `frame_data`, `frame_events`, `knockback`, `win`, `winner`, `script`, `code`, `eval`, `onload`, `handler` — dilarang di level mana pun, termasuk di dalam `x-…`, tanpa memandang huruf besar/kecil (`PAS-E002`).

## 6. Atlas

1. Atlas adalah kisi frame. Kolom ke-i dan baris ke-r berada di `x = i·frame.w`, `y = r·frame.h`.
2. Maksimal 4096 piksel per sisi dan 8 MB.
3. Latar sebaiknya transparan.
4. Karakter digambar menghadap ke kanan; engine membalik gambar untuk sisi kiri.

## 7. Enam state

| State | Arti | Saran |
|---|---|---|
| `IDLE` | Diam siaga | `loop: true` |
| `WALK` | Bergerak maju/mundur | `loop: true` |
| `ATTACK` | Menyerang | `loop: false` |
| `HIT` | Terkena serangan | `loop: false` |
| `BLOCK` | Menangkis | `loop: true` |
| `KO` | Kalah | `loop: false`, berhenti di frame terakhir |

Setiap klip: `row` (0–63), `frames` (1–64), `fps` (1–60), `loop` (true/false).
Waktu dan lamanya state ditentukan engine. Klip hanya disampling; panjang animasi tidak memperlambat atau mempercepat laga.

## 8. Langkah membuat karakter dari templat

1. Ganti `atlas.png` dengan gambar Anda (kisi frame, menghadap kanan, 6 baris: IDLE, WALK, ATTACK, HIT, BLOCK, KO).
2. Ubah `id`, `name`, `author` di `manifest.json`.
3. Hapus baris `integrity` atau isi ulang dengan sidik baru.
4. Unggah folder ke GitHub, lalu periksa linknya di halaman Standar PAS 1.0.

## 9. Contoh manifest (templat)

```json
{
  "pas": "1.0",
  "id": "io.github.namaanda.karakter-saya",
  "name": "Karakter Saya",
  "author": "namaanda",
  "license": "CC-BY-4.0",
  "profile": "2d-frames@1",
  "binds_to": { "base_class": "swordsman" },
  "atlas": "atlas.png",
  "frame": { "w": 128, "h": 128 },
  "anchor": { "x": 64, "y": 124 },
  "height_scale": 1.0,
  "clips": {
    "IDLE":   { "row": 0, "frames": 4, "fps": 6,  "loop": true },
    "WALK":   { "row": 1, "frames": 4, "fps": 8,  "loop": true },
    "ATTACK": { "row": 2, "frames": 4, "fps": 12, "loop": false },
    "HIT":    { "row": 3, "frames": 4, "fps": 10, "loop": false },
    "BLOCK":  { "row": 4, "frames": 4, "fps": 6,  "loop": true },
    "KO":     { "row": 5, "frames": 4, "fps": 4,  "loop": false }
  }
}
```

## 10. Pengambilan dan fallback

Engine menerima link GitHub (repo, `tree`, `blob`, `raw`) dan mengubahnya ke CDN jsDelivr.
Bila langkah mana pun gagal, engine memakai figur bawaan dan laga tetap berjalan. Paket tidak pernah dipakai sebagian.

## 11. Kode galat

Kode `E` = paket ditolak (fallback). Kode `W` = paket tetap dipakai dengan peringatan.
Daftar lengkap kode `PAS-E001` … `PAS-E080` dan `PAS-W001` … `PAS-W003` ada di `SPEC.md` bagian 7. Makna kode tidak boleh diubah dalam keluarga 1.x.

## 12. Batas yang diketahui

1. Tidak ada titik pukul per frame di 1.0; engine memakai jangkauan kelas.
2. Hanya satu atlas per paket; suara, efek, dan panggung belum tercakup.
