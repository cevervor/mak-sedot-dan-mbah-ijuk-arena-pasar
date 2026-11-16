# MODUL STANDAR ASET KARAKTER — PAS 1.0 (profil `2d-frames@1`) — rev2

**Status:** NOT_RC_NORMATIVE — draf siap ditinjau, **belum disahkan pemilik**. Agen dilarang menyebut modul ini resmi.
**Tanggal:** 16-11-2026 · **Menggantikan:** rekonstruksi rev1 (`MODUL_STANDAR_ASET_KARAKTER_PAS_1.0.md`)
**Hubungan dengan standar:** modul ini adalah **panduan produksi**. Ia tidak mengubah `SPEC.md`, `manifest.schema.json`, atau `conformance.json`.
Tidak ada kunci manifest baru, nama keadaan gerak tetap, dan kode galat tetap.

Kata **WAJIB**, **DILARANG**, **SEBAIKNYA**, dan **BOLEH** bersifat normatif seperti di `SPEC.md`.
Aturan bertanda **[MODUL]** lebih ketat daripada `SPEC.md`: validator engine tidak menolak paket yang melanggarnya, tetapi paket itu **tidak patuh modul** dan bisa tampil buruk.

---

## 0. Urutan sumber yang berlaku

Bila ada pertentangan, yang lebih atas menang:

1. `standar-pas-1.0/standar/SPEC.md`, `manifest.schema.json`, `conformance.json` (sidik di `SHA256SUMS`). Ini aturan yang ditegakkan engine.
2. Modul ini (aturan produksi dan aturan tampilan D1–D6).
3. `DOSIER_AUDIT_STANDAR_ASET_PAS_v1` — **usulan** format lain (`character.json`, banyak state, sel 512). Dosier itu **bukan** format PAS 1.0 dan DILARANG dipakai untuk paket `2d-frames@1`.

---

## 1. Batas otoritas

1. Paket adalah **kulit visual saja**. Engine memutuskan semua hal laga: HP, damage, siapa kena, siapa menang.
2. Paket DILARANG berisi angka laga atau kode (lihat 4.2).
3. Panjang animasi DILARANG dipakai untuk mengatur laga. Engine yang menentukan kapan dan berapa lama setiap keadaan.

## 2. Fakta engine yang dipakai modul ini

| Fakta | Nilai | Status bukti |
|---|---|---|
| Detak engine | 30 detak per detik | Terverifikasi: `src/engine/arena.worker.ts` `TICK_MS = 1000 / 30` (baseline V2.4.1) |
| Kelas engine | `brawler`, `swordsman`, `gunslinger`, `mage` | Terverifikasi: `src/engine/ko-engine.types.d.ts:102`, `src/engine/opsi-laga.ts:6` |
| Pemain 2 dicerminkan | gambar dibalik menurut arah hadap | Terverifikasi untuk figur bawaan: `ArenaCanvas.tsx:132,152`; untuk sprite: `SPEC.md` 4.4 |
| Kanvas arena | 800 × 360 piksel, garis lantai y = 300 | Dari mandat; **belum terverifikasi** (pemuat sprite tidak ada di arsip baseline) |
| Skala gambar | `1,3 × height_scale`, titik `anchor` ditempel ke lantai | Dari mandat; **belum terverifikasi** di kode |
| Enam keadaan gerak | `IDLE`, `WALK`, `ATTACK`, `HIT`, `BLOCK`, `KO` | Terverifikasi: `SPEC.md` 5, `conformance.json` N07 (state lain ditolak) |

## 3. Pola laga = cara bertarung, bukan jenis senjata

`binds_to.base_class` memilih **cara bertarung** karakter. Rupa dan senjata **bebas**: sapu, gitar, kipas, wajan, payung, lidah, ekor, tangan kosong — apa saja.

| Pola | Cara bertarung yang akan ditayangkan engine | Contoh rupa yang cocok |
|---|---|---|
| `brawler` | Jarak dekat, cepat | Petinju, nenek ber-plunger, kucing pencakar |
| `swordsman` | Ayunan jarak sedang | Pedang, gitar diayun, payung, dayung |
| `gunslinger` | Jarak jauh, lurus | Pistol, ketapel, sumpit tiup, lempar sandal |
| `mage` | Jarak jauh, lambat tapi kuat | Sihir, semburan api, gelombang suara |

1. Pilih pola dari **cara bergerak**, bukan dari nama senjata. Gitar yang diayun = `swordsman`; gitar yang menembakkan nada = `mage` atau `gunslinger`.
2. Gambar serangan WAJIB cocok dengan polanya: pola jarak dekat jangan digambar menembak jauh, pola jarak jauh jangan digambar menempel lawan.
3. Kelas baru tidak bisa dibuat lewat paket.

## 4. Isi paket dan manifest

Satu folder: `manifest.json` + satu atlas. `README.md` dan `previews/` BOLEH ada (diabaikan engine).
Jalur atlas WAJIB relatif, DILARANG diawali `/`, memuat `..`, atau berupa URL.

### 4.1 Kolom (sama persis dengan `SPEC.md` bagian 3)

| Kunci | Wajib | Aturan |
|---|---|---|
| `$schema` | BOLEH | Teks, diabaikan engine |
| `pas` | WAJIB | Tepat `"1.0"` |
| `id` | WAJIB | Domain-balik **huruf kecil**, ≥ 3 ruas, maks. 128 karakter. Ganti `nama` dengan akun GitHub Anda **dalam huruf kecil** (huruf besar → `PAS-E020`) |
| `name` | WAJIB | Teks 1–64 karakter |
| `author` | BOLEH | Teks 1–64 karakter |
| `license` | SEBAIKNYA | Pengenal SPDX, mis. `CC-BY-4.0` (tanpa ini → `PAS-W001`) |
| `profile` | WAJIB | Tepat `"2d-frames@1"` |
| `binds_to.base_class` | WAJIB | Salah satu pola di bagian 3 |
| `atlas` | WAJIB | Jalur relatif ke `.png`/`.webp` |
| `frame.w`, `frame.h` | WAJIB | Bilangan bulat 16–1024 |
| `anchor.x`, `anchor.y` | WAJIB | Bilangan bulat di dalam kotak (0..w, 0..h). Lihat D1 |
| `height_scale` | WAJIB | 0,75–1,30. Hanya tinggi tampilan; tidak mengubah jangkauan atau tabrakan |
| `clips` | WAJIB | Tepat enam kunci keadaan (bagian 7). Kunci keadaan lain → `PAS-E003`, seluruh paket ditolak |
| `integrity.atlas` | SEBAIKNYA | `sha256-` + Base64 standar (dengan `=`) dari SHA-256 **isi berkas** atlas. Tanpa ini → `PAS-W003` |
| `x-…` | BOLEH | Catatan bebas, di level mana pun. Tetap diperiksa kunci terlarangnya |

Kolom lain DILARANG (`PAS-E003`). Di dalam setiap klip hanya `row`, `frames`, `fps`, `loop`, dan `x-…`.

Cara menghitung `integrity.atlas` (sekali setelah atlas final; ubah satu piksel = hitung ulang):

```bash
echo "sha256-$(openssl dgst -sha256 -binary atlas.png | base64)"
```

### 4.2 Kunci terlarang (di level mana pun, termasuk di dalam `x-…`, huruf besar/kecil sama saja → `PAS-E002`)

`damage`, `dmg`, `hp`, `health`, `maxhp`, `attack_power`, `defense`, `armor`, `hitbox`, `hurtbox`, `pushbox`, `collision`, `hitstun`, `blockstun`, `startup`, `active`, `recovery`, `priority`, `speed`, `reach`, `range`, `cooldown`, `frame_data`, `frame_events`, `knockback`, `win`, `winner`, `script`, `code`, `eval`, `onload`, `handler`

## 5. Atlas

1. Atlas adalah kisi. Frame kolom ke-*i* (mulai 0), baris ke-*r*: `x = i·frame.w`, `y = r·frame.h`.
2. Lebar ≥ `max(frames)·frame.w`; tinggi ≥ `(max(row)+1)·frame.h` (kurang → `PAS-E071`).
3. Maks. 4096 px per sisi dan 8 MB (`PAS-E072`).
4. **[MODUL]** Satu keadaan = satu baris, urutan baris `IDLE(0) WALK(1) ATTACK(2) HIT(3) BLOCK(4) KO(5)`. Berbagi baris boleh menurut SPEC (`PAS-W002`), tetapi tidak patuh modul.
5. **[MODUL]** Ukuran acuan: kotak 128 × 128, 4 frame per baris → atlas 512 × 768.

## 6. Enam aturan tampilan (WAJIB)

Angka dalam kurung siku berlaku untuk kotak 128 × 128; untuk ukuran lain pakai persentase yang sama.

**D1 — Kaki menapak.**
1. `anchor.x = frame.w / 2` dan `anchor.y` antara `frame.h − 4` dan `frame.h` [`{"x":64,"y":124}` s.d. `{"x":64,"y":128}`].
2. Di **setiap** frame, piksel tubuh paling bawah (telapak; saat terduduk/terbaring: bagian tubuh yang menyentuh lantai) berada **tepat** di baris `anchor.y − 1`.
3. DILARANG ada piksel apa pun pada baris `anchor.y` ke bawah.
4. Langkah jalan: minimal satu kaki tetap di baris itu.

**D2 — Ruang ayun.**
1. Tubuh inti (kepala, badan, kaki; tanpa lengan, senjata, efek) berada di pita tengah selebar 47–62 % lebar kotak [60–80 px; seluruhnya di dalam x 24–103].
2. Sisi kiri dan kanan dipakai senjata dan efek.
3. Tepi kotak 2 px WAJIB transparan di semua sisi. Senjata atau efek yang menyentuh tepi akan terpotong, jadi perpendek atau tekuk.
4. Pengecualian: frame `KO` terbaring boleh keluar dari pita tengah, tetapi tetap menjaga tepi 2 px.
5. Efek panjang (semburan, lidah, gelombang) hanya bisa sepanjang ruang ayun di dalam kotak [± 30–40 px dari tubuh]. Proyektil jauh adalah urusan engine, bukan sprite.

**D3 — Arah hadap dan cermin.**
1. Semua frame digambar **menghadap kanan**.
2. Pemain 2 dibalik seperti cermin. Tulisan, angka, logo, dan detail satu sisi (tahi lalat, tambalan, senjata di tangan kanan) ikut terbalik.
3. DILARANG menaruh tulisan di sprite. Detail satu sisi SEBAIKNYA dibuat simetris atau tidak penting.

**D4 — Berulang vs tertahan.**
1. `IDLE`, `WALK`, `BLOCK` WAJIB `loop: true`.
2. `ATTACK`, `HIT`, `KO` WAJIB `loop: false`.
3. Frame terakhir `KO` WAJIB pose **terkapar diam**, tanpa efek bergerak (garis gerak, debu, asap), karena frame itu ditahan sampai laga selesai.
4. Frame terakhir `ATTACK` dan `HIT` WAJIB pose yang enak dilihat bila ditahan agak lama.

**D5 — Kecepatan (fps).**

| Keadaan | fps |
|---|---|
| `IDLE` | 6–8 |
| `WALK` | 8–10 |
| `ATTACK` | 10–12 |
| `HIT` | 8–10 |
| `BLOCK` | 8–10 |
| `KO` | 8–10 |

**D6 — Transparan.**
1. Atlas **PNG RGBA**; latar 100 % tembus pandang (alfa 0). SPEC menerima WebP beralfa, tetapi modul ini memakai PNG.
2. DILARANG kotak putih/hitam, latar hijau (chroma), bingkai, garis kisi, atau bayangan lantai di dalam sprite. Bayangan lantai milik engine.
3. Sudut-sudut atlas WAJIB alfa 0.

## 7. Isi pose setiap keadaan

### 7.1 Cara engine memilih frame (tafsiran modul)

Detik `t` dihitung sejak engine masuk keadaan itu. `k = floor(t × fps)`.
- `loop: true` → frame `k mod frames`.
- `loop: false` → frame `min(k, frames − 1)`, lalu **berhenti** di frame terakhir.

Akibatnya:
1. Bila engine keluar dari keadaan lebih cepat daripada panjang klip, frame akhir tidak pernah tampil. Taruh pose terpenting di depan.
2. Bila engine bertahan lebih lama, frame terakhir ditahan (lihat D4.4).
3. **[MODUL]** Untuk `ATTACK` 4 frame pada 10–12 fps, pose **hentakan** WAJIB di frame ke-2 atau ke-3 (tampil 0,08–0,3 detik setelah mulai).

> Tafsiran ini mengikuti mandat ("maju sesuai lama keadaan lalu berhenti di frame terakhir"). Rumus pastinya wajib dicocokkan dengan renderer referensi saat tersedia.

### 7.2 Pola pose umum (untuk 4 frame; bila memakai frame lain, pertahankan urutan tahapnya)

| Keadaan | Frame 1 | Frame 2 | Frame 3 | Frame 4 |
|---|---|---|---|---|
| `IDLE` (loop) | Siaga, napas masuk | Naik sedikit | Puncak napas | Turun (menyambung ke frame 1 tanpa loncat) |
| `WALK` (loop) | Kaki depan menapak di depan | Kaki melintas (satu kaki diangkat ≤ 4 px) | Kaki lain menapak di depan | Kaki melintas lagi |
| `ATTACK` | **Ancang-ancang**: tubuh atau senjata ditarik | **Hentakan**: gerak paling jauh / kontak | **Puncak efek** di ruang ayun | **Penyelesaian**: kembali ke siaga, sisa efek |
| `HIT` | Tersentak paling keras ke belakang | Terdorong / goyah | Mulai menahan diri | Hampir siaga (aman ditahan) |
| `BLOCK` (loop) | Senjata/tangan dipalang di depan badan | Gemetar kecil (± 1 px) | Kembali | Gemetar ke arah lain |
| `KO` | Limbung | Jatuh (terduduk/berlutut) | Menyentuh lantai | **Terkapar diam** (D4.3) |

Aturan isi:
1. Setiap frame WAJIB berisi karakter utuh. DILARANG frame kosong atau hanya efek.
2. Keadaan `WALK` dipakai untuk maju **dan** mundur. Langkah SEBAIKNYA pendek dan netral agar tidak tampak "jalan mundur ke depan".
3. Proporsi, warna, kostum, dan senjata WAJIB sama di semua frame.
4. Garis gerak dan efek BOLEH, asal di dalam kotak (D2) dan tidak di frame terakhir `KO`.
5. SEBAIKNYA tidak memakai merah/oranye atau biru/toska sebagai warna dominan seluruh tubuh (penanda tim engine). Efek api boleh oranye.

## 8. Jujur soal batas

1. Enam keadaan gerak adalah **batas tampilan saat ini**. Tidak ada lompat, jongkok, jurus khusus, intro, atau pose menang. Klip tambahan menyebabkan **seluruh paket ditolak** (`PAS-E003`) dan engine memakai figur bawaan.
2. Yang boleh diperbanyak adalah **jumlah frame per keadaan**: 1–64.
3. "Aksi nyata" dicapai lewat **pose kunci** (ancang-ancang → hentakan → penyelesaian), **garis gerak**, dan **efek** di dalam kotak — bukan lewat klip tambahan.
4. Tidak ada titik pukul per frame di 1.0; kapan lawan kena ditentukan engine dari kelasnya.
5. Satu atlas per paket. Suara dan panggung belum tercakup. Gambar arena dari luar **belum** dibaca engine.

## 9. Contoh manifest lengkap

```json
{
  "pas": "1.0",
  "profile": "2d-frames@1",
  "id": "io.github.nama.mbah-ijuk",
  "name": "Mbah Ijuk",
  "author": "nama",
  "license": "CC-BY-4.0",
  "binds_to": { "base_class": "mage" },
  "atlas": "atlas.png",
  "frame": { "w": 128, "h": 128 },
  "anchor": { "x": 64, "y": 124 },
  "height_scale": 0.9,
  "clips": {
    "IDLE":   { "row": 0, "frames": 4, "fps": 7,  "loop": true },
    "WALK":   { "row": 1, "frames": 4, "fps": 9,  "loop": true },
    "ATTACK": { "row": 2, "frames": 4, "fps": 11, "loop": false },
    "HIT":    { "row": 3, "frames": 4, "fps": 9,  "loop": false },
    "BLOCK":  { "row": 4, "frames": 4, "fps": 8,  "loop": true },
    "KO":     { "row": 5, "frames": 4, "fps": 8,  "loop": false }
  },
  "integrity": { "atlas": "sha256-<Base64 dari SHA-256 atlas.png>" }
}
```

Catatan: templat lama (`templat-karakter/manifest.json`) memakai `BLOCK` 6 fps dan `KO` 4 fps. Itu sah menurut SPEC tetapi **tidak patuh D5**; ubah ke 8–10 saat memakai templat.

## 10. Daftar periksa sebelum unggah

- [ ] Tidak ada kunci terlarang; hanya kolom 4.1 atau berawalan `x-`.
- [ ] `id` huruf kecil semua.
- [ ] Atlas PNG RGBA, sudut alfa 0, tepi kotak 2 px transparan.
- [ ] Piksel terbawah tubuh setiap frame di baris `anchor.y − 1`; tidak ada piksel di bawahnya.
- [ ] Tubuh inti di pita tengah (kecuali KO terbaring).
- [ ] Menghadap kanan; tanpa tulisan.
- [ ] `loop` dan `fps` sesuai D4 dan D5.
- [ ] Frame terakhir `KO` terkapar diam tanpa efek.
- [ ] `integrity.atlas` dihitung dari atlas final.
- [ ] Link GitHub diperiksa di halaman Standar PAS 1.0.

## 11. Pengambilan, fallback, dan kode galat

Tidak berubah dari `SPEC.md` bagian 6 dan 7: link GitHub (repo, `tree`, `blob`, `raw`) diubah ke jsDelivr; bila satu langkah gagal, engine memakai figur bawaan dan laga tetap berjalan; paket tidak pernah dipakai sebagian. CDN bisa menyimpan salinan lama beberapa jam, jadi SEBAIKNYA pakai tag rilis (`@v1.0.0`) atau folder baru untuk versi baru.

| Kode | Arti |
|---|---|
| `PAS-E001` | Manifest bukan objek JSON yang valid |
| `PAS-E002` | Kunci gameplay dilarang — angka laga hanya milik engine |
| `PAS-E003` | Kunci tidak dikenal (gunakan awalan x- untuk ekstensi) |
| `PAS-E004` | Manifest melebihi batas ukuran |
| `PAS-E005` | Kolom wajib hilang |
| `PAS-E010` | Versi pas tidak didukung |
| `PAS-E020` | id harus domain-balik huruf kecil, mis. io.github.nama.karakter |
| `PAS-E021` | name wajib berupa teks 1–64 karakter |
| `PAS-E022` | author/license harus teks 1–64 karakter |
| `PAS-E030` | profile tidak didukung |
| `PAS-E031` | binds_to.base_class bukan kelas engine |
| `PAS-E040` | atlas harus jalur relatif ke berkas .png/.webp di folder paket |
| `PAS-E041` | frame.w/h harus bilangan bulat dalam batas |
| `PAS-E042` | anchor harus bilangan bulat di dalam kotak frame |
| `PAS-E043` | height_scale di luar batas |
| `PAS-E050` | Klip state wajib hilang |
| `PAS-E051` | Klip tidak valid (row/frames/fps/loop) |
| `PAS-E060` | integrity.atlas harus berformat sha256-<base64> |
| `PAS-E070` | Atlas gagal dimuat |
| `PAS-E071` | Atlas lebih kecil dari yang dibutuhkan klip |
| `PAS-E072` | Atlas melebihi batas piksel |
| `PAS-E073` | Checksum atlas tidak cocok |
| `PAS-E080` | Manifest tidak dapat diambil |
| `PAS-W001` | license belum diisi — sebaiknya cantumkan, mis. CC-BY-4.0 |
| `PAS-W002` | Beberapa klip memakai baris atlas yang sama |
| `PAS-W003` | integrity.atlas belum diisi — isi agar atlas tidak bisa ditukar diam-diam |

---

## Catatan Perubahan (rev1 → rev2)

| No | Perubahan | Alasan (ID temuan di `LAPORAN_AUDIT.md`) |
|---|---|---|
| 1 | Tambah bagian 0: urutan sumber; dosier dinyatakan usulan, bukan PAS 1.0 | X-01 |
| 2 | Tambah bagian 2: fakta engine beserta status buktinya | X-02 |
| 3 | Bagian 3 baru: pola laga dijelaskan sebagai cara bertarung, senjata bebas, contoh | B-01, B-02 |
| 4 | `id` wajib huruf kecil ditegaskan; cara menghitung `integrity` ditambahkan | C-06, C-08 |
| 5 | Klip tambahan dinyatakan menolak seluruh paket; `x-` di dalam klip dijelaskan | C-04, E-01 |
| 6 | D1–D6 dimasukkan sebagai aturan WAJIB dengan angka yang bisa diukur | D-01 … D-06, C-01, C-02, C-03, C-05 |
| 7 | Bagian 7: cara engine memilih frame + isi pose per frame untuk keenam keadaan | A-01, A-02, A-03 |
| 8 | Bagian 8: batas tampilan dijelaskan jujur (6 keadaan, 1–64 frame, aksi lewat pose kunci) | E-01 |
| 9 | Catatan templat: `BLOCK` 6 fps dan `KO` 4 fps tidak patuh D5 | D-05 |
| 10 | Tabel kode galat disalin utuh dari SPEC (tanpa perubahan makna) | Kelengkapan |
| 11 | Efek panjang dibatasi ruang ayun di dalam kotak | X-06 |

Yang **tidak** diubah: nama kunci manifest, nama enam keadaan, kode galat, batas angka SPEC.
