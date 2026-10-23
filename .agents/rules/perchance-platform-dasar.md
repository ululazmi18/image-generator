---
trigger: model_decision
description: Aktif saat pengguna meminta membuat generator, plugin, atau kode untuk platform Perchance.org, atau menyebut sintaksis Perchance (Lists Editor, text-to-image-plugin, ai-text-plugin).
---

# PERCHANCE.ORG — FONDASI PLATFORM & PLUGIN AI

> Referensi ini terhubung dengan `perchance-formula-prompt.md` dan `perchance-tips-dan-contoh.md`.

## 1. Tentang Perchance

Platform open-source gratis untuk membuat generator acak & aplikasi web interaktif berbasis browser. Plugin AI berjalan di GPU server Perchance — **tidak perlu API Key**.

| Komponen | Fungsi |
|:--|:--|
| **Lists Editor** | Variabel, daftar acakan, bobot, logika evaluasi |
| **HTML Editor** | Tampilan UI (HTML/CSS/JS) mengaitkan data dari Lists Editor |
| **Plugin Ecosystem** | Modul ekstensi: Stable Diffusion/FLUX (gambar), LLM (teks) |

## 2. Sintaksis Lists Editor

### Daftar Acak
```perchance
character
  seorang ksatria cyberpunk
  seorang penyihir elemen
```
Panggil: `[character]` → pilih satu secara acak.

### Inline Choice & Bobot
```perchance
weapon = {pedang laser|tongkat sihir|pistol plasma}
rarity
  Biasa ^5
  Langka ^2
  Legendaris ^0.1
```

### Referensi Antar-List
```perchance
output
  [character] memegang [weapon] [place].
```

### Impor Generator Lain
```perchance
kata_benda = {import:noun}
warna = {import:color}
```

### Properties Transformasi Teks
| Property | Fungsi |
|:--|:--|
| `.titleCase` | Kapital tiap kata |
| `.upperCase` | Seluruh huruf besar |
| `.lowerCase` | Seluruh huruf kecil |
| `.capitalize` | Kapital huruf pertama |
| `.a` | Tambah artikel "a/an" |
| `.s` | Bentuk jamak |
| `.ed` | Bentuk lampau |
| `.ing` | Bentuk gerund |

### Range Angka & Variabel Persisten
```perchance
age = {18-35}
$heroName = [name]
$heroWeapon = [weapon]
output
  $heroName mengambil $heroWeapon.
```
Variabel `$` menyimpan nilai tetap selama satu sesi evaluasi.

## 3. HTML Editor

```html
<p id="outputEl">[prompt]</p>
<button onclick="update(outputEl)">Acak Ulang</button>
```
- `[variabel]` — Tampilkan hasil evaluasi Lists Editor
- `update(element)` — Refresh elemen dengan evaluasi baru
- `root.namaList.evaluateItem` — Akses & evaluasi list dari JavaScript

## 4. Plugin Text-to-Image

### Impor
```perchance
image = {import:text-to-image-plugin}
```

### Penggunaan dari Lists Editor
```perchance
prompt = cyberpunk warrior, 8k, masterpiece
output
  [image(prompt)]
```

### Penggunaan via JavaScript
```javascript
let result = await image({
  prompt: "cyberpunk cat on neon rooftop",
  resolution: "512x768",
  removeBackground: false,
  guidanceScale: 7
});
```

### Parameter Lengkap
| Parameter | Tipe | Default | Deskripsi |
|:--|:--|:--|:--|
| `prompt` | String | — | **Wajib.** Deskripsi gambar |
| `negativePrompt` | String | — | Elemen dihindari |
| `resolution` | String | `"512x512"` | `512x512`, `768x768`, `512x768`, `768x512`, `1024x1024` |
| `guidanceScale` | Number | `7` | Kepatuhan prompt (1–30) |
| `seed` | Number | `-1` | Seed reproduksibilitas. `-1` = acak |
| `removeBackground` | Boolean | `false` | Hapus background → PNG transparan |
| `style` | String | — | CSS kustom elemen gambar |

### Inline Parameter (tiga titik dua `:::`)
```perchance
prompt
  warrior (resolution:::512x768) (guidanceScale:::8) (negativePrompt:::blurry, low quality)
```

### Tag Emphasis (Bobot Kata)
```
(kata:1.2)   → Boost 1.2x
(kata:0.8)   → Kurangi bobot
((kata))     → ~1.44x
(((kata)))   → Penekanan triple
```

## 5. Plugin AI Text (LLM)

### Impor
```perchance
text = {import:ai-text-plugin}
```

### Penggunaan via JavaScript
```javascript
let result = await text({
  instruction: "Anda adalah detektif noir. Jawab sinis.",
  startWith: "Laporan Kasus #402:\n",
  stopSequences: ["\n\n", "User:", "---"],
  outputTo: document.getElementById('storyOutput')
});
```

### Parameter Lengkap
| Parameter | Tipe | Deskripsi |
|:--|:--|:--|
| `instruction` | String/Array | **Wajib.** Perintah utama. Array: teks + Blob gambar (Vision) |
| `startWith` | String | Teks pembuka yang dilanjutkan AI |
| `stopSequences` | Array | Kata penghenti generasi |
| `hideStartWith` | Boolean | Sembunyikan `startWith` di UI |
| `outputTo` | Element | Elemen DOM untuk streaming |
| `onChunk` | Function | Callback `({text, isFirstChunk, isLastChunk})` |
| `onFinish` | Function | Callback saat selesai |
| `endButtons` | String | `"none"` untuk sembunyikan tombol Lanjut/Edit |

### Token Counter & Stop Manual
```javascript
let count = text.countTokens("Teks");
// Maks konteks: text.idealMaxContextTokens (~6000)

let pending = text({instruction: "...", outputTo: div});
stopButton.onclick = () => pending.stop();
```
