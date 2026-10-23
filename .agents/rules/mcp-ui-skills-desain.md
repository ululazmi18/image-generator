---
trigger: model_decision
description: Aktif saat merancang atau merombak antarmuka pengguna (web, mobile, CLI/TUI layout), palet warna harmonis, tipografi, semantik ikon, penempatan emoji, atau animasi UI.
---

# SERVER MCP: UI-SKILLS & STANDAR VISUAL CRAFT

Pedoman ini mengatur kewajiban mutlak memanggil server MCP `ui-skills` saat mengerjakan elemen visual, tata letak, palet warna, tipografi, dan penempatan emoji.

---

## 1. Kewajiban Mutlak Penggunaan UI-Skills
- **Wajib dipanggil secara otomatis dan mandiri** setiap kali merancang, memoles (*deslop*), merombak, atau mereview antarmuka visual apapun tanpa menunggu perintah.
- Panggil `list_skills` dan `get_skill` untuk menarik aturan industri terkait (`baseline-ui`, `fixing-accessibility`, `fixing-motion-performance`, dsb.).

---

## 2. Cakupan Standar Desain Visual
1. **Layout & Tata Letak Antarmuka:** Web apps, mobile responsive, hingga **TUI / Terminal UI / CLI Layout** (box-drawing Unicode/ASCII, tabel berspasi rapi, hierarki visual CLI ergonomis).
2. **Ikon Semantik:** Pasangkan ikon yang selaras dengan makna kontekstualnya (*semantic icon pairing*), SVG rapi, dan desain simbol grafis yang konsisten.
3. **Penyelarasan Emoji (*Anti-Emoji Slop*):** Penempatan emoji harus terukur, presisi, dan elegan. Dilarang menghamburkan emoji sembarangan yang menurunkan kewibawaan antarmuka.
4. **Penyelarasan Warna (Color Harmony):** Standar kontras aksesibilitas WCAG 2.2, semantic color tokens (primary, surface, muted, accent, destructive), dilarang menggunakan gradien norak (*anti-neon/purple slop*).
5. **Tipografi & Micro-interactions:** Skala font berimbang (`text-balance`, `tabular-nums`), animasi ringan berbasis GPU compositor $\le 200\text{ ms}$, dan ramah pembaca layar (*screen-reader*).
