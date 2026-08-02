@echo off
title LifeOS Auto-Update
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File "%~dp0scripts\update.ps1"
pause
