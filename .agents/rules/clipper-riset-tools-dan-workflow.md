---
description: Aktif saat melakukan riset video sumber YouTube Shorts, analisis channel/view, validasi hashtag/keyword, audit thumbnail/judul, atau menerapkan alur kerja clipper.
trigger: model_decision
globs: "**/*"
---

# PANDUAN DAN PROTOKOL RISET YOUTUBE SHORTS (CLIPPER WORKFLOW)

Aturan ini menetapkan toolkit gratis dan standar operasional riset klip YouTube Shorts berbasis performa trafik publik.

---

## 1. Stack Toolkit Gratis Riset & Analisis Shorts

Agen dan tim clipper mengandalkan kombinasi tool gratis tanpa keharusan langganan berbayar:

### A. Analisis Channel & Trafik View
- **CreatorSift:** Menemukan video terbaik/outlier dari suatu channel, median view, dan konsistensi upload publik tanpa login.
- **YouTube Data Viewer:** Ekstraksi granular metadata video (view eksak, like, komentar, tanggal upload, tag tersembunyi, hashtag, durasi).
- **Postigniter & TubeLeader:** Pemantauan engagement, pola upload, dan perbandingan performa kompetitor.
- **MiniWebTool & StatFlare:** Audit cepat usia channel, total penayangan, dan rata-rata views.

### B. Riset Keyword & Hashtag
- **Keyword Tool YouTube:** Generator keyword, tag, dan hashtag spesifik pencarian YouTube.
- **YouSEO Shorts Tools & View2:** Rekomendasi hashtag khusus Shorts berdasarkan niche dan kalkulator engagement.
- **Google Trends (Filter YouTube Search):** Validasi apakah topik/tokoh sedang naik daun (*trending*) atau menurun.

### C. Audit Thumbnail & Judul
- **AnalyzeVid:** Penilaian daya tarik judul, generator ide, dan identifikasi video trending.
- **View2 Thumbnail Previewer:** Simulasi tampilan thumbnail dan judul pada feed mobile dan Shorts.
- **VideoDubber:** Analisis kontras warna, keterbacaan tipografi, dan komposisi frame awal.

---

## 2. Kombinasi Toolkit Inti Rekomendasi Praktis

Untuk efisiensi kerja harian, gunakan kombinasi 5 pilar utama:
1. **CreatorSift** $\rightarrow$ Menemukan video terbaik/paling menonjol dari channel podcast master.
2. **YouTube Data Viewer** $\rightarrow$ Membedah data teknis (tag, hashtag, tanggal rilis, rasio like-komentar).
3. **Keyword Tool YouTube** $\rightarrow$ Menentukan variasi kata kunci dan hashtag pencarian.
4. **AnalyzeVid / View2** $\rightarrow$ Menguji kekuatan hook judul dan keterbacaan visual frame awal.
5. **Google Trends** $\rightarrow$ Memastikan topik memiliki volume minat penonton global yang stabil/tinggi.

---

## 3. SOP Kriteria Pemilihan Video Sumber (Kliping)

Saat meneliti episode podcast untuk dipotong, video sumber **wajib memenuhi indikator berikut**:
1. **Outlier View:** Jumlah views jauh melampaui rata-rata video biasa di channel tersebut.
2. **Resensi Waktu Baru:** Video masih segar atau memiliki relevansi topik yang sedang hangat diperbincangkan.
3. **Tingkat Komentar Tinggi:** Menandakan adanya perdebatan, polarisasi, atau keterikatan emosional audiens yang kuat.
4. **Pola Berulang:** Topik serupa telah terbukti sukses di beberapa video/kreator lain.
5. **Akselerasi Cepat:** Kurva penambahan views meningkat tajam dalam waktu singkat setelah rilis.
6. **Kemandirian Konteks (Self-Contained Moment):** Momen 30–50 detik yang dapat langsung dipahami dan memiliki *punchline/value* utuh tanpa perlu menonton video 2 jam penuh.

---

## 4. Protokol Penemuan Rekursif Channel Clipper (Recursive Discovery Loop)

Untuk mempelajari tren pemotongan klip nyata di audiens, agen tidak hanya bersandar pada channel podcast utama, melainkan wajib menjalankan siklus eksplorasi channel clipper pihak ketiga (*third-party/fan clippers*):
1. **Inisiasi dari Hashtag/Query Khusus:** Mulai dari hashtag klip (`#podcastclips`, `#jreclips`, `#doacclips`, `#clips`) atau query pencarian klip Shorts.
2. **Filter & Identifikasi Akun Clipper:** Pisahkan antara channel podcast master dengan channel kurator klip (mengandung kata *clips, moments, mindset, wisdom, highlights, vault*).
3. **Penetrasi Tab `/shorts/` Channel Clipper:** Masuk ke tab `/shorts` resmi channel clipper tersebut dan ekstrak video-video Shorts terbaik (judul, thumbnail frame awal, transkrip dialog, durasi, view count).
4. **Pemanenan Hashtag Berulang (Looping):** Kumpulkan hashtag baru yang disematkan para clipper ke dalam pool database, lalu gunakan hashtag baru tersebut untuk menemukan ekosistem channel clipper berikutnya secara berulang (*recursive cycle*).

