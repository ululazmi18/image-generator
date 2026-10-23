@echo off
rem ==============================================================================
rem GOOGLE FLOW SHORTCUT RUNNER
rem ==============================================================================
chcp 65001 >nul

rem Eksekusi automate_flow.py dengan seluruh argumen yang diteruskan
python "%~dp0automate_flow.py" %*
