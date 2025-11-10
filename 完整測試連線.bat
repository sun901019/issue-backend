@echo off
chcp 65001 >nul
echo ========================================
echo 完整測試資料庫連線
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
    echo 正在建立...
    copy env.template .env >nul
    echo 請先設定密碼
    pause
    exit /b 1
)

REM 啟動虛擬環境
call .venv\Scripts\activate.bat

echo [1/4] 檢查 .env 設定...
findstr "DB_PASSWORD=a7638521" .env >nul
if errorlevel 1 (
    echo ⚠ 警告: .env 中的密碼可能不是 a7638521
    echo 正在更新...
    powershell -Command "(Get-Content .env) -replace 'DB_PASSWORD=.*', 'DB_PASSWORD=a7638521' | Set-Content .env"
    echo ✓ 密碼已更新
) else (
    echo ✓ 密碼設定正確
)
echo.

echo [2/4] 檢查 Django 設置...
python manage.py check --database default
if errorlevel 1 (
    echo.
    echo ❌ Django 設置檢查失敗
    echo 請檢查錯誤訊息
    pause
    exit /b 1
)
echo ✓ Django 設置正確
echo.

echo [3/4] 測試資料庫連線...
python -c "from django.db import connection; connection.ensure_connection(); print('✓ 資料庫連線成功')" 2>nul
if errorlevel 1 (
    echo ❌ 資料庫連線失敗
    echo.
    echo 可能的原因:
    echo 1. MySQL 服務未啟動
    echo 2. 資料庫 issue_system 不存在
    echo 3. 密碼錯誤
    echo.
    pause
    exit /b 1
)
echo ✓ 資料庫連線成功
echo.

echo [4/4] 檢查資料庫是否存在...
python manage.py dbshell -c "USE issue_system;" 2>nul
if errorlevel 1 (
    echo ⚠ 警告: 資料庫 issue_system 可能不存在
    echo.
    echo 請在 MySQL 中執行:
    echo   CREATE DATABASE issue_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    echo.
) else (
    echo ✓ 資料庫 issue_system 存在
)
echo.

echo ========================================
echo 測試完成！
echo ========================================
echo.
echo 如果所有檢查都通過，現在可以執行:
echo   python manage.py makemigrations
echo   python manage.py migrate
echo.
pause

