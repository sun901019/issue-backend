@echo off
chcp 65001 >nul
echo ========================================
echo 更新資料庫密碼
echo ========================================
echo.

REM 切換到腳本所在目錄
cd /d "%~dp0"

if not exist .env (
    echo ❌ .env 檔案不存在，正在從模板建立...
    if exist env.template (
        copy env.template .env >nul
        echo ✓ 已建立 .env 檔案
    ) else (
        echo ❌ env.template 也不存在
        pause
        exit /b 1
    )
)

echo 正在更新 DB_PASSWORD...
echo.

REM 使用 PowerShell 更新密碼（更可靠）
powershell -Command "(Get-Content .env) -replace 'DB_PASSWORD=.*', 'DB_PASSWORD=a7638521' | Set-Content .env"

if errorlevel 1 (
    echo ❌ 更新失敗，請手動編輯 .env 檔案
    echo 將 DB_PASSWORD=your_mysql_password_here 改為 DB_PASSWORD=a7638521
    pause
    exit /b 1
)

echo ✓ 密碼已更新為: a7638521
echo.
echo 請確認 .env 檔案中的設定:
echo   DB_USER=root
echo   DB_PASSWORD=a7638521
echo   DB_NAME=issue_system
echo.
pause

