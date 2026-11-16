# pas-paket-laga

Paket aset laga 2D untuk standar **PAS 1.0** (profil `2d-frames@1`): dua karakter nenek petarung dan satu arena pasar.

> **Status:** NOT_RC_NORMATIVE. Standar PAS 1.0 dan modul rev2 **belum disahkan pemilik**. Paket ini siap diuji, belum rilis resmi.

## Isi

| Folder / berkas | Isi |
|---|---|
| `karakter/mbah-ijuk/` | **Mbah Ijuk**, nenek sapu api — pola `mage`. `manifest.json` + `atlas.png` (512 × 768) |
| `karakter/mak-sedot/` | **Mak Sedot**, nenek pembersih WC — pola `brawler`. `manifest.json` + `atlas.png` (512 × 768) |
| `arena/pasar/` | `background-pasar.png` (800 × 360, lantai mulai y = 300) + `arena.json` (format usulan) |
| `previews/` | GIF pratinjau: tiap keadaan gerak, Pemain 1 asli dan Pemain 2 dicerminkan |
| `MODUL_STANDAR_ASET_KARAKTER_PAS_1.0_rev2.md` | Modul standar yang sudah diperbaiki |
| `MODUL_STANDAR_ASET_KARAKTER_PAS_1.0.md` | Rekonstruksi modul yang hilang (rev1, objek audit) |
| `LAPORAN_AUDIT.md` | Hasil audit modul, temuan, dan putusan |
| `BUKTI_UJI.md` | Hasil semua pemeriksaan |
| `alat/` | Skrip pembuat gambar dan pemeriksa (tambahan, agar hasil bisa dibuat ulang) |

## Cara unggah ke GitHub

1. Buat repositori publik bernama `pas-paket-laga` di akun GitHub Anda.
2. Unggah **seluruh isi** folder ini (tombol *Add file → Upload files*, seret semua folder), lalu *Commit*.
3. Buka `karakter/mbah-ijuk/manifest.json` dan `karakter/mak-sedot/manifest.json`. Ganti `nama` di `id` dan `author` dengan nama akun GitHub Anda **dalam huruf kecil semua**. Contoh: akun `BudiSantoso` → `io.github.budisantoso.mbah-ijuk`.
   Mengubah manifest tidak mengubah `integrity`, karena sidik itu milik `atlas.png`. Jangan ubah `atlas.png` tanpa menghitung ulang sidiknya.
4. Tempel link di bawah ke halaman **Standar PAS 1.0** di aplikasi untuk diperiksa.

## Link uji

Ganti `NAMA` dengan akun GitHub Anda:

- `https://github.com/NAMA/pas-paket-laga/tree/main/karakter/mbah-ijuk`
- `https://github.com/NAMA/pas-paket-laga/tree/main/karakter/mak-sedot`

CDN bisa menyimpan salinan lama beberapa jam. Untuk versi baru, sebaiknya buat rilis (mis. `v1.0.0`) dan pakai link tag itu.

## Arena pasar

Engine saat ini **belum** bisa memuat gambar latar dari luar. `arena/pasar/` disiapkan untuk versi engine berikutnya. `arena.json` adalah format usulan (`"x-pas-arena": "draft-1"`) dan belum dibaca engine.

## Lisensi

Gambar dan dokumen: CC-BY-4.0. Lukisan dasar arena dibuat dengan generator gambar AI lalu diolah dengan skrip `alat/gen_arena.py`. Sprite karakter digambar sepenuhnya oleh skrip `alat/gen_karakter.py`.
