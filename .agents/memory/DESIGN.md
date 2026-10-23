# DESIGN CONTRACT & VISUAL STANDARDS (DESIGN.md)

## 1. Visual Foundation
- **Style Archetype:** Raycast / Terminal Cyber-Firefox Aesthetic.
- **Color Palette (ANSI TrueColor & 256 Colors):**
  - Accent / Primary: `RGB(255, 74, 28)` (Firefox Vibrant Orange / Amber).
  - Background Neutral: Dark Terminal Slate `RGB(15, 23, 42)`.
  - Border: Dimmed Slate `RGB(71, 85, 105)`.
  - Success Indicator: `RGB(74, 222, 128)` (Emerald Green).
  - Info / Secondary: `RGB(56, 189, 248)` (Electric Cyan).
  - Text Muted: `RGB(148, 163, 184)`.
  - Text High-Contrast: `RGB(248, 250, 252)`.

## 2. Terminal UI Gates (CLI/Batch Launcher)
- **Hierarchy:** Banner header dengan border rapi `+======+`, sub-header dengan badge status, dan informasi profil terstruktur.
- **Encoding:** Wajib UTF-8 (`chcp 65001 >nul` di Batch, `sys.stdout.reconfigure(encoding="utf-8")` di Python).
- **Feedback:** Menampilkan indikator status peluncuran yang jelas (`>> Membuka jendela Firefox...`) tanpa layar berkedip (*flicker-free*).
- **Anti-Slop:** Tidak menggunakan karakter acak atau teks polos tanpa format; semua status diberi badge semantik (`[READY]`, `[ACTIVE]`, `[ERROR]`).
