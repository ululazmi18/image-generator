# ==============================================================================
# GOOGLE FLOW IMAGE GENERATOR — 1-CLICK ALL-IN-ONE INSTALLER & BOOTSTRAPPER
# ==============================================================================
# Cara menjalankan langsung dari GitHub:
# irm https://raw.githubusercontent.com/ululazmi18/image-generator/main/install.ps1 | iex
# ==============================================================================

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host " 🎨 GOOGLE FLOW IMAGE GENERATOR — AUTO INSTALLER & PROVISIONER" -ForegroundColor Cyan
Write-Host " Otomasi Penuh: Deteksi Alat, Dependensi, Peramban Stealth, & Kanvas Flow" -ForegroundColor DarkGray
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""

function Refresh-EnvPath {
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

# 1. PERIKSA ATAU PASANG 7-ZIP
Write-Host "[1/6] Memeriksa ketersediaan 7-Zip..." -ForegroundColor Yellow
$has7z = (Get-Command 7z -ErrorAction SilentlyContinue) -or (Test-Path "C:\Program Files\7-Zip\7z.exe") -or (Test-Path "C:\Program Files (x86)\7-Zip\7z.exe")
if (-not $has7z) {
    Write-Host "      7-Zip belum terpasang. Memasang 7-Zip otomatis via winget..." -ForegroundColor Cyan
    winget install --id 7zip.7zip -e --source winget --accept-source-agreements --accept-package-agreements --silent
    Refresh-EnvPath
}
Write-Host "      ✓ 7-Zip siap digunakan." -ForegroundColor Green

# 2. PERIKSA ATAU PASANG GIT
Write-Host "[2/6] Memeriksa ketersediaan Git..." -ForegroundColor Yellow
$hasGit = Get-Command git -ErrorAction SilentlyContinue
if (-not $hasGit) {
    Write-Host "      Git belum terpasang. Memasang Git otomatis via winget..." -ForegroundColor Cyan
    winget install --id Git.Git -e --source winget --accept-source-agreements --accept-package-agreements --silent
    Refresh-EnvPath
}
Write-Host "      ✓ Git siap digunakan." -ForegroundColor Green

# 3. PERIKSA ATAU PASANG PYTHON
Write-Host "[3/6] Memeriksa ketersediaan Python..." -ForegroundColor Yellow
$pythonCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonCmd = "py"
}

if (-not $pythonCmd) {
    Write-Host "      Python belum terpasang. Memasang Python 3.12 otomatis via winget..." -ForegroundColor Cyan
    winget install --id Python.Python.3.12 -e --source winget --accept-source-agreements --accept-package-agreements --silent
    Refresh-EnvPath
    if (Get-Command python -ErrorAction SilentlyContinue) { $pythonCmd = "python" }
}

if (-not $pythonCmd) {
    Write-Host "      ✗ Python tidak dapat ditemukan setelah instalasi. Harap restart terminal Anda." -ForegroundColor Red
    exit 1
}
$pyVer = & $pythonCmd --version
Write-Host "      ✓ Python terdeteksi: $pyVer" -ForegroundColor Green

# 4. KLONING ATAU PINDAH KE DIREKTORI PROYEK
Write-Host "[4/6] Menyiapkan repositori image-generator..." -ForegroundColor Yellow
$targetDir = "image-generator"
if (-not (Test-Path "image_generator.py")) {
    if (-not (Test-Path $targetDir)) {
        Write-Host "      Mengkloning image-generator dari GitHub..." -ForegroundColor Cyan
        git clone https://github.com/ululazmi18/image-generator.git
    }
    Set-Location $targetDir
}
Write-Host "      ✓ Berada di direktori: $(Get-Location)" -ForegroundColor Green

# 5. PASANG DEPENDENSI PIP
Write-Host "[5/6] Memasang dependensi Python (rich, pillow, dll)..." -ForegroundColor Yellow
& $pythonCmd -m pip install -r requirements.txt --quiet
Write-Host "      ✓ Pustaka dependensi Python siap." -ForegroundColor Green

# 6. SIAPKAN PERAMBAN FIREFOX PORTABLE STEALTH
Write-Host "[6/6] Memeriksa biner peramban portabel & profil stealth..." -ForegroundColor Yellow
$ffBin = "firefox_portable\App\Firefox64\firefox.exe"
$profileDir = "browser_profile"

if (-not (Test-Path $ffBin) -or -not (Test-Path $profileDir)) {
    Write-Host "      Biner atau profil belum lengkap. Menyiapkan otomatis via firefox-stealth-automation..." -ForegroundColor Cyan
    $subRepo = "firefox-stealth-automation"
    if (-not (Test-Path $subRepo)) {
        git clone https://github.com/ululazmi18/firefox-stealth-automation.git
    }
    Push-Location $subRepo
    & $pythonCmd -m pip install -r requirements.txt --quiet
    & $pythonCmd setup_browser.py
    Pop-Location

    Write-Host "      Menyalin biner dan profil ke direktori image-generator..." -ForegroundColor Cyan
    Copy-Item -Path ".\firefox-stealth-automation\browser_profile" -Destination ".\" -Recurse -Force
    Copy-Item -Path ".\firefox-stealth-automation\firefox_portable" -Destination ".\" -Recurse -Force
}
Write-Host "      ✓ Firefox Portable Stealth & profil telah siap." -ForegroundColor Green

Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Green
Write-Host " ✓ INSTALASI LENGKAP & BERHASIL DISIAPKAN!" -ForegroundColor Green
Write-Host "==============================================================================" -ForegroundColor Green
Write-Host ""
Write-Host " [LANGKAH TERAKHIR] Login Akun Google ke Google Flow:" -ForegroundColor Yellow
Write-Host " Silakan login akun Google Anda di jendela Firefox Portable yang akan terbuka." -ForegroundColor Cyan
Write-Host " Setelah kanvas Google Flow siap, TUTUP jendela Firefox tersebut." -ForegroundColor Cyan
Write-Host ""

$doLogin = Read-Host "Apakah Anda ingin membuka jendela login Google Flow sekarang? (Y/n)"
if ($doLogin -ne "n" -and $doLogin -ne "N") {
    Start-Process -FilePath ".\firefox_portable\App\Firefox64\firefox.exe" -ArgumentList "-profile `"$pwd\browser_profile`" https://flow.google.com"
}

Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Green
Write-Host " 🚀 GENERATOR SIAP DIGUNAKAN SECARA SENYAP (SILENT BACKGROUND):" -ForegroundColor Green
Write-Host "   .\run.bat -a 16:9 -m pro -p `"pemandangan fajar di puncak gunung berapi`"" -ForegroundColor Yellow
Write-Host "   python image_generator.py -a 1:1 -m pro -p `"kucing astronot di bulan`"" -ForegroundColor Yellow
Write-Host "==============================================================================" -ForegroundColor Green
