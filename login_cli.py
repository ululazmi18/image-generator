"""LOGIN CLI — GOOGLE FLOW AUTHENTICATION & AUTOMATION MANAGER.

Modul dan perkakas baris perintah (CLI) untuk mengelola autentikasi akun Google
pada Google Flow secara 100% otomatis dari terminal tanpa perlu interaksi manual di browser.

Fitur Utama:
1. Full Automated Login (--auto / default):
   Pengguna hanya memasukkan email dan sandi di terminal. Skrip mengotomasi pengisian form
   Google secara langsung via peramban aman anti-deteksi bot (bebas blokir 'rrk=46').
   Jika Google meminta verifikasi 2FA (konfirmasi perangkat atau angka cocok), terminal akan
   otomatis mendeteksi dan menampilkan instruksi kepada pengguna. Sesi tersimpan permanen
   di browser_profile/cookies.sqlite lokal proyek.
2. Isolated Interactive Login (--login):
   Membuka peramban Firefox Portable lokal proyek secara mandiri TANPA flag Marionette.
3. Cookie Ingestion (--paste / --cookie):
   Menyuntikkan token/cookie sesi langsung dari string atau clipboard tanpa browser.
4. Headless Verification (--verify):
   Menguji keabsahan sesi Google Flow di background menggunakan mesin Marionette
   stealth tanpa menampilkan jendela di layar desktop.
5. Profile Auto-Sync (--sync):
   Menyinkronkan sesi dari profil browser eksternal yang sudah ada (opsional).
"""

import argparse
import os
import random
import re
import shutil
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

# Standar encoding UTF-8 untuk terminal Windows
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.theme import Theme

CUSTOM_THEME = Theme(
    {
        "info": "cyan",
        "success": "bold green",
        "warning": "bold yellow",
        "error": "bold red",
        "accent": "bold magenta",
        "muted": "dim white",
        "gold": "bold yellow",
        "brand": "bold color(208)",
    }
)
console = Console(theme=CUSTOM_THEME)

WORKSPACE_DIR = Path(__file__).resolve().parent
DEFAULT_TARGET_PROFILE = WORKSPACE_DIR / "browser_profile"
DEFAULT_TARGET_BIN = WORKSPACE_DIR / "firefox_portable" / "App" / "Firefox64" / "firefox.exe"
FLOW_HOME_URL = "https://flow.google.com/"


def save_playwright_cookies_to_firefox(
    cookies: list[dict], profile_dir: Path = DEFAULT_TARGET_PROFILE
) -> int:
    """Menyimpan daftar cookies hasil ekstraksi Playwright ke dalam cookies.sqlite profil lokal.
    
    Menegakkan standar Firefox Gecko 115+:
    - Masa kedaluwarsa (expiry) format milidetik 13-digit (bukan detik 10-digit).
    - Nilai schemeMap = 2 (HTTPS bitmask) untuk memastikan cookie dikirim di koneksi aman.
    - sameSite = 256 (SAMESITE_UNSET) untuk kompatibilitas penuh antar-domain Google.
    - Pembersihan cookie lama sebelum penyimpanan guna mencegah insiden CookieMismatch.
    - Checkpoint SQLite WAL langsung ke file database utama.
    """
    profile_dir.mkdir(parents=True, exist_ok=True)
    db_path = profile_dir / "cookies.sqlite"

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Pastikan tabel moz_cookies ada
    if not cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='moz_cookies'"
    ).fetchone():
        cur.execute(
            """
            CREATE TABLE moz_cookies (
                id INTEGER PRIMARY KEY,
                originAttributes TEXT NOT NULL DEFAULT '',
                name TEXT,
                value TEXT,
                host TEXT,
                path TEXT,
                expiry INTEGER,
                lastAccessed INTEGER,
                creationTime INTEGER,
                isSecure INTEGER,
                isHttpOnly INTEGER,
                inBrowserElement INTEGER DEFAULT 0,
                sameSite INTEGER DEFAULT 0,
                rawSameSite INTEGER DEFAULT 0,
                schemeMap INTEGER DEFAULT 0,
                isPartitionedAttributeSet INTEGER DEFAULT 0,
                updateTime INTEGER,
                CONSTRAINT moz_uniqueid UNIQUE (name, host, path, originAttributes)
            )
            """
        )
        conn.commit()

    # Hapus cookie autentikasi Google/Flow lama agar tidak tercampur (mencegah CookieMismatch)
    cur.execute(
        "DELETE FROM moz_cookies WHERE host LIKE '%google%' OR host LIKE '%flow%' OR host LIKE '%youtube%'"
    )
    conn.commit()

    cols = [c[1] for c in cur.execute("PRAGMA table_info(moz_cookies)").fetchall()]
    has_same_site = "sameSite" in cols
    has_scheme_map = "schemeMap" in cols
    has_update_time = "updateTime" in cols

    now = int(time.time())
    now_us = now * 1000000

    inserted = 0
    for c in cookies:
        name = c.get("name", "")
        val = c.get("value", "")
        domain = c.get("domain", "")
        path = c.get("path", "/")
        expires = c.get("expires", -1)
        if expires is None or expires < 0:
            expires_ms = (now + (365 * 24 * 3600)) * 1000
        else:
            expires_val = int(expires)
            expires_ms = expires_val * 1000 if expires_val < 1000000000000 else expires_val

        is_secure = 1 if c.get("secure") else 0
        is_http_only = 1 if c.get("httpOnly") else 0

        # Normalisasi host khusus OSID / Flow (harus host-only tanpa leading dot)
        if name in ("OSID", "__Secure-OSID") and domain.startswith("."):
            domain = domain.lstrip(".")

        # Konfigurasi SameSite untuk Firefox Gecko (256: SAMESITE_UNSET, 0: None, 1: Lax, 2: Strict)
        if name.startswith("__Secure-3P") or name in ("__Secure-OSID", "__Host-3PLSID"):
            ss_val = 0
        else:
            ss_val = 256

        scheme_map = 2  # HTTPS schemeMap bitmask

        insert_cols = [
            "originAttributes",
            "name",
            "value",
            "host",
            "path",
            "expiry",
            "lastAccessed",
            "creationTime",
            "isSecure",
            "isHttpOnly",
            "inBrowserElement",
        ]
        insert_vals = [
            "",
            name,
            val,
            domain,
            path,
            expires_ms,
            now_us,
            now_us,
            is_secure,
            is_http_only,
            0,
        ]

        if has_same_site:
            insert_cols.append("sameSite")
            insert_vals.append(ss_val)
        if has_scheme_map:
            insert_cols.append("schemeMap")
            insert_vals.append(scheme_map)
        if has_update_time:
            insert_cols.append("updateTime")
            insert_vals.append(now_us)

        cols_part = ", ".join(insert_cols)
        placeholders = ", ".join(["?"] * len(insert_vals))
        sql = f"INSERT OR REPLACE INTO moz_cookies ({cols_part}) VALUES ({placeholders})"
        cur.execute(sql, tuple(insert_vals))
        inserted += 1

    conn.commit()
    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    conn.close()
    return inserted


def automated_google_login(
    email: str | None = None,
    password: str | None = None,
    headless: bool = True,
    profile_dir: Path = DEFAULT_TARGET_PROFILE,
) -> bool:
    """Melakukan otomatisasi penuh login Google Flow dari terminal.
    
    Fitur:
    - Pengguna hanya memberikan email dan kata sandi di terminal.
    - Menggunakan mesin peramban aman dengan penangkal deteksi bot (anti rrk=46).
    - Mendeteksi verifikasi perangkat (2FA) dan mengekstrak nomor pencocokan secara otomatis.
    - Menyimpan seluruh token sesi ke browser_profile/cookies.sqlite proyek lokal.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        console.print("[error]✗ Pustaka playwright belum terpasang. Jalankan: pip install playwright[/error]")
        return False

    console.print(
        Panel(
            "[bold green]OTOMASI LOGIN GOOGLE FLOW PENUH[/bold green]\n\n"
            "Skrip akan secara otomatis mengisi email, sandi, dan mendeteksi verifikasi 2FA.\n"
            "Anda hanya perlu mengonfirmasi perangkat (ketuk Ya / pilih angka di ponsel) jika diminta Google.\n"
            "Seluruh sesi tersimpan 100% mandiri di dalam [cyan]browser_profile/[/cyan] lokal proyek.",
            box=box.ROUNDED,
            title="[cyan]Automated Login Engine[/cyan]",
        )
    )

    if not email:
        email = Prompt.ask("[cyan]Masukkan Email Google Anda[/cyan]")
    if not password:
        password = Prompt.ask("[cyan]Masukkan Kata Sandi Google[/cyan]", password=True)

    if not email or not password:
        console.print("[error]✗ Email dan sandi wajib diisi.[/error]")
        return False

    console.print("\n[info]Memulai peramban otomatisasi aman...[/info]")

    with sync_playwright() as p:
        try:
            # Gunakan Chrome sistem jika tersedia, atau Chromium bawaan
            launch_kwargs = {
                "headless": headless,
                "args": [
                    "--disable-blink-features=AutomationControlled",
                    "--no-first-run",
                    "--no-default-browser-check",
                ],
            }
            # Cek Chrome sistem
            chrome_path = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
            if chrome_path.exists():
                launch_kwargs["channel"] = "chrome"

            browser = p.chromium.launch(**launch_kwargs)
            context = browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
            )
            page = context.new_page()

            console.print("[info]Membuka portal Google Sign-In...[/info]")
            page.goto(
                "https://accounts.google.com/signin/v2/identifier?continue=https://flow.google.com/",
                wait_until="domcontentloaded",
            )
            # Cek jika layar menampilkan pilihan akun yang sudah ada sebelumnya
            if not page.query_selector("#identifierId"):
                use_another = page.query_selector("div:has-text('Use another account'), div:has-text('Gunakan akun lain')")
                if use_another and use_another.is_visible():
                    use_another.click()
                    time.sleep(2)

            page.wait_for_selector("#identifierId", timeout=20000)

            # 1. Ketik email dengan jeda manusiawi
            console.print(f"[info]Mengisi email:[/info] [cyan]{email}[/cyan]")
            for ch in email:
                page.type("#identifierId", ch, delay=random.randint(30, 80))
            time.sleep(0.5)

            console.print("[info]Mengirim formulir email...[/info]")
            page.press("#identifierId", "Enter")
            time.sleep(1)
            next_btn = page.query_selector("#identifierNext button, #identifierNext, button[jsname='LgbsSe']")
            if next_btn and next_btn.is_visible():
                try:
                    next_btn.click()
                except Exception:
                    pass
            time.sleep(4)

            # Evaluasi respons email
            if "signin/rejected" in page.url:
                console.print(
                    "[error]✗ Google menolak akses (signin/rejected). Lingkungan belum memenuhi kriteria attestation.[/error]"
                )
                browser.close()
                return False

            body_text = page.inner_text("body")
            if (
                "Couldn’t find your Google Account" in body_text
                or "Tidak dapat menemukan Akun Google" in body_text
            ):
                console.print(f"[error]✗ Akun Google '{email}' tidak ditemukan.[/error]")
                browser.close()
                return False

            if "Account deleted" in body_text or "Akun dihapus" in body_text:
                console.print(f"[error]✗ Akun Google '{email}' telah dinonaktifkan/dihapus.[/error]")
                browser.close()
                return False

            # 2. Tunggu field kata sandi
            console.print("[info]Menunggu formulir kata sandi...[/info]")
            pwd_sel = 'input[type="password"]:not([name="hiddenPassword"]), input[name="Passwd"]'
            page.wait_for_selector(pwd_sel, timeout=20000)

            console.print("[info]Mengisi kata sandi secara aman...[/info]")
            for ch in password:
                page.type(pwd_sel, ch, delay=random.randint(30, 80))
            time.sleep(0.5)

            console.print("[info]Mengirim kata sandi...[/info]")
            # Tombol submit password
            page.press(pwd_sel, "Enter")
            time.sleep(1)
            pwd_next = page.query_selector("#passwordNext button, #passwordNext, button[jsname='LgbsSe']")
            if pwd_next and pwd_next.is_visible():
                try:
                    pwd_next.click()
                except Exception:
                    pass
            time.sleep(5)

            # Evaluasi respons kata sandi
            body_post_pwd = page.inner_text("body")
            if "Wrong password" in body_post_pwd or "Sandi salah" in body_post_pwd:
                console.print("[error]✗ Kata sandi yang Anda masukkan salah.[/error]")
                browser.close()
                return False

            # 3. Penanganan Verifikasi 2FA / Device Challenge
            notified_2fa = False
            start_wait_auth = time.time()
            max_timeout = 120.0  # Beri waktu 2 menit bagi pengguna untuk merespons ponsel

            with console.status(
                "[bold cyan]Menunggu konfirmasi autentikasi Google Flow...[/bold cyan]",
                spinner="dots",
            ):
                while time.time() - start_wait_auth < max_timeout:
                    try:
                        curr_url = page.url
                        parsed = urlparse(curr_url)

                        # 1. Cek jika terjadi penolakan oleh Google
                        if "signin/rejected" in curr_url:
                            console.print(
                                "\n[error]✗ Google menolak akses (signin/rejected). Lingkungan tidak lolos verifikasi.[/error]"
                            )
                            browser.close()
                            return False

                        # 2. Redirect jika mendarat di myaccount.google.com
                        if "myaccount.google.com" in curr_url:
                            try:
                                page.goto(FLOW_HOME_URL, wait_until="commit")
                            except Exception:
                                pass
                            time.sleep(2)
                            continue

                        # 3. Cek jika berhasil masuk ke kanvas Google Flow (host flow.google.com bukan sekadar query continue)
                        is_flow_canvas = (
                            parsed.netloc == "flow.google.com"
                            or parsed.netloc.endswith(".flow.google.com")
                        ) and not parsed.path.startswith("/about")

                        if is_flow_canvas:
                            console.print("\n[success]✓ BERHASIL TERAUTENTIKASI DI GOOGLE FLOW![/success]")
                            time.sleep(3)
                            cookies = context.cookies()
                            saved_count = save_playwright_cookies_to_firefox(cookies, profile_dir)
                            console.print(
                                f"[success]✓ {saved_count} token cookie berhasil disimpan ke [cyan]browser_profile/cookies.sqlite[/cyan]![/success]"
                            )
                            browser.close()

                            # Jalankan verifikasi headless mandiri menggunakan engine Firefox Portable
                            console.print("[info]Memverifikasi kompatibilitas profil pada Firefox Portable...[/info]")
                            ver = verify_session_headless()
                            _print_verify_result(ver)
                            return True

                        # 4. Lewati dialog opsional Google seperti 'Not now' / 'Protect your account'
                        skip_btn = page.query_selector(
                            "button:has-text('Not now'), button:has-text('Jangan sekarang'), button:has-text('Skip'), button:has-text('Lewati')"
                        )
                        if skip_btn and skip_btn.is_visible():
                            try:
                                skip_btn.click()
                                time.sleep(2)
                            except Exception:
                                pass

                        # 5. Cek apakah layar meminta 2FA / verifikasi
                        page_text = page.inner_text("body")

                        # Cek prompt input kode PIN (SMS / Authenticator)
                        pin_input = page.query_selector(
                            "input#idvPin, input[name='Pin'], input[type='tel'], input#totpPin"
                        )
                        if pin_input and pin_input.is_visible():
                            console.print(
                                "\n[gold]📱 Google meminta 6-digit kode verifikasi (SMS / Google Authenticator):[/gold]"
                            )
                            code = Prompt.ask("[cyan]Masukkan Kode Verifikasi[/cyan]")
                            pin_input.fill(code.strip())
                            pin_next = page.query_selector(
                                "#idvPreregisteredPhoneNext, #totpNext, button[jsname='LgbsSe']"
                            )
                            if pin_next:
                                pin_next.click()
                            else:
                                page.keyboard.press("Enter")
                            time.sleep(4)
                            continue

                        # Cek prompt input email pemulihan
                        rec_input = page.query_selector(
                            "input#knowledge-preregistered-email-response, input[name='knowledgePreregisteredEmailResponse']"
                        )
                        if rec_input and rec_input.is_visible():
                            console.print("\n[gold]📧 Google meminta konfirmasi email pemulihan:[/gold]")
                            rec_val = Prompt.ask("[cyan]Masukkan Email Pemulihan[/cyan]")
                            rec_input.fill(rec_val.strip())
                            rec_input.press("Enter")
                            time.sleep(3)
                            continue

                        # Cek prompt notifikasi perangkat (Tap Yes / Match Number)
                        is_2fa_screen = any(
                            kw in page_text.lower()
                            for kw in [
                                "check your",
                                "periksa ponsel",
                                "periksa tablet",
                                "ketuk ya",
                                "tap yes",
                                "2-step",
                                "2 langkah",
                                "verifikasi 2 langkah",
                                "verifikasi perangkat",
                                "google sent a notification",
                                "google mengirim notifikasi",
                                "mengirimkan notifikasi",
                                "pilih angka",
                                "select the number",
                                "verify it's you",
                                "verifikasi bahwa ini memang anda",
                            ]
                        )

                        if is_2fa_screen and not notified_2fa:
                            notified_2fa = True
                            # Ekstrak nomor pencocokan jika ada (misal Google menampilkan angka '42')
                            match_num = None
                            for sel in [
                                ".f9UGee",
                                "div[data-number]",
                                "div[data-challengeinfo] div",
                                "span[data-number]",
                                "span[jsname='V67aGc']",
                                "div.BqLWCe",
                            ]:
                                try:
                                    for el_num in page.query_selector_all(sel):
                                        txt = el_num.inner_text().strip()
                                        if txt.isdigit() and 1 <= len(txt) <= 3:
                                            match_num = txt
                                            break
                                except Exception:
                                    pass
                                if match_num:
                                    break

                            if not match_num:
                                # Cari angka 2 digit yang berdiri sendiri di teks instruksi
                                m = re.search(
                                    r"(?:ketuk|tap|pilih|choose|select|angka|nomor)\s*[:\s]*(\d{1,3})\b",
                                    page_text,
                                    re.IGNORECASE,
                                )
                                if m:
                                    match_num = m.group(1)

                            panel_msg = (
                                "[bold yellow]📱 KONFIRMASI VERIFIKASI 2-LANGKAH (2FA) GOOGLE[/bold yellow]\n\n"
                                "Google mengirimkan permintaan verifikasi ke ponsel/perangkat Anda.\n"
                            )
                            if match_num:
                                panel_msg += (
                                    f"[white]Silakan buka ponsel Anda, ketuk [bold green]Ya[/bold green], "
                                    f"dan pilih angka:[/white] [bold gold underline] {match_num} [/bold gold underline]\n"
                                )
                            else:
                                panel_msg += "[white]Silakan buka ponsel Anda dan ketuk [bold green]Ya, itu saya[/bold green].[/white]\n"

                            panel_msg += "\n[muted]Terminal memantau persetujuan secara otomatis...[/muted]"
                            console.print(Panel(panel_msg, box=box.ROUNDED, title="[yellow]Aksi Pengguna Diperlukan[/yellow]"))

                    except Exception as loop_err:
                        # Tangani transisi navigasi (execution context destroyed saat user konfirmasi di ponsel)
                        time.sleep(1.5)
                        continue

                    time.sleep(2.0)

            console.print("[error]✗ Waktu tunggu autentikasi habis (melebihi 2 menit).[/error]")
            browser.close()
            return False

        except Exception as err:
            console.print(f"[error]✗ Terjadi kesalahan pada alur otomatisasi:[/error] {err}")
            return False


def check_google_session_cookies(profile_dir: Path = DEFAULT_TARGET_PROFILE) -> dict:
    """Memeriksa keberadaan cookie autentikasi Google dalam cookies.sqlite profil lokal."""
    db_path = profile_dir / "cookies.sqlite"
    if not db_path.exists():
        return {"logged_in": False, "count": 0, "auth_cookies": []}

    try:
        conn = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)
        cur = conn.cursor()
        cur.execute(
            """
            SELECT name, host FROM moz_cookies 
            WHERE (host LIKE '%google%' OR host LIKE '%flow%')
              AND name IN ('SID', 'SSID', 'HSID', '__Secure-1PSID', '__Secure-3PSID', 'OSID')
            """
        )
        rows = cur.fetchall()
        conn.close()

        auth_names = set(r[0] for r in rows)
        is_auth = ("SID" in auth_names or "__Secure-1PSID" in auth_names) and len(rows) >= 2
        return {
            "logged_in": is_auth,
            "count": len(rows),
            "auth_cookies": sorted(list(auth_names)),
        }
    except Exception:
        return {"logged_in": False, "count": 0, "auth_cookies": []}


def launch_isolated_login(
    firefox_bin: Path = DEFAULT_TARGET_BIN,
    profile_dir: Path = DEFAULT_TARGET_PROFILE,
    target_url: str = FLOW_HOME_URL,
) -> bool:
    """Meluncurkan Firefox Portable lokal dalam mode interaktif manual (fallback)."""
    if not firefox_bin.exists():
        console.print(f"[error]✗ Biner Firefox Portable lokal tidak ditemukan di:[/error] {firefox_bin}")
        return False

    profile_dir.mkdir(parents=True, exist_ok=True)
    lock = profile_dir / "parent.lock"
    if lock.exists():
        try:
            lock.unlink(missing_ok=True)
        except Exception:
            pass

    cmd = [
        str(firefox_bin),
        "-no-remote",
        "-profile",
        str(profile_dir),
        target_url,
    ]

    console.print("[info]Memulai Firefox Portable lokal (Jendela Manual)...[/info]")
    try:
        proc = subprocess.Popen(cmd)
    except Exception as err:
        console.print(f"[error]✗ Gagal meluncurkan peramban:[/error] {err}")
        return False

    console.print(f"[muted]Firefox Portable aktif dengan PID: {proc.pid}[/muted]")
    console.print("[info]Silakan selesaikan login di jendela yang terbuka, lalu tutup jendela jika sudah selesai...[/info]\n")

    detected_auth = False
    with console.status("[bold cyan]Memantau basis data sesi Google Flow...[/bold cyan]", spinner="dots"):
        while proc.poll() is None:
            time.sleep(2.0)
            status = check_google_session_cookies(profile_dir)
            if status["logged_in"] and not detected_auth:
                detected_auth = True
                console.print(
                    f"\n[success]✓ Token sesi Google terdeteksi di cookies.sqlite![/success] "
                    f"([cyan]{', '.join(status['auth_cookies'])}[/cyan])"
                )

    console.print("[info]Jendela Firefox Portable telah ditutup.[/info]")
    ver = verify_session_headless(firefox_bin, profile_dir)
    _print_verify_result(ver)
    return ver["success"]


def discover_potential_profiles() -> list[dict]:
    """Memindai sistem untuk menemukan profil Firefox yang memiliki cookie Google Flow aktif."""
    candidates = []

    fp_profiles = Path(r"D:\FirefoxPortable\Data\profiles")
    if fp_profiles.exists() and fp_profiles.is_dir():
        for p in fp_profiles.iterdir():
            if p.is_dir() and (p / "cookies.sqlite").exists():
                candidates.append({"name": f"FirefoxPortable/{p.name}", "path": p})

    appdata = os.environ.get("APPDATA")
    if appdata:
        sys_ff = Path(appdata) / "Mozilla" / "Firefox" / "Profiles"
        if sys_ff.exists() and sys_ff.is_dir():
            for p in sys_ff.iterdir():
                if p.is_dir() and (p / "cookies.sqlite").exists():
                    candidates.append({"name": f"SystemFirefox/{p.name}", "path": p})

    valid_profiles = []
    for c in candidates:
        db_path = c["path"] / "cookies.sqlite"
        try:
            conn = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)
            cur = conn.cursor()
            cur.execute(
                "SELECT count(*) FROM moz_cookies WHERE host LIKE ? OR host LIKE ?",
                ("%google%", "%flow%"),
            )
            count = cur.fetchone()[0]
            cur.execute(
                "SELECT count(*) FROM moz_cookies WHERE host LIKE ?",
                ("%flow.google.com%",),
            )
            flow_count = cur.fetchone()[0]
            conn.close()

            c["google_cookies"] = count
            c["flow_cookies"] = flow_count
            valid_profiles.append(c)
        except Exception:
            continue

    valid_profiles.sort(key=lambda x: (x["flow_cookies"], x["google_cookies"]), reverse=True)
    return valid_profiles


def sync_profile_session(src_profile: Path, dst_profile: Path = DEFAULT_TARGET_PROFILE) -> dict:
    """Menyinkronkan cookie dan web storage autentikasi Google ke profil target."""
    dst_profile.mkdir(parents=True, exist_ok=True)
    src_db = src_profile / "cookies.sqlite"
    dst_db = dst_profile / "cookies.sqlite"

    if not src_db.exists():
        raise FileNotFoundError(f"Basis data cookies tidak ditemukan pada sumber: {src_db}")

    src_conn = sqlite3.connect(f"file:{src_db.as_posix()}?mode=ro", uri=True)
    src_conn.row_factory = sqlite3.Row

    dst_conn = sqlite3.connect(dst_db)
    if not dst_conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='moz_cookies'"
    ).fetchone():
        schema = src_conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='moz_cookies'"
        ).fetchone()[0]
        dst_conn.execute(schema)
        dst_conn.commit()

    dst_cols = [c[1] for c in dst_conn.execute("PRAGMA table_info(moz_cookies)").fetchall()]
    src_cols = [c[1] for c in src_conn.execute("PRAGMA table_info(moz_cookies)").fetchall()]
    common_cols = [c for c in dst_cols if c in src_cols and c.lower() != "id"]

    cols_str = ", ".join(common_cols)
    placeholders = ", ".join(["?"] * len(common_cols))

    query = f"""
    SELECT {cols_str} FROM moz_cookies 
    WHERE host LIKE '%google%' 
       OR host LIKE '%flow%' 
       OR host LIKE '%labs%'
       OR host LIKE '%youtube%'
       OR host LIKE '%gstatic%'
    """
    rows = src_conn.execute(query).fetchall()

    inserted_count = 0
    for r in rows:
        vals = [r[c] for c in common_cols]
        dst_conn.execute(
            f"INSERT OR REPLACE INTO moz_cookies ({cols_str}) VALUES ({placeholders})",
            vals,
        )
        inserted_count += 1

    dst_conn.commit()
    src_conn.close()
    dst_conn.close()

    storage_synced = []
    src_storage = src_profile / "storage" / "default"
    dst_storage = dst_profile / "storage" / "default"
    if src_storage.exists():
        dst_storage.mkdir(parents=True, exist_ok=True)
        for pattern in ["*flow.google.com*", "*accounts.google.com*"]:
            for item in src_storage.glob(pattern):
                target_dest = dst_storage / item.name
                if item.is_dir():
                    shutil.copytree(item, target_dest, dirs_exist_ok=True)
                    storage_synced.append(item.name)
                elif item.is_file():
                    shutil.copy2(item, target_dest)
                    storage_synced.append(item.name)

    user_js = dst_profile / "user.js"
    base_prefs = """// KONFIGURASI OTOMASI MARIONETTE & STEALTH
user_pref("marionette.enabled", true);
user_pref("marionette.port", 2828);
user_pref("dom.webdriver.enabled", false);
user_pref("toolkit.telemetry.enabled", false);
user_pref("toolkit.telemetry.reportingpolicy.firstRun", false);
user_pref("browser.sessionstore.resume_from_crash", false);
user_pref("media.peerconnection.enabled", true);
user_pref("media.peerconnection.ice.no_host", true);
user_pref("media.peerconnection.ice.default_address_only", true);
"""
    if not user_js.exists():
        user_js.write_text(base_prefs, encoding="utf-8")

    return {
        "cookies_synced": inserted_count,
        "storage_synced": storage_synced,
        "source": str(src_profile),
    }


def ingest_cookie_string(cookie_raw: str, dst_profile: Path = DEFAULT_TARGET_PROFILE) -> int:
    """Menyuntikkan string cookie (format Header atau Name=Value) ke dalam cookies.sqlite."""
    dst_profile.mkdir(parents=True, exist_ok=True)
    dst_db = dst_profile / "cookies.sqlite"
    if not dst_db.exists():
        raise FileNotFoundError(f"Basis data cookies target belum terinisialisasi: {dst_db}")

    raw = re.sub(r"^cookie:\s*", "", cookie_raw.strip(), flags=re.IGNORECASE)
    pairs = [p.strip() for p in raw.split(";") if "=" in p]

    conn = sqlite3.connect(dst_db)
    dst_cols = [c[1] for c in conn.execute("PRAGMA table_info(moz_cookies)").fetchall()]
    has_same_site = "sameSite" in dst_cols
    has_scheme_map = "schemeMap" in dst_cols
    has_update_time = "updateTime" in dst_cols

    now = int(time.time())
    expiry_ms = (now + (365 * 24 * 3600)) * 1000
    now_us = now * 1000000

    inserted = 0
    for pair in pairs:
        name, val = pair.split("=", 1)
        name = name.strip()
        val = val.strip()
        if not name:
            continue

        host = ".google.com"
        if "osid" in name.lower():
            host = "flow.google.com"

        if name.startswith("__Secure-3P") or name in ("__Secure-OSID", "__Host-3PLSID"):
            ss_val = 0
        else:
            ss_val = 256

        insert_cols = [
            "originAttributes",
            "name",
            "value",
            "host",
            "path",
            "expiry",
            "lastAccessed",
            "creationTime",
            "isSecure",
            "isHttpOnly",
            "inBrowserElement",
        ]
        insert_vals = ["", name, val, host, "/", expiry_ms, now_us, now_us, 1, 1, 0]

        if has_same_site:
            insert_cols.append("sameSite")
            insert_vals.append(ss_val)
        if has_scheme_map:
            insert_cols.append("schemeMap")
            insert_vals.append(2)
        if has_update_time:
            insert_cols.append("updateTime")
            insert_vals.append(now_us)

        cols_part = ", ".join(insert_cols)
        placeholders = ", ".join(["?"] * len(insert_vals))
        sql = f"INSERT OR REPLACE INTO moz_cookies ({cols_part}) VALUES ({placeholders})"
        conn.execute(sql, tuple(insert_vals))
        inserted += 1

    conn.commit()
    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    conn.close()
    return inserted


def verify_session_headless(
    firefox_bin: Path = DEFAULT_TARGET_BIN,
    profile_dir: Path = DEFAULT_TARGET_PROFILE,
    timeout: float = 25.0,
) -> dict:
    """Meluncurkan Firefox Portable headless untuk memverifikasi kanvas Google Flow secara senyap."""
    from image_generator import MarionetteDriver

    if not firefox_bin.exists():
        return {"success": False, "message": f"Biner Firefox tidak ditemukan di: {firefox_bin}"}

    cookies_db = profile_dir / "cookies.sqlite"
    has_google_cookie = False
    if cookies_db.exists():
        try:
            conn = sqlite3.connect(str(cookies_db))
            cur = conn.cursor()
            cur.execute("SELECT count(*) FROM moz_cookies WHERE host LIKE '%google.com%'")
            row = cur.fetchone()
            count = row[0] if row else 0
            conn.close()
            if count > 0:
                has_google_cookie = True
        except Exception:
            pass

    if not has_google_cookie:
        return {
            "success": False,
            "status": "fresh_install",
            "url": "https://flow.google.com/about",
            "message": "Profil peramban baru terpasang (kondisi bersih). Akun Google belum terhubung.",
        }

    lock = profile_dir / "parent.lock"
    if lock.exists():
        try:
            lock.unlink(missing_ok=True)
        except Exception:
            pass

    cmd = [
        str(firefox_bin),
        "-no-remote",
        "-headless",
        "-marionette",
        "-profile",
        str(profile_dir),
    ]

    env = os.environ.copy()
    env["MOZ_CRASHREPORTER_DISABLE"] = "1"
    env["MOZ_CRASHREPORTER_NO_REPORT"] = "1"

    proc = subprocess.Popen(cmd, env=env)
    driver = MarionetteDriver()

    try:
        opened = False
        start_wait = time.time()
        while time.time() - start_wait < 10.0:
            if driver.is_port_open(timeout=0.5):
                opened = True
                break
            time.sleep(0.3)

        if not opened:
            return {"success": False, "message": "Gagal terhubung ke port otomasi Marionette (2828)."}

        driver.connect(timeout=15.0)
        driver.navigate(FLOW_HOME_URL)

        start_poll = time.time()
        last_url = ""
        while time.time() - start_poll < timeout:
            time.sleep(1.5)
            check_script = """
            const url = window.location.href.toLowerCase();
            const hasDashboard = !!document.querySelector('aisandbox-root, flow-project-shell, flow-prompt-box, .project-card, [data-test-id="project-card"]');
            const isAuth = url.includes('accounts.google.com') || url.includes('/about');
            return {
                url: window.location.href,
                title: document.title,
                hasDashboard: hasDashboard,
                isAuth: isAuth,
                loggedIn: hasDashboard && !url.includes('/about')
            };
            """
            try:
                state = driver.execute_script(check_script)
                if isinstance(state, dict):
                    last_url = state.get("url", "")
                    if state.get("loggedIn"):
                        return {
                            "success": True,
                            "url": last_url,
                            "title": state.get("title", ""),
                            "message": "Berhasil terotentikasi di Google Flow!",
                        }
                    if "/about" in last_url.lower():
                        return {
                            "success": False,
                            "status": "not_logged_in",
                            "url": last_url,
                            "title": state.get("title", ""),
                            "message": "Akun Google belum masuk (halaman informasi publik flow.google.com/about).",
                        }
                    if state.get("isAuth") and "accounts.google.com" in last_url:
                        return {
                            "success": False,
                            "status": "not_logged_in",
                            "url": last_url,
                            "title": state.get("title", ""),
                            "message": "Sesi belum aktif (berada di halaman login accounts.google.com).",
                        }
            except Exception:
                pass

        return {
            "success": False,
            "status": "timeout",
            "url": last_url,
            "message": "Waktu tunggu habis saat memuat kanvas Google Flow.",
        }

    finally:
        driver.close()
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass


def main() -> int:
    """Titik masuk CLI autentikasi mandiri."""
    parser = argparse.ArgumentParser(
        description="Google Flow CLI Session & Authentication Manager (100% Automated)."
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Otomatisasi login penuh: Cukup masukkan email & sandi di terminal (Anti-Blokir)",
    )
    parser.add_argument(
        "--email",
        type=str,
        help="Email akun Google untuk login otomatis",
    )
    parser.add_argument(
        "--password",
        type=str,
        help="Kata sandi akun Google untuk login otomatis",
    )
    parser.add_argument(
        "--login",
        "--interactive",
        action="store_true",
        help="Buka jendela Firefox Portable lokal terisolasi untuk login manual (Fallback)",
    )
    parser.add_argument(
        "--paste",
        action="store_true",
        help="Buka prompt terminal untuk menempelkan string cookie sesi secara manual",
    )
    parser.add_argument(
        "--cookie",
        type=str,
        help="String cookie Google Flow langsung untuk disuntikkan ke cookies.sqlite",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Uji keabsahan sesi Google Flow secara headless tanpa jendela GUI",
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Sinkronkan sesi dari profil peramban eksternal yang terdeteksi (opsional)",
    )
    parser.add_argument(
        "--from-profile",
        type=str,
        help="Path absolut direktori profil Firefox sumber yang ingin disinkronkan",
    )
    parser.add_argument(
        "--head",
        "--gui",
        action="store_true",
        help="Buka antarmuka jendela peramban visual saat otomatisasi (bukan headless)",
    )

    args = parser.parse_args()

    console.print(
        Panel.fit(
            "[bold cyan]GOOGLE FLOW AUTHENTICATION & AUTOMATION MANAGER[/bold cyan]\n"
            "[muted]Otomasi Login Penuh Jalur Terminal — 100% Terisolasi Total di Direktori Proyek[/muted]",
            box=box.ROUNDED,
        )
    )

    # 1. Mode Otomasi Penuh (--auto / bila --email diberikan)
    if args.auto or args.email:
        success = automated_google_login(
            email=args.email,
            password=args.password,
            headless=not args.head,
        )
        return 0 if success else 1

    # 2. Mode Login Manual Jendela (--login)
    if args.login:
        success = launch_isolated_login()
        return 0 if success else 1

    # 3. Mode Injeksi Cookie String (--cookie)
    if args.cookie:
        count = ingest_cookie_string(args.cookie)
        console.print(f"[success]✓ Berhasil menyuntikkan {count} pasangan cookie ke profil lokal![/success]")
        console.print("[info]ℹ Menjalankan verifikasi headless otomatis...[/info]")
        res = verify_session_headless()
        _print_verify_result(res)
        return 0 if res["success"] else 1

    # 4. Mode Tempel Cookie Manual (--paste)
    if args.paste:
        console.print("[info]Silakan tempelkan (paste) string cookie Anda di bawah ini:[/info]")
        raw = Prompt.ask("[cyan]Cookie[/cyan]")
        if raw.strip():
            count = ingest_cookie_string(raw)
            console.print(f"[success]✓ Berhasil menyuntikkan {count} pasangan cookie ke profil lokal![/success]")
            res = verify_session_headless()
            _print_verify_result(res)
            return 0 if res["success"] else 1
        else:
            console.print("[warning]Input cookie kosong.[/warning]")
            return 1

    # 5. Mode Verifikasi Murni (--verify)
    if args.verify:
        console.print("[info]ℹ Menguji status sesi Google Flow di latar belakang (mode headless)...[/info]")
        res = verify_session_headless()
        _print_verify_result(res)
        return 0 if res["success"] else 1

    # 6. Mode Sinkronisasi Profil Spesifik (--from-profile)
    if args.from_profile:
        src = Path(args.from_profile)
        if not src.exists():
            console.print(f"[error]✗ Direktori profil sumber tidak ditemukan: {src}[/error]")
            return 1
        console.print(f"[info]ℹ Menyinkronkan sesi dari:[/info] [cyan]{src}[/cyan]")
        res_sync = sync_profile_session(src)
        console.print(
            f"[success]✓ Selesai: {res_sync['cookies_synced']} cookies disinkronkan, {len(res_sync['storage_synced'])} storage folder disalin.[/success]"
        )
        res = verify_session_headless()
        _print_verify_result(res)
        return 0 if res["success"] else 1

    # 7. Mode Sinkronisasi Profil Eksternal (--sync)
    if args.sync:
        console.print("[info]ℹ Memindai profil peramban eksternal yang memiliki sesi Google Flow...[/info]")
        profiles = discover_potential_profiles()
        if not profiles:
            console.print("[warning]⚠ Tidak ditemukan profil peramban dengan sesi Google aktif.[/warning]")
            return 1
        best_profile = profiles[0]
        console.print(f"[info]ℹ Menyinkronkan dari profil: [cyan]{best_profile['name']}[/cyan][/info]")
        res_sync = sync_profile_session(best_profile["path"])
        console.print(f"[success]✓ Selesai menyinkronkan {res_sync['cookies_synced']} cookies.[/success]")
        res_ver = verify_session_headless()
        _print_verify_result(res_ver)
        return 0 if res_ver["success"] else 1

    # 8. Menu Interaktif Jika Dipanggil Tanpa Argumen
    console.print("[bold]Pilih Metode Otentikasi Sesi:[/bold]\n")
    console.print(" [bold green][1][/bold green] [white]Otomasi Login Penuh[/white] [dim](Cukup Masukkan Email & Sandi di Terminal)[/dim]")
    console.print(" [bold cyan][2][/bold cyan] [white]Tempelkan (Paste) Cookie Sesi via Terminal[/white]")
    console.print(" [bold magenta][3][/bold magenta] [white]Uji Verifikasi Sesi di Latar Belakang (Headless)[/white]")
    console.print(" [bold yellow][4][/bold yellow] [white]Buka Jendela Peramban Manual[/white] [dim](Fallback)[/dim]")
    console.print(" [bold blue][5][/bold blue] [white]Sinkronkan Sesi dari Profil Eksternal[/white] [dim](Opsional)[/dim]")
    console.print(" [dim][0] Keluar[/dim]\n")

    choice = Prompt.ask("[cyan]Pilihan Anda[/cyan]", choices=["1", "2", "3", "4", "5", "0"], default="1")

    if choice == "1":
        success = automated_google_login()
        return 0 if success else 1
    elif choice == "2":
        console.print("\n[info]Silakan tempelkan (paste) string cookie Anda di bawah ini:[/info]")
        raw = Prompt.ask("[cyan]Cookie[/cyan]")
        if raw.strip():
            count = ingest_cookie_string(raw)
            console.print(f"[success]✓ Berhasil menyuntikkan {count} pasangan cookie ke profil lokal![/success]")
            res = verify_session_headless()
            _print_verify_result(res)
            return 0 if res["success"] else 1
        return 1
    elif choice == "3":
        res = verify_session_headless()
        _print_verify_result(res)
        return 0 if res["success"] else 1
    elif choice == "4":
        success = launch_isolated_login()
        return 0 if success else 1
    elif choice == "5":
        profiles = discover_potential_profiles()
        if not profiles:
            console.print("[warning]⚠ Tidak ditemukan profil peramban dengan sesi Google aktif.[/warning]")
            return 1
        best_profile = profiles[0]
        console.print(f"[info]ℹ Menyinkronkan dari profil: [cyan]{best_profile['name']}[/cyan][/info]")
        res_sync = sync_profile_session(best_profile["path"])
        console.print(f"[success]✓ Selesai menyinkronkan {res_sync['cookies_synced']} cookies.[/success]")
        res_ver = verify_session_headless()
        _print_verify_result(res_ver)
        return 0 if res_ver["success"] else 1
    else:
        console.print("[dim]Keluar.[/dim]")
        return 0


def _print_verify_result(res: dict) -> None:
    """Mencetak panel hasil verifikasi sesi ke terminal."""
    if res["success"]:
        console.print(
            Panel(
                f"[bold green]✓ SESI GOOGLE FLOW AKTIF & TERVERIFIKASI![/bold green]\n\n"
                f"URL Kanvas : [cyan]{res.get('url', '-')}[/cyan]\n"
                f"Judul Tab  : [white]{res.get('title', '-')}[/white]\n\n"
                "[muted]Generator siap digunakan secara senyap (headless) di latar belakang.[/muted]",
                box=box.ROUNDED,
                title="[green]Status Autentikasi Headless[/green]",
            )
        )
    elif res.get("status") in ("fresh_install", "not_logged_in") or "/about" in res.get("url", "").lower():
        console.print(
            Panel(
                f"[bold yellow]ℹ AKUN GOOGLE BELUM TERHUBUNG KE PERAMBAN LOKAL[/bold yellow]\n\n"
                f"Kondisi : [white]{res.get('message', 'Peramban dalam status bersih. Sesi Google belum terpasang.')}[/white]\n"
                f"URL     : [cyan]{res.get('url', '-')}[/cyan]\n\n"
                "[bold green]Langkah Berikutnya:[/bold green] Silakan masukkan email & sandi di terminal untuk menghubungkan akun Google Anda.",
                box=box.ROUNDED,
                title="[yellow]Status Akun Google Flow[/yellow]",
            )
        )
    else:
        console.print(
            Panel(
                f"[bold red]✗ KENDALA VERIFIKASI PERAMBAN[/bold red]\n\n"
                f"Pesan   : [yellow]{res.get('message', '-')}[/yellow]\n"
                f"URL     : [dim]{res.get('url', '-')}[/dim]\n\n"
                "[muted]Silakan jalankan opsi [1] Otomasi Login Penuh untuk menghubungkan sesi Google Flow Anda.[/muted]",
                box=box.ROUNDED,
                title="[red]Status Autentikasi[/red]",
            )
        )


if __name__ == "__main__":
    sys.exit(main())
