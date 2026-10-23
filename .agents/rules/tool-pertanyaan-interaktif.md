---
trigger: model_decision
description: Aktif saat mengajukan pertanyaan ke pengguna, klarifikasi kebutuhan, validasi keputusan, atau membuat kuis interaktif dengan opsi bergradasi nilai yang posisinya diacak.
---

# FITUR BAWAAN: MODAL INTERAKTIF PERTANYAAN (ASK_QUESTION)

Pedoman ini mengatur pemanfaatan modal antarmuka `ask_question`, standar kualitas opsi berbobot (*graded options*), dan pengacakan posisi opsi mutlak.

---

## 1. Pemanfaatan Modal Interaktif (`ask_question`)
- **Wajib digunakan secara proaktif** untuk setiap pertanyaan klarifikasi kebutuhan, validasi keputusan arsitektur, uji kemampuan (*skill assessment*), kuis kompetensi, maupun survei opsi.
- Dilarang menanyakan pertanyaan pilihan ganda melalui teks obrolan biasa secara pasif jika dapat disajikan melalui modal antarmuka interaktif `ask_question`.

---

## 2. Kualitas Opsi Bergradasi Nilai (*Graded Competency Options*)
- Pada sesi kuis atau pengetesan skenario, dilarang membuat opsi yang terlalu konyol atau mudah ditebak.
- Buat opsi-opsi yang tampak masuk akal (*plausible*) dengan tingkatan nilai kebenaran bergradasi (misalnya: 100%, 90%, 80%, 70%, 60%) untuk mengukur pemahaman pengguna secara presisi.

---

## 3. Pengacakan Posisi Opsi Mutlak (*Strictly Randomized Placement*)
- Urutan peletakan opsi bergradasi nilai **wajib diacak secara total** pada setiap pertanyaan.
- Dilarang menyusunnya berurutan (misal: opsi terbaik selalu di atas) agar posisi jawaban tidak membentuk pola yang dapat ditebak.
