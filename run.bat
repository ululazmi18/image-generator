@echo off
rem ==============================================================================
rem IMAGE GENERATOR RUNNER — GOOGLE FLOW AUTOMATION (SILENT BACKGROUND)
rem ==============================================================================
chcp 65001 >nul

python "%~dp0image_generator.py" %*

if "%~1"=="" pause
