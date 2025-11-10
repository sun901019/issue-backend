@echo off
chcp 65001 >nul
title Django 開發伺服器
echo ========================================
echo Django 開發伺服器啟動腳本
echo ========================================
echo.

REM 切換到腳本所在目錄
cd /d "%~dp0"

REM 檢查虛擬環境
if not exist .venv (
    echo ❌ 錯誤: 虛擬環境不存在
    echo 請先執行 快速安裝.bat
    pause
    exit /b 1
)

REM 啟動虛擬環境
call .venv\Scripts\activate.bat

REM 檢查資料庫遷移狀態
echo [檢查] 檢查資料庫遷移狀態...
python manage.py showmigrations 2>nul | findstr /C:"[ ]" >nul
if errorlevel 1 (
    echo ⚠ 發現未執行的遷移，正在執行...
    python manage.py makemigrations
    python manage.py migrate
    echo ✓ 資料庫遷移完成
    echo.
) else (
    echo ✓ 資料庫已是最新狀態
    echo.
)

echo ========================================
echo 啟動開發伺服器
echo ========================================
echo.
echo 訪問地址:
echo   📄 API 文件:    http://localhost:8000/api/docs/
echo   🔧 Admin 後台:  http://localhost:8000/admin/
echo   📊 API 端點:    http://localhost:8000/api/issues/
echo.
echo 按 Ctrl+C 停止伺服器
echo ========================================
echo.

python manage.py runserver 0.0.0.0:8000

pause

