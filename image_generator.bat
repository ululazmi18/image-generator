@echo off
rem ==============================================================================
rem IMAGE GENERATOR — GOOGLE FLOW AUTOMATION RUNNER
rem ==============================================================================
chcp 65001 >nul

python "%~dp0image_generator.py" %*
