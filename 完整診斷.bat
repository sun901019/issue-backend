@echo off
chcp 65001 >nul
echo ========================================
echo 完整診斷資料庫連線問題
echo ========================================
echo.

REM 切換到腳本所在目錄
cd /d "%~dp0"

echo [步驟 1] 檢查 MySQL 服務...
echo.
sc query MySQL80 2>nul | findstr "RUNNING" >nul
if errorlevel 1 (
    echo ❌ MySQL80 服務未運行
    echo.
    echo 正在嘗試啟動...
    net start MySQL80 2>nul
    if errorlevel 1 (
        echo ❌ 無法自動啟動（可能需要管理員權限）
        echo.
        echo 請手動啟動 MySQL 服務:
        echo 1. 按 Win+R，輸入 services.msc
        echo 2. 找到 MySQL80（或 MySQL）
        echo 3. 右鍵選擇「啟動」
        echo.
        echo 或使用管理員 CMD 執行: net start MySQL80
        echo.
    ) else (
        echo ✓ MySQL80 服務已啟動
    )
) else (
    echo ✓ MySQL80 服務正在運行
)
echo.

echo [步驟 2] 確認 .env 設定...
echo.
if exist .env (
    echo .env 檔案內容（隱藏密碼）:
    type .env | findstr "DB_" | findstr /V "PASSWORD"
    findstr "DB_PASSWORD=a7638521" .env >nul
    if errorlevel 1 (
        echo ⚠ 密碼可能不正確，正在更新...
        powershell -NoProfile -Command "$content = Get-Content .env -Raw; $content = $content -replace '(?m)^DB_PASSWORD=.*$', 'DB_PASSWORD=a7638521'; Set-Content .env -Value $content -NoNewline"
        echo ✓ 密碼已更新為: a7638521
    ) else (
        echo ✓ 密碼設定正確
    )
) else (
    echo ❌ .env 檔案不存在
    if exist env.template (
        copy env.template .env >nul
        powershell -NoProfile -Command "$content = Get-Content .env -Raw; $content = $content -replace '(?m)^DB_PASSWORD=.*$', 'DB_PASSWORD=a7638521'; Set-Content .env -Value $content -NoNewline"
        echo ✓ 已建立 .env 並設定密碼
    )
)
echo.

echo [步驟 3] 檢查虛擬環境...
if not exist .venv (
    echo ❌ 虛擬環境不存在
    pause
    exit /b 1
)
echo ✓ 虛擬環境存在
echo.

echo [步驟 4] 測試 Django 連線...
call .venv\Scripts\activate.bat
python manage.py check --database default 2>&1
if errorlevel 1 (
    echo.
    echo ❌ 連線失敗
    echo.
    echo 請確認:
    echo 1. MySQL 服務已啟動（見步驟 1）
    echo 2. 密碼正確（已設定為: a7638521）
    echo 3. 資料庫 issue_system 存在（從圖片看已存在）
    echo.
) else (
    echo.
    echo ✓ Django 設置檢查通過
    echo.
    echo [步驟 5] 測試實際資料庫連線...
    python manage.py dbshell -c "SELECT 1;" 2>nul
    if errorlevel 1 (
        echo ❌ 無法連接到資料庫
        echo.
        echo 請確認:
        echo 1. MySQL 服務正在運行
        echo 2. 密碼正確
        echo 3. 資料庫 issue_system 已建立
        echo.
    ) else (
        echo.
        echo ========================================
        echo ✓✓✓ 連線成功！可以執行遷移了！
        echo ========================================
        echo.
        echo 執行以下命令建立資料表:
        echo   python manage.py makemigrations
        echo   python manage.py migrate
        echo.
    )
)
echo.
pause

