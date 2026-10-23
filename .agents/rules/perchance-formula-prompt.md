---
trigger: model_decision
description: Aktif saat pengguna meminta membuat atau menyusun prompt gambar/teks untuk Perchance.org, membahas formula prompt 5 blok, negative prompt, tag emphasis, atau strategi positive pivot.
---

# PERCHANCE.ORG — FORMULA PROMPT GAMBAR & TEKS

> Referensi ini terhubung dengan `perchance-platform-dasar.md` dan `perchance-tips-dan-contoh.md`.

## 1. Formula Prompt Gambar — Struktur 5 Blok

```
[1. STYLE] + [2. SUBJECT] + [3. ENVIRONMENT] + [4. LIGHTING] + [5. QUALITY]
```

### Blok 1 — STYLE (Gaya Visual) ← SELALU DI AWAL
Model AI membaca elemen awal dengan bobot lebih tinggi.

| Kategori | Keyword |
|:--|:--|
| **Fotografi** | `photorealistic`, `35mm photography`, `DSLR photo`, `cinematic photography`, `macro lens` |
| **Seni Digital** | `digital art`, `concept art`, `cyberpunk art`, `fantasy illustration` |
| **Lukisan** | `oil painting`, `watercolor`, `acrylic painting`, `impressionism` |
| **3D Render** | `3D render`, `octane render`, `unreal engine 5`, `blender render` |
| **Anime/Manga** | `anime style`, `manga illustration`, `Studio Ghibli style`, `cel-shaded` |
| **Pixel Art** | `pixel art`, `16-bit`, `retro game art`, `voxel art` |

### Blok 2 — SUBJECT (Subjek Utama)
Detail spesifik: usia, fisik, rambut, pakaian, pose, ekspresi.
```
✅ "A 25-year-old woman with silver hair, wearing black leather jacket, holding a katana"
❌ "A woman"
```

| Aspek | Contoh |
|:--|:--|
| **Usia/Fisik** | `young`, `elderly`, `muscular`, `25-year-old` |
| **Rambut** | `silver braided hair`, `short black pixie cut`, `flowing red curls` |
| **Pakaian** | `ornate samurai armor`, `Victorian dress`, `cyberpunk hoodie` |
| **Pose/Aksi** | `standing tall`, `sitting cross-legged`, `wielding a sword` |
| **Ekspresi** | `smiling warmly`, `intense gaze`, `melancholic expression` |

### Blok 3 — ENVIRONMENT (Latar Belakang)
```
"In a misty ancient forest, moss-covered rocks, towering pine trees"
"Futuristic city rooftop at night, holographic billboards, flying cars"
"Cozy café interior, warm wooden furniture, rain on window"
```

### Blok 4 — LIGHTING & ATMOSPHERE
| Tipe | Keyword |
|:--|:--|
| **Natural** | `golden hour`, `sunrise`, `overcast sky`, `moonlight` |
| **Studio** | `studio lighting`, `softbox`, `rim light`, `three-point lighting` |
| **Dramatis** | `dramatic shadows`, `chiaroscuro`, `volumetric light`, `god rays` |
| **Suasana** | `moody`, `ethereal`, `warm glow`, `cold blue tones`, `soft bokeh` |
| **Sinematik** | `cinematic lighting`, `film noir`, `anamorphic lens flare` |

### Blok 5 — QUALITY KEYWORDS
```
masterpiece, best quality, highly detailed, sharp focus, intricate textures,
8k resolution, professional photography, award-winning, artstation trending
```

Prioritas: `Tier 1` masterpiece/best quality → `Tier 2` sharp focus/8k → `Tier 3` artstation/trending → `Tier 4` octane render/ray tracing.

## 2. Contoh Prompt Gambar Lengkap

**Fotorealistik:**
```
Cinematic photography, 35mm lens, a young Japanese woman in a red kimono
walking through a bamboo forest path, autumn leaves falling, golden hour
sunlight filtering through the bamboo, soft bokeh, warm tones,
highly detailed, sharp focus, masterpiece, 8k resolution
```

**Fantasy Art:**
```
Digital fantasy illustration, a powerful dragon perched on a mountain peak,
glowing orange eyes, massive wings spread wide, storm clouds gathering,
lightning bolts in background, epic cinematic lighting, vibrant colors,
octane render, highly detailed scales, masterpiece
```

**Anime:**
```
Anime illustration, Studio Ghibli style, a young adventurer with a backpack
standing at the edge of a floating island, vast sky with fluffy clouds,
wind blowing through hair, warm sunset colors, cel-shaded, clean linework,
soft pastel palette, beautiful scenery
```

## 3. Formula Prompt Teks

### Struktur Efektif
```
instruction: [PERAN] + [KONTEKS] + [BATASAN]
startWith:   [FORMAT AWAL OUTPUT]
stopSequences: [PENGHENTI GENERASI]
```

### Teknik A — Role-Playing
```javascript
text({
  instruction: "Anda adalah Gandalf. Bicaralah bijaksana penuh teka-teki.",
  startWith: "Gandalf berbicara: \"",
  stopSequences: ["\""]
});
```

### Teknik B — Format Steering
```javascript
text({
  instruction: "Buat profil karakter RPG: Nama, Ras, Kelas, Level, Kekuatan.",
  startWith: "📋 PROFIL KARAKTER\n═══════════════\n🏷️ Nama: ",
  stopSequences: ["\n\n\n"]
});
```

### Teknik C — Vision / Multi-modal
```javascript
text({
  instruction: ["Analisis gambar ini.", imageBlob],
  startWith: "Berdasarkan gambar, "
});
```

## 4. Negative Prompt — Strategi & Template

### Efektif vs Tidak Efektif
| ✅ Efektif (Cacat Teknis) | ❌ Kurang Efektif |
|:--|:--|
| `blurry, low quality` | `no glasses` → AI fokus pada "glasses" |
| `distorted hands, extra fingers` | `not realistic` → ambigu |
| `watermark, text, logo` | `not anime style` → nyatakan gaya positif |

### Template Universal
```
blurry, low resolution, bad anatomy, bad hands, extra fingers, extra limbs,
distorted face, deformed body, oversaturated, watermark, signature, text,
logo, cropped, out of frame, worst quality, low quality, jpeg artifacts,
ugly, duplicate, morbid, mutilated
```

### Template Potret/Manusia
```
bad anatomy, bad hands, extra fingers, missing fingers, fused fingers,
too many fingers, long neck, distorted face, cross-eyed, asymmetric eyes,
bad proportions, deformed limbs, extra limbs, mutated hands
```

### Template Lanskap/Arsitektur
```
blurry, low quality, cropped, out of frame, watermark, text, signature,
oversaturated, washed out, pixelated, noisy, grainy
```

### Template Anime/Ilustrasi
```
bad anatomy, bad proportions, extra limbs, deformed, disfigured,
low quality, worst quality, normal quality, lowres, blurry
```

### Strategi "Positive Pivot"
Model FLUX sering salah menginterpretasi negasi. Nyatakan secara **positif**:

| ❌ Negative | ✅ Positive Pivot |
|:--|:--|
| "no blurry background" | "sharp, clear focus throughout" |
| "no glasses" | "clear face, bare face, without accessories" |
| "not dark" | "bright, well-lit, high-key lighting" |
| "no watermark" | *(tetap di negative prompt — pengecualian)* |
