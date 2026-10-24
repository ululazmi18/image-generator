@echo off
rem ==============================================================================
rem LOGIN BROWSER RUNNER — GOOGLE FLOW AUTHENTICATION
rem ==============================================================================
chcp 65001 >nul
echo ==============================================================================
echo  Buka Firefox Portable untuk Login Akun Google (Google Flow)
echo ==============================================================================
echo  1. Masuk / Login menggunakan akun Google Anda pada jendela peramban.
echo  2. Pastikan antarmuka kanvas Google Flow terbuka dan siap digunakan.
echo  3. Setelah selesai login, TUTUP jendela Firefox ini agar image_generator.py
echo     dapat menjalankannya secara otomatis di latar belakang.
echo ==============================================================================
echo.

start "" "%~dp0firefox_portable\App\Firefox64\firefox.exe" -profile "%~dp0browser_profile" "https://flow.google.com"

pause
