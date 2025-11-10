@echo off
chcp 65001 >nul
echo ========================================
echo 設定資料庫密碼
echo ========================================
echo.

REM 切換到腳本所在目錄
cd /d "%~dp0"

REM 如果 .env 不存在，從模板建立
if not exist .env (
    if exist env.template (
        copy env.template .env >nul
        echo ✓ 已從模板建立 .env 檔案
    ) else (
        echo ❌ env.template 不存在
        pause
        exit /b 1
    )
)

echo 正在更新 DB_PASSWORD 為: a7638521
echo.

REM 使用 PowerShell 更新密碼
powershell -NoProfile -Command "$content = Get-Content .env -Raw; $content = $content -replace '(?m)^DB_PASSWORD=.*$', 'DB_PASSWORD=a7638521'; Set-Content .env -Value $content -NoNewline"

if errorlevel 1 (
    echo ❌ 自動更新失敗
    echo.
    echo 請手動編輯 .env 檔案，將:
    echo   DB_PASSWORD=your_mysql_password_here
    echo 改為:
    echo   DB_PASSWORD=a7638521
    echo.
    pause
    exit /b 1
)

echo ✓ 密碼已更新
echo.
echo 當前設定:
findstr "DB_" .env
echo.
echo 現在可以執行: 完整測試連線.bat
echo.
pause

