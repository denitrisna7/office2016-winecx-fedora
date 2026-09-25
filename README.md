# Office 2016 + WineCX — Fedora 44

Installer otomatis untuk menjalankan **Microsoft Office 2016 32-bit** di Fedora menggunakan **WineCX** dan prefix khusus `~/.office2016`.

> **Status:** V3.13.4  
> Fokus versi ini: instalasi yang dapat dilanjutkan, output installer yang ringkas, progress persentase, perbaikan permission font, instalasi icon, launcher GNOME, dan verifikasi akhir.

---

## ⚠️ Catatan penting

Project ini **tidak menyertakan file ISO Microsoft Office, WineCX binary, font package, atau file proprietary Microsoft lainnya**.

Pengguna harus menyediakan file yang memang berhak digunakan/didistribusikan dan meletakkannya di folder `~/Downloads`.

Jika file sumber disediakan melalui Google Drive, gunakan **link Google Drive milik Anda sendiri** pada bagian tabel sumber di bawah.

---

## 1. Persyaratan

### Sistem

- Fedora 44
- arsitektur x86_64
- koneksi internet untuk dependency Fedora/Winetricks
- akses `sudo`
- ruang penyimpanan yang cukup untuk Office dan Wine prefix

### File yang diperlukan

Letakkan semua file berikut di:

```text
~/Downloads/
```

| File | Keterangan | Link |
|---|---|---|
| `install_office2016_fedora.py` | Installer utama | Repository ini |
| `SW_DVD5_Office_Professional_Plus_2016_W32_English_MLF_X20-41353.ISO` | ISO Office 2016 32-bit | **[Google Drive — isi link Anda]** |
| `winecx.zip` | WineCX precompiled | **[Google Drive — isi link Anda]** |
| `FuentesOffice365.zip` | Font yang digunakan installer | **[Google Drive — isi link Anda]** |
| `Requerimientos Office 2016.zip` | DLL, icon, dan file pendukung | **[Google Drive — isi link Anda]** |

> Nama file harus sesuai dengan yang tercantum di tabel agar installer dapat menemukannya secara otomatis.

---

## 2. Struktur file

Setelah semua file berada di `~/Downloads`, struktur awalnya kira-kira:

```text
~/Downloads/
├── install_office2016_fedora.py
├── SW_DVD5_Office_Professional_Plus_2016_W32_English_MLF_X20-41353.ISO
├── winecx.zip
├── FuentesOffice365.zip
└── Requerimientos Office 2016.zip
```

Installer akan menangani ekstraksi file pendukung.

Untuk `Requerimientos Office 2016.zip`, struktur sumber yang digunakan adalah:

```text
Requerimientos Office 2016.zip
└── Requerimientos Office 2016/
    └── Office 2016 icons.zip
        └── Office 2016 icons/
            ├── word2016.png
            ├── excel2016.png
            ├── powerpoint2016.png
            ├── outlook2016.png
            ├── access2016.png
            └── publisher2016.png
```

---

# 3. Instalasi

## Langkah 1 — Download repository

Clone repository:

```bash
git clone https://github.com/denitrisna7/office2016-winecx-fedora.git
cd office2016-winecx-fedora
```

Salin installer ke Downloads:

```bash
cp install_office2016_fedora.py ~/Downloads/
```

---

## Langkah 2 — Pastikan source tersedia

Cek:

```bash
cd ~/Downloads

ls -lh \
"SW_DVD5_Office_Professional_Plus_2016_W32_English_MLF_X20-41353.ISO" \
"winecx.zip" \
"FuentesOffice365.zip" \
"Requerimientos Office 2016.zip"
```

Jika keempat file muncul, lanjutkan.

---

## Langkah 3 — Jalankan installer

```bash
cd ~/Downloads
chmod +x install_office2016_fedora.py
python3 install_office2016_fedora.py
```

Installer akan meminta password `sudo` jika diperlukan.

---

# 4. Apa yang dilakukan installer?

Installer menjalankan tahapan berikut:

```text
[  8%] Source files ready
[ 15%] Installing Fedora dependencies
[ 23%] Preparing WineCX
[ 31%] Preparing Office prefix
[ 38%] Installing Winetricks components
[ 46%] Checking Office 2016 installation
[ 54%] Installing Gecko / Mono
[ 62%] Applying DirectX fixes
[ 69%] Applying Office DLLs
[ 77%] Installing Office icons
[ 85%] Installing fonts
[ 92%] Creating Office launchers
[100%] Final verification
```

Normal output dari subprocess dibuat lebih ringkas agar terminal tidak dipenuhi log.

Jika terjadi error, detail error akan ditampilkan.

---

# 5. Office sudah terinstall?

Installer dapat mendeteksi instalasi Office yang sudah ada.

Jika prefix sudah berisi Office 2016:

```text
State: COMPLETE

[ OK ] Office 2016 is already installed/present.
[INFO] Skipping setup.exe only; continuing all remaining PDF stages.
```

Artinya installer **tidak mengulang instalasi Office**.

Tahap setelahnya tetap dijalankan, termasuk:

- Gecko / Mono
- DirectX fixes
- Office DLL
- icon
- font
- launcher
- Excel association
- desktop database
- final verification

Ini memungkinkan script digunakan untuk **memperbaiki/menyelesaikan instalasi yang sebelumnya sudah berjalan sebagian**.

---

# 6. Wine prefix

Office menggunakan prefix:

```text
~/.office2016
```

Wine yang digunakan launcher:

```text
/opt/winecx/bin/wine
```

Wine server:

```text
/opt/winecx/bin/wineserver
```

WineCX:

```text
/opt/winecx
```

Installer tidak menghapus prefix yang sudah ada.

---

# 7. Office launcher

Installer membuat launcher GNOME untuk:

- Microsoft Word 2016
- Microsoft Excel 2016
- Microsoft PowerPoint 2016
- Microsoft Outlook 2016
- Microsoft Access 2016
- Microsoft Publisher 2016

Launcher berada di:

```text
/usr/share/applications/
```

Icon berada di:

```text
/usr/share/icons/hicolor/256x256/apps/
```

Contoh:

```text
word2016.png
excel2016.png
powerpoint2016.png
outlook2016.png
access2016.png
publisher2016.png
```

---

# 8. Font

Font dari:

```text
FuentesOffice365.zip
```

dipasang ke Wine prefix:

```text
~/.office2016/drive_c/windows/Fonts/
```

Installer juga menangani kondisi ketika file font dari instalasi sebelumnya memiliki ownership/permission yang menyebabkan error seperti:

```text
Permission denied:
~/.office2016/drive_c/windows/Fonts/tahoma.ttf
```

Permission diperbaiki hanya pada direktori Fonts di prefix.

---

# 9. Verifikasi setelah instalasi

Jalankan:

```bash
ls -lh /usr/share/icons/hicolor/256x256/apps/*2016*.png
```

Harus terdapat enam icon:

```text
word2016.png
excel2016.png
powerpoint2016.png
outlook2016.png
access2016.png
publisher2016.png
```

Cek launcher:

```bash
ls -lh /usr/share/applications/*2016.desktop
```

---

# 10. Menjalankan Office

Setelah instalasi selesai, buka menu **Applications / Show Apps** GNOME dan cari:

```text
Microsoft Word 2016
Microsoft Excel 2016
Microsoft PowerPoint 2016
```

Launcher menggunakan WineCX secara langsung.

---

# 11. Jika icon belum muncul

Refresh cache:

```bash
sudo gtk-update-icon-cache -f -t /usr/share/icons/hicolor
sudo update-desktop-database /usr/share/applications
```

Kemudian logout/login GNOME.

Jika masih belum muncul, cek:

```bash
ls -lh /usr/share/icons/hicolor/256x256/apps/*2016*.png
grep -R "^Icon=" /usr/share/applications/*2016.desktop
```

---

# 12. Log instalasi

Log dibuat di:

```text
~/Downloads/office2016_v3_13_3.log
```

Jika instalasi mengalami masalah, kirim isi log tersebut untuk diagnosis.

---

# 13. Memulai ulang instalasi

Installer **tidak dirancang untuk menghapus semuanya secara otomatis**.

Ini disengaja agar:

- WineCX tidak perlu di-download ulang
- Office prefix tidak hilang
- Office tidak perlu diinstall ulang
- source file tetap tersedia
- instalasi yang sudah berhasil tidak rusak

Jika ingin melakukan clean install, hapus prefix hanya setelah memahami konsekuensinya:

```bash
rm -rf ~/.office2016
```

> Jangan menjalankan perintah ini jika Anda hanya ingin memperbaiki launcher, icon, font, atau tahap post-install.

---

# 14. Troubleshooting

### `setup.exe not found`

Pastikan ISO ada dengan nama yang tepat:

```text
SW_DVD5_Office_Professional_Plus_2016_W32_English_MLF_X20-41353.ISO
```

### `winecx.zip` tidak ditemukan

Pastikan:

```text
~/Downloads/winecx.zip
```

tersedia.

### Icon tidak ditemukan

Pastikan:

```text
~/Downloads/Requerimientos Office 2016.zip
```

tersedia.

Installer akan mencari:

```text
Requerimientos Office 2016/Office 2016 icons.zip
```

dan mengekstraknya jika diperlukan.

### Permission denied pada font

V3.13.4 sudah menangani ownership/permission font yang berasal dari instalasi sebelumnya.

### Office terdeteksi COMPLETE

Ini normal.

Installer akan melewati `setup.exe` dan melanjutkan tahap post-install.

---

# 15. Lisensi dan distribusi

Repository ini hanya berisi **script instalasi**.

File Microsoft Office, ISO, font proprietary, DLL proprietary, dan materi berhak cipta lainnya **tidak disertakan dalam repository**.

Pengguna bertanggung jawab memastikan bahwa mereka memiliki hak/lisensi yang diperlukan untuk memperoleh dan menggunakan file tersebut.

Jika menyediakan source melalui Google Drive, gunakan file yang Anda memang berhak bagikan dan atur permission Google Drive sesuai kebutuhan.

---

# 16. Kontribusi

Pull request dan issue dipersilakan untuk:

- perbaikan kompatibilitas Fedora
- perbaikan installer
- perbaikan launcher
- perbaikan icon
- perbaikan dokumentasi
- peningkatan error handling

---

## License

Lisensi repository ini dapat ditentukan oleh pemilik repository.

**Catatan:** lisensi repository script ini tidak memberikan hak apa pun atas Microsoft Office atau komponen proprietary Microsoft.
