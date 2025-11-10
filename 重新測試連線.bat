@echo off
chcp 65001 >nul
echo ========================================
echo 重新測試資料庫連線
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

REM 啟動虛擬環境
call .venv\Scripts\activate.bat

echo [1/2] 確認 .env 設定...
findstr "DB_PASSWORD=a7638521" .env >nul
if errorlevel 1 (
    echo ⚠ 密碼可能未正確設定，正在更新...
    powershell -NoProfile -Command "$content = Get-Content .env -Raw; $content = $content -replace '(?m)^DB_PASSWORD=.*$', 'DB_PASSWORD=a7638521'; Set-Content .env -Value $content -NoNewline"
    echo ✓ 密碼已更新
) else (
    echo ✓ 密碼設定正確 (a7638521)
)
echo.

echo [2/2] 測試 Django 資料庫連線...
python manage.py check --database default
if errorlevel 1 (
    echo.
    echo ❌ 連線失敗
    echo.
    echo 請執行: 檢查MySQL服務.bat
    echo 確認 MySQL 服務是否啟動
    echo.
    pause
    exit /b 1
)

echo.
python -c "from django.db import connection; connection.ensure_connection(); print('✓ 資料庫連線成功！')"
if errorlevel 1 (
    echo ❌ 連線失敗
    pause
    exit /b 1
)
echo.

echo ========================================
echo ✓ 連線成功！
echo ========================================
echo.
echo 現在可以執行遷移:
echo   python manage.py makemigrations
echo   python manage.py migrate
echo.
pause

