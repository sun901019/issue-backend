@echo off
chcp 65001 >nul
echo ========================================
echo 執行資料庫遷移（建表）
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
echo [1/3] 啟動虛擬環境...
call .venv\Scripts\activate.bat
echo ✓ 虛擬環境已啟動
echo.

REM 檢查 .env
if not exist .env (
    echo ⚠ 警告: .env 檔案不存在
    echo 請先建立 .env 檔案並設定資料庫連線
    pause
    exit /b 1
)

REM 建立遷移檔案
echo [2/3] 建立遷移檔案...
python manage.py makemigrations
if errorlevel 1 (
    echo ❌ 錯誤: 建立遷移檔案失敗
    pause
    exit /b 1
)
echo ✓ 遷移檔案建立完成
echo.

REM 執行遷移
echo [3/3] 執行資料庫遷移（建立資料表）...
python manage.py migrate
if errorlevel 1 (
    echo ❌ 錯誤: 資料庫遷移失敗
    echo 請檢查:
    echo 1. MySQL 服務是否啟動
    echo 2. 資料庫 issue_system 是否已建立
    echo 3. .env 中的資料庫連線資訊是否正確
    pause
    exit /b 1
)
echo ✓ 資料庫遷移完成
echo.

echo ========================================
echo 遷移完成！所有資料表已建立
echo ========================================
echo.
echo 下一步:
echo 1. 建立超級使用者: python manage.py createsuperuser
echo 2. 啟動伺服器: python manage.py runserver 0.0.0.0:8000
echo.
pause

