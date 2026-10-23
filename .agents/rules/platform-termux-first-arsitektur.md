---
trigger: model_decision
description: Aktif saat merancang aplikasi Python untuk Termux Android ARM64, menetapkan target runtime, atau menerapkan prinsip zero regresi kompatibilitas lintas-platform.
---

# ARSITEKTUR TERMUX-FIRST (TARGET RUNTIME ANDROID ARM64)

Pedoman ini mengatur penetapan lingkungan target utama Termux pada perangkat Android, peran Windows sebagai mesin pengembangan sementara, dan prinsip nol regresi kompatibilitas Termux.

---

## 1. Lingkungan Target Utama (Production Environment)
- **Target Utama:** Termux (Android OS, Linux ARM64) dengan Python 3.
- **Peran Windows:** Sistem operasi Windows hanya digunakan sebagai mesin pengembangan (*development*) dan pengujian sintaksis lokal sementara.
- **Prinsip Nol Regresi Termux:** Dilarang keras menambahkan kode, pustaka, atau perintah yang hanya dapat berjalan di Windows (*Windows-only*) tanpa menyediakan implementasi padanan yang berjalan sempurna di Linux/Termux.
