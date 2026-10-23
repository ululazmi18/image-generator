"""Test Step-by-Step Google Flow Automation dengan Screenshot Setiap Langkah.

Menjalankan otomasi secara bertahap dan mengambil tangkapan layar (screenshot)
pada SETIAP langkah agar pengguna dapat memeriksa dan memverifikasi perilaku
peramban, letak kursor, teks prompt, menu opsi, dan hasil unduhan.

Penggunaan:
    python test_step_by_step.py
    python test_step_by_step.py --prompt gambar pemandangan gunung es
    python test_step_by_step.py --auto
"""

import base64
import datetime
import os
import re
import shutil
import sys
import time
from pathlib import Path

# Standar encoding UTF-8 untuk terminal Windows
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

from PIL import ImageGrab
import win32api
import win32gui

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.theme import Theme

from image_generator import (
    CUSTOM_THEME,
    ImageGenerator,
    NativeOSController,
    parse_cli_args,
    XPATH_PROMPT_INPUT,
    XPATH_GENERATE_BUTTON,
    XPATH_TILE_CONTAINER,
    XPATH_HOTBAR_ICON,
    XPATH_CONTEXT_MENU_ITEM_5,
    XPATH_SUBMENU_DOWNLOAD_ITEM_2,
)

console = Console(theme=CUSTOM_THEME)


class StepByStepTester:
    """Penguji otomasi bertahap lengkap dengan perekaman tangkapan layar (screenshot)."""

    def __init__(self, output_dir: Path | None = None, auto_mode: bool = False):
        self.workspace_dir = Path(__file__).resolve().parent
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_dir = (output_dir or (self.workspace_dir / "screenshots")) / f"run_{timestamp}"
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.auto_mode = auto_mode
        self.screenshots: list[tuple[int, str, Path, str]] = []
        self.generator = ImageGenerator(workspace_dir=self.workspace_dir)

    def capture_screenshot(self, step_num: int, step_name: str, description: str) -> Path:
        """Mengambil tangkapan layar jendela Firefox dan halaman web."""
        NativeOSController.ensure_interactive_desktop()
        file_slug = re.sub(r"[^\w\s-]", "", step_name).strip().replace(" ", "_").lower()
        file_path = self.run_dir / f"step_{step_num:02d}_{file_slug}.png"

        hwnd = NativeOSController.find_firefox_hwnd()
        captured = False

        if hwnd and win32gui.IsWindow(hwnd):
            try:
                rect = win32gui.GetWindowRect(hwnd)
                # Bounding box: left, top, right, bottom
                if rect[2] > rect[0] and rect[3] > rect[1]:
                    im = ImageGrab.grab(bbox=rect)
                    im.save(file_path, "PNG")
                    captured = True
            except Exception:
                captured = False

        if not captured:
            # Fallback ke fullscreen desktop grab
            try:
                im = ImageGrab.grab()
                im.save(file_path, "PNG")
                captured = True
            except Exception:
                pass

        # Tambahkan ke rekaman ringkasan
        self.screenshots.append((step_num, step_name, file_path, description))
        console.print(f"  [accent]📸 Tangkapan Layar Disimpan:[/accent] [cyan]{file_path.name}[/cyan]")
        return file_path

    def step_pause(self, message: str) -> None:
        """Jeda sejenak untuk inspeksi manual jika tidak dalam mode --auto."""
        if self.auto_mode:
            time.sleep(1.2)
        else:
            Prompt.ask(f"[dim]{message} (Tekan Enter untuk lanjut)[/dim]")

    def run_test(self, prompt: str, timeout: int = 180) -> int:
        console.clear()
        banner = (
            "[brand]IMAGE GENERATOR — STEP-BY-STEP AUTOMATION AUDIT[/brand]\n"
            "[muted]Pemeriksaan Bertahap Setiap Langkah Dilengkapi Tangkapan Layar (Screenshot)[/muted]"
        )
        console.print(Panel(banner, box=box.ROUNDED, style="color(240)"))

        info_table = Table(box=box.ROUNDED, show_header=False, expand=True)
        info_table.add_column("Parameter", style="cyan", width=22)
        info_table.add_column("Nilai", style="bold white")
        info_table.add_row("Prompt Uji", f"[gold]{prompt}[/gold]")
        info_table.add_row("Folder Screenshot", f"[accent]{self.run_dir}[/accent]")
        info_table.add_row("Mode Uji", "[green]Auto Progression[/green]" if self.auto_mode else "[yellow]Manual Step-by-Step (Enter to proceed)[/yellow]")
        console.print(info_table)
        console.print()

        try:
            # ------------------------------------------------------------------
            # LANGKAH 1: Inisialisasi Peramban & Deteksi Tab Google Flow
            # ------------------------------------------------------------------
            console.print(Panel("[bold cyan]LANGKAH 1:[/bold cyan] Memverifikasi Peramban & Tab Google Flow", box=box.SIMPLE))
            self.generator.ensure_browser()
            self.generator.connect()
            existing_files = {str(f.resolve()) for f in list(self.generator.download_dir.glob("*.jpg")) + list(self.generator.download_dir.glob("*.jpeg"))}
            
            handle = self.generator.find_flow_tab()
            NativeOSController.activate_window()
            time.sleep(0.8)
            self.capture_screenshot(1, "tab_google_flow_terdeteksi", "Jendela Firefox aktif dan tab Google Flow ditemukan.")
            console.print("[success]✓ Langkah 1 Selesai: Tab Google Flow siap.[/success]\n")
            self.step_pause("Tab Google Flow terverifikasi.")

            # ------------------------------------------------------------------
            # LANGKAH 2: Cari Elemen Editor & Fokuskan Kursor Fisik
            # ------------------------------------------------------------------
            console.print(Panel("[bold cyan]LANGKAH 2:[/bold cyan] Mencari Area Editor Prompt & Mengunci Fokus Mouse", box=box.SIMPLE))
            locate_script = """
            const inputXpath = arguments[0];
            function getByXPath(p) {
                try { return document.evaluate(p, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue; } catch (e) { return null; }
            }
            let el = getByXPath(inputXpath) ||
                     document.querySelector('flow-rich-text-editor div[contenteditable="true"]') ||
                     document.querySelector('flow-rich-text-editor div div p') ||
                     document.querySelector('flow-rich-text-editor p') ||
                     document.querySelector('flow-prompt-box [contenteditable="true"]');
            if (!el) return { success: false };
            el.scrollIntoView({ block: 'center' });
            el.focus();
            const rect = el.getBoundingClientRect();
            return {
                success: true,
                x: Math.round(window.mozInnerScreenX + rect.left + rect.width / 2),
                y: Math.round(window.mozInnerScreenY + rect.top + rect.height / 2)
            };
            """
            res_loc = self.generator.driver.execute_script(locate_script, [XPATH_PROMPT_INPUT])
            if not isinstance(res_loc, dict) or not res_loc.get("success"):
                raise RuntimeError("Elemen editor prompt Google Flow tidak ditemukan.")

            screen_x = res_loc["x"]
            screen_y = res_loc["y"]
            NativeOSController.send_mouse_click(screen_x, screen_y)
            time.sleep(0.4)
            self.capture_screenshot(2, "editor_prompt_terfokus", f"Mouse fisik mengeklik koordinat input ({screen_x}, {screen_y}).")
            console.print("[success]✓ Langkah 2 Selesai: Fokus editor aktif.[/success]\n")
            self.step_pause("Fokus input prompt siap.")

            # ------------------------------------------------------------------
            # LANGKAH 3: Injeksi Teks Prompt via Windows Clipboard (Ctrl+V)
            # ------------------------------------------------------------------
            console.print(Panel("[bold cyan]LANGKAH 3:[/bold cyan] Mengirim Prompt via Windows Clipboard & Ctrl+V", box=box.SIMPLE))
            NativeOSController.set_clipboard_text(prompt)
            time.sleep(0.08)
            # Bersihkan dan paste
            NativeOSController.send_key_combination(win32con.VK_CONTROL, ord("A"))
            time.sleep(0.05)
            win32api.keybd_event(win32con.VK_BACK, 0, 0, 0)
            win32api.keybd_event(win32con.VK_BACK, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.05)
            NativeOSController.send_key_combination(win32con.VK_CONTROL, ord("V"))
            time.sleep(0.4)
            self.capture_screenshot(3, "prompt_berhasil_ditempel", "Teks prompt berhasil ditempel via hardware Ctrl+V.")
            console.print("[success]✓ Langkah 3 Selesai: Prompt berhasil ditempel.[/success]\n")
            self.step_pause("Prompt telah tertempel.")

            # ------------------------------------------------------------------
            # LANGKAH 4: Submit Prompt (Enter Fisik & Klik Generate)
            # ------------------------------------------------------------------
            console.print(Panel("[bold cyan]LANGKAH 4:[/bold cyan] Mengirim Perintah Submit (Enter & Tombol Generate)", box=box.SIMPLE))
            # Tekan Enter
            win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.3)

            # Cek koordinat tombol generate sebagai penjamin eksekusi
            btn_script = """
            const buttonXpath = arguments[0];
            function getByXPath(p) {
                try { return document.evaluate(p, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue; } catch (e) { return null; }
            }
            let btn = getByXPath(buttonXpath) ||
                      document.querySelector('flow-generate-icon-button button') ||
                      document.querySelector('flow-generate-icon-button') ||
                      document.querySelector('flow-base-prompt-box button.generate-button');
            if (!btn) return null;
            const rect = btn.getBoundingClientRect();
            return {
                x: Math.round(window.mozInnerScreenX + rect.left + rect.width / 2),
                y: Math.round(window.mozInnerScreenY + rect.top + rect.height / 2)
            };
            """
            btn_coord = self.generator.driver.execute_script(btn_script, [XPATH_GENERATE_BUTTON])
            if btn_coord and btn_coord.get("x") and btn_coord.get("y"):
                NativeOSController.send_mouse_click(btn_coord["x"], btn_coord["y"])

            time.sleep(1.0)
            self.capture_screenshot(4, "prompt_disubmit_proses_mulai", "Enter dan tombol generate telah dieksekusi.")
            console.print("[success]✓ Langkah 4 Selesai: Submit berhasil dikirim.[/success]\n")
            self.step_pause("Submit terkirim.")

            # ------------------------------------------------------------------
            # LANGKAH 5 & 6: Hover Tile 1 & Tunggu Render Selesai (Hotbar Button 3)
            # ------------------------------------------------------------------
            console.print(Panel("[bold cyan]LANGKAH 5 & 6:[/bold cyan] Hover Tile Gambar & Menunggu Render Selesai", box=box.SIMPLE))
            start_wait = time.time()
            render_ready = False
            last_ss_time = 0.0

            while time.time() - start_wait < timeout:
                check_script = """
                const tileXpath = arguments[0];
                const hotbarXpath = arguments[1];
                function getByXPath(p) {
                    try { return document.evaluate(p, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue; } catch (e) { return null; }
                }
                let tile = getByXPath(tileXpath) || document.querySelector('flow-grid-tile-container');
                let tileCoord = null;
                if (tile) {
                    const rect = tile.getBoundingClientRect();
                    tileCoord = {
                        x: Math.round(window.mozInnerScreenX + rect.left + rect.width / 2),
                        y: Math.round(window.mozInnerScreenY + rect.top + rect.height / 2)
                    };
                }
                let hotbar = getByXPath(hotbarXpath) ||
                             document.querySelector('flow-grid-tile-container flow-image-hotbar button:nth-child(3) mat-icon') ||
                             document.querySelector('flow-image-hotbar button:nth-child(3)');
                return { tileCoord: tileCoord, hotbarReady: !!hotbar };
                """
                res_check = self.generator.driver.execute_script(check_script, [XPATH_TILE_CONTAINER, XPATH_HOTBAR_ICON])
                if isinstance(res_check, dict):
                    if res_check.get("tileCoord"):
                        c = res_check["tileCoord"]
                        NativeOSController.send_mouse_move(c["x"], c["y"])

                    if res_check.get("hotbarReady"):
                        render_ready = True
                        break

                time.sleep(1.5)

            if not render_ready:
                self.capture_screenshot(5, "render_timeout_error", f"Waktu tunggu habis ({timeout} detik).")
                raise TimeoutError(f"Generasi gambar belum selesai dalam {timeout} detik.")

            time.sleep(0.5)
            self.capture_screenshot(6, "render_selesai_hotbar_muncul", "Render gambar selesai dan tombol opsi hotbar 3 terdeteksi.")
            console.print("[success]✓ Langkah 6 Selesai: Render selesai & Hotbar siap.[/success]\n")
            self.step_pause("Hotbar opsi terdeteksi.")

            # ------------------------------------------------------------------
            # LANGKAH 7: Klik Tombol Hotbar 3 (Buka Menu Konteks)
            # ------------------------------------------------------------------
            console.print(Panel("[bold cyan]LANGKAH 7:[/bold cyan] Mengeklik Tombol Hotbar 3 (Buka Menu Opsi)", box=box.SIMPLE))
            get_h_script = """
            const hotbarXpath = arguments[0];
            function getByXPath(p) {
                try { return document.evaluate(p, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue; } catch (e) { return null; }
            }
            let btn = getByXPath(hotbarXpath) ||
                      document.querySelector('flow-grid-tile-container flow-image-hotbar button:nth-child(3)') ||
                      document.querySelector('flow-image-hotbar button:nth-child(3)');
            if (!btn) return null;
            const rect = btn.getBoundingClientRect();
            return {
                x: Math.round(window.mozInnerScreenX + rect.left + rect.width / 2),
                y: Math.round(window.mozInnerScreenY + rect.top + rect.height / 2)
            };
            """
            h_coord = self.generator.driver.execute_script(get_h_script, [XPATH_HOTBAR_ICON])
            if not h_coord:
                raise RuntimeError("Koordinat tombol hotbar 3 tidak dapat dihitung.")

            NativeOSController.send_mouse_click(h_coord["x"], h_coord["y"])
            time.sleep(0.8)
            self.capture_screenshot(7, "menu_konteks_terbuka", "Tombol hotbar 3 diklik dan menu konteks terbuka.")
            console.print("[success]✓ Langkah 7 Selesai: Menu konteks terbuka.[/success]\n")
            self.step_pause("Menu konteks terbuka.")

            # ------------------------------------------------------------------
            # LANGKAH 8: Hover Menu Item 5 (Submenu Download)
            # ------------------------------------------------------------------
            console.print(Panel("[bold cyan]LANGKAH 8:[/bold cyan] Men-hover Menu Item 5 untuk Membuka Submenu", box=box.SIMPLE))
            get_m5_script = """
            const menu5Xpath = arguments[0];
            function getByXPath(p) {
                try { return document.evaluate(p, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue; } catch (e) { return null; }
            }
            let m5 = getByXPath(menu5Xpath);
            if (!m5) {
                const all = document.querySelectorAll('flow-image-context-menu-items flow-menu-item, flow-media-context-menu-items flow-menu-item');
                if (all.length >= 5) m5 = all[4];
            }
            if (!m5) return null;
            m5.dispatchEvent(new MouseEvent('mouseenter', { bubbles: true }));
            m5.dispatchEvent(new MouseEvent('mouseover', { bubbles: true }));
            const rect = m5.getBoundingClientRect();
            return {
                x: Math.round(window.mozInnerScreenX + rect.left + rect.width / 2),
                y: Math.round(window.mozInnerScreenY + rect.top + rect.height / 2)
            };
            """
            m5_coord = self.generator.driver.execute_script(get_m5_script, [XPATH_CONTEXT_MENU_ITEM_5])
            if m5_coord:
                NativeOSController.send_mouse_move(m5_coord["x"], m5_coord["y"])

            time.sleep(0.8)
            self.capture_screenshot(8, "submenu_unduhan_muncul", "Kursor mouse mengarah ke item ke-5 dan submenu unduhan terbuka.")
            console.print("[success]✓ Langkah 8 Selesai: Submenu siap.[/success]\n")
            self.step_pause("Submenu unduhan siap.")

            # ------------------------------------------------------------------
            # LANGKAH 9: Klik Tombol Download (Submenu Item 2)
            # ------------------------------------------------------------------
            console.print(Panel("[bold cyan]LANGKAH 9:[/bold cyan] Mengeklik Tombol Download di Submenu", box=box.SIMPLE))
            get_dl_script = """
            const dlXpath = arguments[0];
            function getByXPath(p) {
                try { return document.evaluate(p, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue; } catch (e) { return null; }
            }
            let dl = getByXPath(dlXpath);
            if (!dl) {
                const overlays = document.querySelectorAll('div.cdk-overlay-pane flow-menu-item, flow-menu-item');
                for (let el of overlays) {
                    if ((el.innerText || '').toLowerCase().includes('download') || (el.innerText || '').toLowerCase().includes('unduh')) {
                        dl = el; break;
                    }
                }
                if (!dl && overlays.length >= 2) dl = overlays[1];
            }
            if (!dl) return null;
            const rect = dl.getBoundingClientRect();
            return {
                x: Math.round(window.mozInnerScreenX + rect.left + rect.width / 2),
                y: Math.round(window.mozInnerScreenY + rect.top + rect.height / 2)
            };
            """
            dl_coord = self.generator.driver.execute_script(get_dl_script, [XPATH_SUBMENU_DOWNLOAD_ITEM_2])
            if not dl_coord:
                raise RuntimeError("Koordinat tombol download submenu tidak ditemukan.")

            NativeOSController.send_mouse_click(dl_coord["x"], dl_coord["y"])
            time.sleep(1.0)
            self.capture_screenshot(9, "tombol_download_diklik", "Tombol download diklik dan proses unduhan dimulai.")
            console.print("[success]✓ Langkah 9 Selesai: Tombol download diklik.[/success]\n")

            # ------------------------------------------------------------------
            # LANGKAH 10: Pemantauan Unduhan & Pemindahan Berkas
            # ------------------------------------------------------------------
            console.print(Panel("[bold cyan]LANGKAH 10:[/bold cyan] Menunggu Berkas .jpg di Folder Unduhan", box=box.SIMPLE))
            downloaded = self.generator.wait_for_downloaded_file(existing_files=existing_files, timeout=60)

            dest_dir = self.workspace_dir / "outputs"
            dest_dir.mkdir(parents=True, exist_ok=True)
            slug = re.sub(r"[^\w\s-]", "", prompt)[:30].strip().replace(" ", "_")
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            target_file = dest_dir / f"{slug}_{timestamp}.jpg"
            shutil.move(str(downloaded), str(target_file))

            self.capture_screenshot(10, "unduhan_selesai_dan_dipindahkan", f"File berhasil dipindahkan ke {target_file.name}.")
            console.print("[success]✓ Langkah 10 Selesai: Berkas berhasil diunduh dan dipindahkan.[/success]\n")

        except Exception as e:
            console.print(f"\n[error]✗ Uji Coba Terhenti karena Kesalahan:[/error] {e}")
            try:
                self.capture_screenshot(99, "kegagalan_eksekusi", str(e))
            except Exception:
                pass
            return 1
        finally:
            self.generator.close()

        # Cetak Tabel Rekapitulasi Screenshot
        summary_table = Table(title="[bold green]REKAPITULASI BUKTI TANGKAPAN LAYAR (AUDIT SCREENSHOTS)[/bold green]", box=box.ROUNDED)
        summary_table.add_column("No", style="cyan", width=5)
        summary_table.add_column("Nama Langkah", style="bold white", width=32)
        summary_table.add_column("Nama File Tangkapan Layar", style="gold", width=38)
        summary_table.add_column("Deskripsi", style="dim white")

        for num, name, path, desc in self.screenshots:
            summary_table.add_row(str(num), name, path.name, desc)

        console.print(summary_table)

        console.print(
            Panel(
                f"[bold green]SELURUH PENGUJIAN OTOMASI SELESAI DENGAN SUKSES![/bold green]\n\n"
                f"[muted]Direktori Bukti Screenshot:[/muted] [cyan]{self.run_dir}[/cyan]\n"
                f"[muted]Hasil Gambar Akhir:[/muted] [white]{target_file}[/white]\n"
                f"[muted]Total Tangkapan Layar:[/muted] [gold]{len(self.screenshots)} berkas PNG[/gold]",
                box=box.ROUNDED,
                style="color(240)",
            )
        )
        return 0


def main() -> int:
    prompt, output_dest, timeout = parse_cli_args()
    auto_mode = "--auto" in sys.argv

    if not prompt:
        prompt = "gambar produk hidup estetik di atas meja kayu sinematik"

    tester = StepByStepTester(auto_mode=auto_mode)
    return tester.run_test(prompt=prompt, timeout=timeout)


if __name__ == "__main__":
    sys.exit(main())
