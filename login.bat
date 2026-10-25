@echo off
rem ==============================================================================
rem LOGIN BROWSER RUNNER — GOOGLE FLOW AUTHENTICATION
rem ==============================================================================
chcp 65001 >nul
cd /d "%~dp0"

echo ==============================================================================
echo  🔐 GOOGLE FLOW AUTHENTICATION MANAGER (100%% AUTOMATED CLI)
echo ==============================================================================
echo  [1] Otomasi Login Penuh (Cukup Masukkan Email & Sandi di Terminal)
echo  [2] Masukkan / Tempel (Paste) Cookie Sesi via Terminal
echo  [3] Uji Verifikasi Status Sesi di Latar Belakang (Headless)
echo  [4] Buka Jendela Peramban Manual (Fallback)
echo  [5] Sinkronkan Sesi dari Profil Eksternal (Opsional)
echo ==============================================================================
set /p opt="Pilih opsi [1-5] (default 1): "

if "%opt%"=="2" (
    python login_cli.py --paste
    goto done
)
if "%opt%"=="3" (
    python login_cli.py --verify
    goto done
)
if "%opt%"=="4" (
    python login_cli.py --login
    goto done
)
if "%opt%"=="5" (
    python login_cli.py --sync
    goto done
)

python login_cli.py --auto

:done
echo.
pause
