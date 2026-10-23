---
description: Aktif saat merancang atau membuat animasi motion graphics berbasis web/browser, menegakkan hukum Anti-PPT, determinisme linimasa GSAP, struktur panggung scale paten, dan rendering video ringan tanpa drop frame.
trigger: model_decision
globs: "**/*"
---

# MOTION GRAPHICS WEB (BANG-MOTION STANDARDS)

Aturan ini wajib ditegakkan saat merancang atau memproduksi motion graphics di browser:

## 1. Hukum Mutlak Anti-PPT
- **Bukan Slide Deck:** Dilarang menukar adegan dengan fade-in/fade-out `<section>` kaku. Adegan berganti karena kamera dunia (`#world`) bergerak, sudut pandang berpindah (*whip/cut* pada ritme audio), atau *object wipe* berkedalaman melintas.
- **Batasan Teks:** Maksimal satu kalimat inti (≤ 5 kata) + satu objek fokus per adegan. Dilarang menumpuk 3 tingkat teks (*kicker* + judul + paragraf deskripsi).
- **Tipografi Alami:** Gunakan *Sentence case* bobot 500-600. Default tanpa tanda titik `.` pada judul/frasa pendek.

## 2. Determinisme Waktu 100%
- Seluruh visual wajib merupakan fungsi murni dari master timeline GSAP `tl.time()`. Dilarang membaca jam sistem acak (`Date.now()`, `performance.now()`) atau akumulasi per frame agar scrub dan ekspor frame selalu identik.
- Terapkan detik absolut pada timeline GSAP (`tl.fromTo(..., atSeconds)`), bukan *chaining* relatif yang rapuh.

## 3. Panggung & Rig Kamera
- Panggung dipatok tetap (`1920×1080` untuk 16:9 atau `1080×1920` untuk 9:16) dan di-*scale* otomatis via `Math.min(innerWidth/W, innerHeight/H)`.
- Rig `#world` membungkus canvas WebGL dan elemen DOM adegan agar zoom kamera memperbesar teks dan latar secara simultan. Lapisan optik lensa (*light leak, grain, vignette*) berada di luar `#world`.

## 4. Efisiensi & Kontras Latar
- Latar wajib tunduk pada keterbacaan teks (luminance area teks ≤ 25% untuk teks putih, atau pasang *pocket gradient* gelap).
- Gunakan *Directional Motion Blur* via SVG `<feGaussianBlur>` terarah dan wajib dilepas (`filter: 'none'`) setelah animasi selesai demi efisiensi render.

Referensi lengkap implementasi: [docs/bang_motion_comprehensive_handbook.md](file:///d:/Documents/quran-video-studio/docs/bang_motion_comprehensive_handbook.md).
