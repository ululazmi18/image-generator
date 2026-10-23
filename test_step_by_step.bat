@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
python test_step_by_step.py %*
pause
