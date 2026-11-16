# LAPORAN AUDIT — MODUL STANDAR ASET KARAKTER PAS 1.0

**Objek audit:** `MODUL_STANDAR_ASET_KARAKTER_PAS_1.0.md` — **rekonstruksi rev1** (berkas asli hilang; disusun ulang 16-11-2026 dari `SPEC.md`, `BACA-SAYA.md`, templat, dan dosier). Nomor baris di bawah merujuk ke berkas rekonstruksi itu.
**Acuan:** `MANDAT_AUDIT_DAN_PEMBUATAN_ASET_PAS_1.0.md` Bagian 0–1; `standar-pas-1.0` (SPEC, skema, conformance); baseline `BASELINE_PANGGUNG_TERPADU_V2_4_1`; `MANDAT_GLOBAL_GOVERNMENT_rev2`.
**Status standar:** **NOT_RC_NORMATIVE** — belum ditandatangani pemilik. Laporan ini tidak mengesahkan apa pun.

## Pernyataan kejujuran (Pasal 9–10 Mandat Global)

1. **Ini bukan audit independen.** Agen yang sama menyusun ulang modul rev1, mengauditnya, menulis rev2, dan membuat aset. Mandat audit meminta auditor yang bukan pembuat modul; syarat itu **tidak terpenuhi** karena modul asli hilang. Audit independen oleh pihak lain tetap diperlukan sebelum pengesahan.
2. Rekonstruksi rev1 sengaja tidak ditambah aturan di luar sumbernya, agar audit menilai isi yang memang tersedia. Bila modul asli ditemukan, audit harus diulang terhadap berkas asli.
3. Validator referensi `src/lib/pas/validate.ts` **tidak ada** di arsip yang diterima. Sebagai gantinya dibuat pemeriksa Python (`alat/pas_validate.py`) dan diuji terhadap `conformance.json`: **32/32 kasus cocok** (lihat `BUKTI_UJI.md`). Ini bukti kesetaraan, bukan pengganti validator referensi.

## Ringkasan

| Tingkat | Jumlah |
|---|---|
| KRITIS | 2 |
| SEDANG | 13 |
| RINGAN | 6 |

**Putusan untuk rev1: LAYAK DENGAN PERBAIKAN.**
Alasan: semua aturan teknis manifest sudah benar dan sama dengan SPEC (kolom, kunci terlarang, batas angka, kode galat). Kekurangannya ada di panduan gambar: isi pose, aturan tampilan, dan kejujuran batas. Semua perbaikan bersifat menambah penjelasan, tanpa mengubah kunci manifest, nama keadaan, atau kode galat. Perbaikan itu sudah dikerjakan di `MODUL_STANDAR_ASET_KARAKTER_PAS_1.0_rev2.md`.
Status standar tetap **NOT_RC_NORMATIVE** sampai pemilik menandatangani.

## Temuan

Format: `ID | Bagian | Masalah | Bukti (kutipan) | Tingkat | Perbaikan`

### A. Kelengkapan gerak

| ID | Bagian | Masalah | Bukti (kutipan) | Tingkat | Perbaikan |
|---|---|---|---|---|---|
| A-01 | A | Tidak ada isi pose per frame untuk keenam keadaan. AI bisa membuat `ATTACK` tanpa pose hentakan atau `KO` yang berakhir berdiri. | L69–74: "`ATTACK` \| Menyerang \| `loop: false`" — hanya arti satu kata | KRITIS | rev2 §7.2: tabel pose frame 1–4 untuk tiap keadaan + aturan isi |
| A-02 | A | Tidak dijelaskan kapan klip mulai dan apa yang tampil bila keadaan lebih pendek/panjang dari klip. Pose penting bisa tidak pernah tampil. | L77: "Klip hanya disampling" | SEDANG | rev2 §7.1: rumus `k = floor(t × fps)`, akibatnya, hentakan di frame 2–3 |
| A-03 | A | `WALK` dipakai untuk maju dan mundur, tetapi tidak ada saran agar langkah tetap wajar saat mundur. | L70: "Bergerak maju/mundur" | RINGAN | rev2 §7.2 aturan isi no. 2 |

### B. Kebebasan senjata

| ID | Bagian | Masalah | Bukti (kutipan) | Tingkat | Perbaikan |
|---|---|---|---|---|---|
| B-01 | B | Kelas hanya disebut namanya. Nama `swordsman`/`gunslinger` terbaca sebagai jenis senjata; tidak ada penjelasan cara bertarung tiap kelas. | L25: "Ada empat kelas: `brawler`, `swordsman`, `gunslinger`, `mage`." | SEDANG | rev2 §3: tabel pola = cara bertarung + contoh senjata bebas (sapu, gitar, kipas, lidah) |
| B-02 | B | Kebebasan bentuk tubuh disebut, kebebasan senjata/efek tidak. | L21: "Bentuk tubuh bebas: humanoid, hewan, …" | RINGAN | rev2 §3 kalimat pembuka |

### C. Bebas ambiguitas

| ID | Bagian | Masalah | Bukti (kutipan) | Tingkat | Perbaikan |
|---|---|---|---|---|---|
| C-01 | C | "Sebaiknya transparan" bisa dibaca boleh latar putih/hijau. Dosier 05 malah membolehkan chroma `#00FF00`, padahal engine PAS 1.0 tidak menghapus chroma. | L62: "Latar sebaiknya transparan." | SEDANG | rev2 D6 (WAJIB alfa 0, chroma dilarang) |
| C-02 | C | "Titik kaki" tidak menyebut titik mana (tengah bawah?) dan tidak mewajibkan semua frame di baris yang sama. | L46: "Titik kaki yang menapak lantai" | SEDANG | rev2 D1 |
| C-03 | C | Kolom "Saran" membuat `loop` tampak opsional. `KO` dengan `loop: true` akan jatuh berulang-ulang. | L67: "\| State \| Arti \| Saran \|" | SEDANG | rev2 D4 (WAJIB) |
| C-04 | C | Tidak jelas bahwa satu klip tambahan menolak **seluruh** paket, dan apakah `x-…` boleh di dalam klip. | L48: "Tepat enam state"; L50: "`x-…` \| BOLEH" | SEDANG | rev2 §4.1 baris `clips` + kalimat penutup; §8.1 |
| C-05 | C | Akibat cermin untuk Pemain 2 tidak dijelaskan (tulisan/detail satu sisi ikut terbalik). | L63: "engine membalik gambar untuk sisi kiri" | SEDANG | rev2 D3 |
| C-06 | C | Contoh `id` huruf kecil benar, tetapi tidak diperingatkan bahwa akun GitHub berhuruf besar harus ditulis kecil. Contoh di mandat (`io.github.NAMA.…`) sendiri akan ditolak `PAS-E020` bila disalin apa adanya. | L38: "Domain-balik huruf kecil"; mandat Bagian 3: "`id`: `io.github.NAMA.mbah-ijuk`" | SEDANG | rev2 §4.1 baris `id`; paket ini memakai `io.github.nama.…` |
| C-07 | C | Cara `height_scale` diterapkan ke layar tidak dijelaskan, jadi kreator tidak bisa menebak besar tampilan. | L47: "`height_scale` \| WAJIB \| 0,75–1,30" | RINGAN | rev2 §2 (fakta skala, dengan status bukti) |
| C-08 | C | "Isi ulang dengan sidik baru" tanpa cara menghitungnya. | L83 | RINGAN | rev2 §4.1 perintah `openssl` |

### D. Enam aturan tampilan

| ID | Aturan | Ada? | Bukti (kutipan) | Tingkat | Perbaikan |
|---|---|---|---|---|---|
| D-01 | D1 Kaki menapak | Sebagian | L46: "Titik kaki yang menapak lantai"; nilai `{"x":64,"y":124}` hanya di contoh L99 | SEDANG | rev2 D1 |
| D-02 | D2 Ruang ayun | **Tidak ada** | Tidak ada kalimat tentang lebar tubuh atau tepi kotak | SEDANG | rev2 D2 |
| D-03 | D3 Arah hadap & cermin | Sebagian | L63 (lihat C-05) | (digabung C-05) | rev2 D3 |
| D-04 | D4 Berulang vs tertahan | Sebagian, sebagai saran | L67–74 (lihat C-03); "frame terakhir KO terkapar diam" tidak ada | (digabung C-03) | rev2 D4 |
| D-05 | D5 Kecepatan | **Tidak ada**, dan contoh bertentangan | L106: "`BLOCK` … `fps`: 6"; L107: "`KO` … `fps`: 4" — di bawah rentang 8–10 | SEDANG | rev2 D5 + catatan templat §9 |
| D-06 | D6 Transparan | Sebagian | L62 (lihat C-01); larangan bayangan lantai tidak ada | (digabung C-01) | rev2 D6 |

### E. Jujur soal batas

| ID | Bagian | Masalah | Bukti (kutipan) | Tingkat | Perbaikan |
|---|---|---|---|---|---|
| E-01 | E | Tidak dikatakan bahwa 6 keadaan adalah batas tampilan, bahwa jumlah frame per keadaan boleh 1–64, dan bahwa aksi dibuat lewat pose kunci/garis gerak/efek. AI cenderung menambah `JUMP`/`SPECIAL`, dan satu kunci saja membuat seluruh paket ditolak. | L122–125 hanya menyebut titik pukul dan satu atlas | KRITIS | rev2 §8 |

### X. Temuan tambahan (di luar A–E)

| ID | Kategori (Mandat Global Ps. 5) | Masalah | Bukti | Tingkat | Perbaikan |
|---|---|---|---|---|---|
| X-01 | C — konflik dokumentasi | Dosier 04/05 memakai format lain (`character.json`, state `attack.<M>@keluarga`, sel 512, garis tanah 496/512, chroma hijau). Tanpa urutan sumber, AI bisa mencampur dua format. | Dosier 04 §3; Dosier 05 §2 | SEDANG | rev2 §0: SPEC > modul > dosier (usulan) |
| X-02 | G — keterbatasan bukti | Fakta mandat "kanvas 800 × 360, lantai y = 300, skala 1,3 × `height_scale`" **tidak bisa dibuktikan** dari baseline: pemuat sprite tidak ada (Dosier 01: "Asset loader … NOT IMPLEMENTED"), dan lantai figur bawaan di `H*0.84` (`ArenaCanvas.tsx:282`). Yang terbukti: 30 detak/dtk (`arena.worker.ts` `TICK_MS = 1000 / 30`), 4 kelas (`ko-engine.types.d.ts:102`), cermin menurut arah hadap (`ArenaCanvas.tsx:132,152`). | Baseline V2.4.1 | SEDANG | rev2 §2 menandai status tiap fakta; aset dibuat mengikuti angka mandat |
| X-03 | C | Contoh manifest di mandat tidak punya `author`; modul punya `author` (BOLEH). Sesuai mandat ("ikuti modul"), paket ini mengisi `author`. | Mandat Bagian 3 vs L40 | RINGAN | Paket memakai `author: "nama"` |
| X-04 | D — kekurangan spesifikasi | Efek "panjang" (semburan api, lidah) dibatasi lebar kotak. Dengan kotak 128 dan tepi 2 px, efek hanya ±30–40 px dari tubuh. | Mandat Bagian 3: "semburan api panjang ke kanan (di ruang ayun)" | RINGAN | rev2 D2.5 |
| X-05 | B — kekurangan verifikasi | Tafsiran pemilihan frame (`t` sejak masuk keadaan) belum bisa dicocokkan dengan renderer referensi. | Mandat Bagian 0 no. 7 | (dicatat) | rev2 §7.1 diberi catatan "wajib dicocokkan" |

## Pemeriksaan ulang rev2 terhadap A–E (oleh pelaksana yang sama)

| Kriteria | rev1 | rev2 |
|---|---|---|
| A. Pose per frame keenam keadaan | Tidak ada | Ada (§7.2) + cara pilih frame (§7.1) |
| B. Pola = cara bertarung, senjata bebas | Tidak jelas | Ada (§3) |
| C. Bebas ambiguitas | 8 temuan | Semua ditangani; sisa tafsiran §7.1 ditandai terbuka |
| D. D1–D6 | 0 lengkap, 4 sebagian, 2 tidak ada | 6 WAJIB dengan angka terukur (§6) |
| E. Jujur soal batas | Tidak ada | Ada (§8) |

## Yang membutuhkan tindakan pemilik

1. Tanda tangan/pengesahan modul rev2 dan kit standar (`standar/PENGESAHAN.md`). Agen tidak boleh dan tidak menandatangani.
2. Menunjuk auditor independen untuk mengulang audit ini (syarat independensi belum terpenuhi).
3. Bila modul asli ditemukan: kirimkan, agar audit diulang terhadap berkas asli.
4. Konfirmasi angka kanvas (800 × 360, lantai 300, skala 1,3) dari kode engine versi yang memuat sprite, karena kode itu tidak ada di arsip yang diterima.
