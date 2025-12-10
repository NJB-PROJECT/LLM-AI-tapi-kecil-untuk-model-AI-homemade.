# AI Asisten Pribadi (Offline)

Ini adalah proyek AI Asisten pribadi yang berjalan **sepenuhnya offline** di laptop kamu, menggunakan teknologi Small Language Models (SLM) yang canggih namun ringan.

Fitur utama:
*   **Chat Cerdas**: Menggunakan model Qwen2.5 (atau lainnya).
*   **Mata (Vision)**: Bisa melihat gambar dan menjelaskannya (jika menggunakan model Vision seperti Qwen2-VL).
*   **Telinga & Mulut**: Bisa mendengar suara (Speech-to-Text) dan membalas dengan suara (Text-to-Speech).
*   **Baca Dokumen**: Bisa membaca isi file PDF, Word, dan Text.
*   **Ringan**: Dioptimalkan untuk berjalan di CPU (Laptop biasa).

## Persiapan (Instalasi)

Pastikan kamu sudah menginstall **Python** dan **VS Code**.

1.  **Buka Terminal** di VS Code (Ctrl + `).

2.  **Install Library Pendukung**:
    Ketik perintah berikut untuk menginstall semua kebutuhan:
    ```bash
    pip install -r requirements.txt
    ```
    *Catatan: Jika ada error saat install `llama-cpp-python` di Windows, kamu mungkin perlu menginstall "Visual Studio Build Tools" (pilih opsi "Desktop development with C++") dari website Microsoft.*

3.  **Download Model AI**:
    Jalankan script otomatis yang sudah disiapkan untuk mendownload "otak" AI-nya:
    ```bash
    python setup_models.py
    ```
    *Tunggu sampai selesai (sekitar 1-2 GB).*

4.  **Install FFMPEG (Wajib untuk Suara)**:
    Agar fitur suara jalan, kamu perlu `ffmpeg`.
    *   **Windows**: Download dari `ffmpeg.org` atau gunakan `winget install ffmpeg` di PowerShell.
    *   **Mac**: `brew install ffmpeg`
    *   **Linux**: `sudo apt install ffmpeg`

## Cara Menjalankan

Setelah semua siap, jalankan aplikasi dengan perintah:

```bash
streamlit run main.py
```

Browser kamu akan otomatis terbuka dengan tampilan Chat AI.

## Cara Pakai

1.  **Pilih Model**: Di sidebar sebelah kiri, pilih model yang mau dipakai (misal `qwen2.5` untuk teks cepat, atau `qwen2-vl` untuk gambar). Klik "Muat Model".
2.  **Chatting**: Ketik pesan seperti biasa.
3.  **Gambar**: Upload gambar lewat menu expander "Upload Gambar", lalu tanya tentang gambar itu.
    *   *Penting*: Pastikan kamu memilih model yang support Vision (seperti Qwen2-VL) saat tanya soal gambar.
4.  **Suara**: Klik tombol rekam mikrofon, bicara, lalu stop. AI akan mendengar.
5.  **Dokumen**: Upload PDF/Doc di sidebar, AI akan membaca isinya sebagai konteks tambahan.

## Tips

*   Jika laptop terasa berat, gunakan model yang ukurannya lebih kecil (1.5B atau 0.5B).
*   Untuk performa terbaik, tutup aplikasi berat lain saat menjalankan AI ini.
