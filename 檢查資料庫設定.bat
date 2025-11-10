@echo off
chcp 65001 >nul
echo ========================================
echo 檢查資料庫設定
echo ========================================
echo.

REM 切換到腳本所在目錄
cd /d "%~dp0"

if exist .env (
    echo [檢查] .env 檔案內容:
    echo.
    type .env | findstr /V "PASSWORD" | findstr "DB_"
    echo.
    echo ⚠ 注意: 已隱藏密碼欄位
    echo.
    echo 請確認:
    echo 1. DB_PASSWORD 是否與你的 MySQL root 密碼一致
    echo 2. DB_NAME 是否為 issue_system
    echo 3. DB_USER 是否為 root（或你的 MySQL 用戶名）
    echo.
) else (
    echo ❌ .env 檔案不存在
    echo.
    echo 請執行:
    echo   Copy-Item env.template .env
    echo   然後編輯 .env 設定資料庫密碼
    echo.
)

echo [測試] 嘗試連接 MySQL...
mysql -u root -p -e "SELECT 1;" 2>nul
if errorlevel 1 (
    echo ⚠ 無法使用 mysql 命令列工具測試
    echo 請手動測試: mysql -u root -p
) else (
    echo ✓ MySQL 命令列工具可用
)
echo.

pause

