// GECKO NATIVE STEALTH SCRIPT — ELIMINASI FLAG OTOMASI WEBDRIVER
// Dijalankan pada document_start di semua window dan iframe

(function () {
  "use strict";

  try {
    const win = window.wrappedJSObject;
    if (!win || !win.Navigator || !win.Navigator.prototype) {
      return;
    }

    // 1. Definisikan native getter palsu dengan identitas "get webdriver"
    const getter = exportFunction(function webdriver() {
      return false;
    }, win);

    try {
      win.Object.defineProperty(getter, "name", { value: "get webdriver", configurable: true });
    } catch (_e) {}

    // 2. Clone descriptor ke kompartemen halaman web TANPA setter (WebIDL readonly attribute)
    const desc = cloneInto(
      {
        get: getter,
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

    // 5. Normalisasi window.outerWidth & outerHeight jika dalam mode headless
    if (win.outerWidth === win.innerWidth && win.outerHeight === win.innerHeight) {
      try {
        win.Object.defineProperty(win, "outerWidth", { value: win.innerWidth + 16, configurable: true });
        win.Object.defineProperty(win, "outerHeight", { value: win.innerHeight + 85, configurable: true });
      } catch (_dimErr) {}
    }
  } catch (_err) {
    // Abaikan jika konteks halaman terisolasi atau di-restrict
  }
})();
