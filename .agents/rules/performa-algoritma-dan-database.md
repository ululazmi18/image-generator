---
trigger: model_decision
description: Aktif saat mengoptimalkan performa kode, efisiensi algoritma (kompleksitas waktu dan memori O(1)/O(N)), optimasi kueri database, penambahan indeks, atau paginasi data.
---

# OPTIMALISASI PERFORMA ALGORITMA & BASIS DATA

Pedoman ini mengatur efisiensi komputasi, penggunaan memori/CPU, serta optimalisasi kueri basis data pada pemrosesan data.

---

## 1. Efisiensi Algoritma & Komputasi
- Hindari perulangan bersarang yang tidak efisien (*redundant nested loops*) atau komputasi berulang.
- Gunakan struktur data yang tepat untuk pencarian cepat ($O(1)$ seperti `Set` atau `Map`/kamus) daripada memindai array berulang kali ($O(N)$).
- Optimalkan konsumsi memori dan siklus CPU, terutama saat memproses himpunan data besar atau proses streaming data.

---

## 2. Efisiensi Kueri Basis Data
- Cegah masalah kueri $N+1$ dengan teknik *eager loading*, *batch fetching*, atau *JOIN* yang efisien.
- Pastikan kolom-kolom yang sering digunakan dalam klausa pencarian, filter, dan pengurutan memiliki indeks basis data yang tepat.
- Terapkan teknik paginasi (*pagination* berbasis cursor atau limit/offset) dan *lazy loading* untuk mencegah pemuatan seluruh data sekaligus ke memori.
