// GECKO NATIVE STEALTH SCRIPT — ELIMINASI FLAG OTOMASI WEBDRIVER
// Dijalankan pada document_start di semua window dan iframe

(function () {
  "use strict";

  try {
    const win = window.wrappedJSObject;
    if (!win || !win.Navigator || !win.Navigator.prototype) {
      return;
    }

    // 1. Definisikan native getter & setter palsu menggunakan API exportFunction
    const getter = exportFunction(function () {
      return false;
    }, win);

    const setter = exportFunction(function (_val) {
      // no-op
    }, win);

    // 2. Clone descriptor ke kompartemen halaman web
    const desc = cloneInto(
      {
        get: getter,
        set: setter,
        enumerable: true,
        configurable: true,
      },
      win,
      { cloneFunctions: true }
    );

    // 3. Terapkan pada Navigator.prototype
    win.Object.defineProperty(win.Navigator.prototype, "webdriver", desc);

    // 4. Pastikan jika ada own property di navigator instance, hapus agar fallback ke prototype
    if (win.navigator && win.Object.prototype.hasOwnProperty.call(win.navigator, "webdriver")) {
      try {
        delete win.navigator.webdriver;
      } catch (_delErr) {}
    }
  } catch (_err) {
    // Abaikan jika konteks halaman terisolasi atau di-restrict
  }
})();
