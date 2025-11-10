@echo off
chcp 65001 >nul
echo ========================================
echo 測試資料庫連線
echo ========================================
echo.

REM 切換到腳本所在目錄
cd /d "%~dp0"

REM 檢查虛擬環境
if not exist .venv (
    echo ❌ 錯誤: 虛擬環境不存在
    pause
    exit /b 1
)

REM 檢查 .env
if not exist .env (
    echo ❌ 錯誤: .env 檔案不存在
    echo 請先建立 .env 檔案
    pause
    exit /b 1
)

REM 啟動虛擬環境
call .venv\Scripts\activate.bat

echo [1/3] 檢查 Django 設置...
python manage.py check --database default
if errorlevel 1 (
    echo.
    echo ❌ 資料庫連線失敗
    echo.
    echo 請檢查:
    echo 1. .env 檔案中的 DB_PASSWORD 是否正確
    echo 2. MySQL 服務是否啟動
    echo 3. 資料庫 issue_system 是否已建立
    echo.
    echo 詳細說明請參考: 修復資料庫連線.md
    pause
    exit /b 1
)
echo ✓ Django 設置檢查通過
echo.

echo [2/3] 測試資料庫連線...
python -c "from django.db import connection; connection.ensure_connection(); print('✓ 資料庫連線成功')"
if errorlevel 1 (
    echo ❌ 資料庫連線失敗
    pause
    exit /b 1
)
echo.

echo [3/3] 檢查資料庫是否存在...
python manage.py dbshell -c "SHOW DATABASES;" 2>nul | findstr issue_system >nul
if errorlevel 1 (
    echo ⚠ 警告: 資料庫 issue_system 可能不存在
    echo 請執行: CREATE DATABASE issue_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
) else (
    echo ✓ 資料庫 issue_system 存在
)
echo.

echo ========================================
echo 測試完成
echo ========================================
echo.
pause

