---
trigger: model_decision
description: Aktif saat merancang atau membuat route, controller, middleware, endpoint API backend, skema request/response type-safe, serta penanganan HTTP status code.
---

# ALUR PEMBUATAN BACKEND & ENDPOINT API (API PROTOCOL)

Pedoman ini mengatur tahapan pembuatan rute, pengendali (*controllers*), skema validasi *type-safe*, dan integrasi layanan API backend.

---

## Tahap Pelaksanaan Pembuatan API

1. **Tahap 1 (Validasi Spesifikasi & Dokumen):**
   - Periksa spesifikasi kerangka kerja atau pustaka backend terkini menggunakan MCP (`context7`) untuk memastikan kompatibilitas sintaks versi terbaru.

2. **Tahap 2 (Skema Request & Response Type-Safe):**
   - Buat model validasi input data (*Pydantic*, *Zod*, *Joi*) dan skema respons yang *type-safe* secara ketat.

3. **Tahap 3 (Logika Bisnis & Middleware Autentikasi):**
   - Tulis logika bisnis modular, integrasi kueri basis data efisien, dan sertakan middleware otentikasi/otorisasi jika rute bersifat terlindungi (*protected*).

4. **Tahap 4 (Penanganan Galat & HTTP Status Code):**
   - Tangani setiap skenario kegagalan dengan HTTP Status Code yang tepat (200, 201, 400, 401, 403, 404, 500) dan payload galat yang terstruktur.

5. **Tahap 5 (Commit & Laporan):**
   - Uji endpoint, buat commit lokal `feat(api): <nama_endpoint>`, dan lampirkan contoh payload request/response pada laporan.
