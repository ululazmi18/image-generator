---
trigger: model_decision
description: Aktif saat pengguna meminta contoh kode generator Perchance.org, tips iterasi prompt, konfigurasi seed/resolusi, atau referensi link resource Perchance.
---

# PERCHANCE.ORG — TIPS LANJUTAN, CONTOH & RESOURCE

> Referensi ini terhubung dengan `perchance-platform-dasar.md` dan `perchance-formula-prompt.md`.

## 1. Tips Lanjutan

### Strategi Iterasi Prompt
1. Mulai 10–15 kata: subjek & gaya
2. Generate → evaluasi hasil
3. Kurang tepat → tambah detail (pencahayaan, suasana)
4. Ada cacat → perbaiki negative prompt
5. Komposisi bagus → lock seed, tweak keyword
6. Ulangi sampai sempurna

**JANGAN** mulai dengan prompt 100+ kata — AI bingung ("prompt soup").

### Lock Seed untuk Konsistensi
```javascript
let result = await image({
  prompt: "your prompt...",
  seed: 42,
  resolution: "512x768"
});
```
Kunci seed, lalu modifikasi keyword tanpa mengubahnya.

### Aspect Ratio
| Rasio | Resolusi | Cocok Untuk |
|:--|:--|:--|
| 1:1 | `512x512` / `768x768` | Avatar, ikon, profil |
| 2:3 | `512x768` | Karakter full-body, poster |
| 3:2 | `768x512` | Pemandangan, banner |
| 1:1 HD | `1024x1024` | Detail tinggi, wallpaper |

### Akses List dari JavaScript
```javascript
let karakter = root.character.evaluateItem;  // Evaluasi acak
let prompt = root.imagePrompt.evaluateItem;
// JANGAN root.character langsung — itu objek, bukan string
```

### Alat Eksternal Pelengkap
Perchance tidak punya inpainting. Gunakan:
- **Upscayl** — tingkatkan resolusi
- **remove.bg** — hapus background lebih presisi
- **Cleanup.pictures** — hapus objek tidak diinginkan

## 2. Contoh Generator Lengkap

### Lists Editor
```perchance
// IMPOR PLUGIN
image = {import:text-to-image-plugin}
text = {import:ai-text-plugin}

// DATA ACAK
genre
  Cyberpunk Sci-Fi
  Dark Fantasy
  Misteri Noir
  Petualangan Steampunk
  Post-Apocalyptic

character
  seorang tentara bayaran dengan lengan siber
  seorang penyihir akademi yang terbuang
  seorang detektif yang dapat membaca pikiran
  seorang pilot pesawat uap antik
  seorang samurai ronin dari masa depan

location
  di gang sempit diterangi lampu neon
  di reruntuhan menara sihir antik
  di dalam kabin kapal udara berasap
  di puncak gedung pencakar langit berkarat
  di perpustakaan bawah tanah terlupakan

mood
  suasana misterius penuh ketegangan
  atmosfer epik penuh keberanian
  nuansa gelap dan melankolis
  vibe retrofuturistik penuh warna

// TEMPLATE PROMPT
storyInstruction
  Tulis cerita pendek (3 paragraf) bernuansa [genre] tentang [character] yang berada [location]. Buat alur menegangkan, [mood]. Bahasa Indonesia dramatis dan deskriptif.

imagePrompt
  Detailed digital concept art of [character] [location], [genre] atmosphere, cinematic lighting, dramatic shadows, masterpiece, highly detailed, sharp focus, 8k resolution, vibrant colors (resolution:::512x768) (guidanceScale:::8) (negativePrompt:::blurry, bad anatomy, low quality, distorted face, extra fingers, watermark)
```

### HTML Editor
```html
<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <title>AI Story & Art Generator</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: 'Inter', sans-serif;
      max-width: 800px; margin: 2rem auto; padding: 0 1rem;
      background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
      color: #e0e0e0; min-height: 100vh;
    }
    h1 {
      text-align: center; font-size: 2rem;
      background: linear-gradient(90deg, #bb86fc, #03dac6);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
      margin-bottom: 1.5rem;
    }
    .card {
      background: rgba(30,30,46,0.8); backdrop-filter: blur(10px);
      border: 1px solid rgba(187,134,252,0.2); border-radius: 12px;
      padding: 1.5rem; margin-bottom: 1.5rem;
      box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    }
    button {
      background: linear-gradient(135deg, #bb86fc, #6200ea);
      color: #fff; border: none; padding: 0.85rem 1.5rem;
      font-size: 1rem; font-weight: 700; border-radius: 8px;
      cursor: pointer; width: 100%; transition: all 0.3s ease;
    }
    button:hover { transform: translateY(-2px); box-shadow: 0 4px 20px rgba(187,134,252,0.5); }
    .content-box { line-height: 1.8; margin-top: 1rem; font-size: 0.95rem; }
    .image-container { text-align: center; margin-top: 1rem; }
    h2 { color: #03dac6; font-size: 1.2rem; margin-bottom: 0.5rem; }
    .loading { color: #bb86fc; font-style: italic; animation: pulse 1.5s ease-in-out infinite; }
    @keyframes pulse { 0%,100% { opacity:1 } 50% { opacity:0.4 } }
  </style>
</head>
<body>
  <h1>AI Story & Illustration Generator</h1>
  <div class="card">
    <button onclick="generateAll()">BUAT CERITA & GAMBAR BARU</button>
  </div>
  <div class="card">
    <h2>Cerita AI</h2>
    <div id="storyOutput" class="content-box">Klik tombol untuk mulai...</div>
  </div>
  <div class="card">
    <h2>Ilustrasi AI</h2>
    <div id="imageOutput" class="image-container">Gambar muncul di sini...</div>
  </div>
  <script>
    async function generateAll() {
      const storyDiv = document.getElementById('storyOutput');
      const imageDiv = document.getElementById('imageOutput');
      storyDiv.innerHTML = '<span class="loading">Menulis cerita...</span>';
      imageDiv.innerHTML = '<span class="loading">Merender ilustrasi...</span>';

      text({ instruction: root.storyInstruction.evaluateItem, outputTo: storyDiv });

      let imgHtml = await image(root.imagePrompt.evaluateItem);
      imageDiv.innerHTML = imgHtml;
    }
  </script>
</body>
</html>
```

## 3. Cheat Sheet Cepat

```
GAMBAR = [STYLE], [SUBJECT], [ENVIRONMENT], [LIGHTING], [QUALITY]
TEKS   = instruction (peran+konteks+batasan) + startWith + stopSequences
IMPORT = image = {import:text-to-image-plugin} | text = {import:ai-text-plugin}
ACAK   = [list], {a|b|c}, {1-100}, ^bobot, $variabel
TIPS   = Mulai singkat → Iterasi → Lock seed | Negative = cacat teknis saja
```

## 4. Resource & Link Penting

| Resource | URL |
|:--|:--|
| Welcome | `https://perchance.org/welcome` |
| Tutorial | `https://perchance.org/tutorial` |
| Contoh | `https://perchance.org/examples` |
| Generator Populer | `https://perchance.org/generators` |
| Plugin | `https://perchance.org/plugins` |
| Plugin Berguna | `https://perchance.org/useful-plugins` |
| Template Dasar | `https://perchance.org/basic-template#edit` |
| AI Image Generator | `https://perchance.org/ai-image-generator` |
| AI Photo Generator | `https://perchance.org/ai-photo-generator` |
| Text-to-Image Plugin | `https://perchance.org/text-to-image-plugin` |
| AI Text Plugin | `https://perchance.org/ai-text-plugin` |
| AI Text Plugin Demo | `https://perchance.org/ai-text-plugin-demo` |
| DIY API Server | `https://perchance.org/diy-perchance-api` |
| Discord Bot | `https://perchance.org/perchance-discord-bot` |
| Komunitas Lemmy | `https://lemmy.world/c/perchance` |
| Template Kosong | `https://perchance.org/minimal#edit` |
