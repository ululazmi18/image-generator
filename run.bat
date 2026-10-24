@echo off
rem ==============================================================================
rem IMAGE GENERATOR RUNNER — GOOGLE FLOW AUTOMATION (100% NATIVE HEADLESS)
rem ==============================================================================
chcp 65001 >nul

python "%~dp0image_generator.py" %*

if "%~1"=="" pause
