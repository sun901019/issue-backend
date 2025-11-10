@echo off
REM 使用 CMD 啟動虛擬環境（不需要修改 PowerShell 執行政策）
cd /d "%~dp0"
call .venv\Scripts\activate.bat
cmd /k

