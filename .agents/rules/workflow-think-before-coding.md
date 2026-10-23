---
trigger: model_decision
description: Aktif sebelum memulai implementasi kode, menegakkan analisis kebutuhan mendalam, pengungkapan asumsi secara eksplisit, dan klarifikasi ketidakjelasan tanpa menebak.
---

# PROTOKOL ANALISIS SEBELUM KODING (THINK BEFORE CODING)

Pedoman ini mengatur proses perumusan asumsi, penanganan ambiguitas, dan evaluasi *tradeoffs* sebelum baris kode pertama ditulis.

---

## 1. Prinsip Anti-Asumsi & Transparansi
- **Jangan berasumsi secara diam-diam:** Ungkapkan asumsi teknis secara eksplisit sebelum memulai pekerjaan.
- **Klarifikasi saat ambigu:** Jika instruksi pengguna memiliki multi-interpretasi atau kurang jelas, **berhenti sejenak** (*stop and clarify*). Sebutkan secara presisi bagian mana yang membingungkan dan tanyakan solusinya (gunakan modal `ask_question`).
- Dilarang memilih salah satu interpretasi secara sepihak tanpa konfirmasi jika terdapat risiko perbedaan ekspektasi.

---

## 2. Mengungkapkan *Tradeoffs* & Alternatif Lebih Sederhana
- Jika pengguna meminta solusi yang rumit padahal ada pendekatan yang jauh lebih sederhana dan efektif, sampaikan secara profesional dan berikan perbandingannya.
- Berikan masukan kritis yang berbobot (*push back when warranted*) demi kualitas arsitektur sistem.
