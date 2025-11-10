@echo off
chcp 65001 >nul
echo ========================================
echo 後端快速安裝腳本
echo ========================================
echo.

REM 切換到腳本所在目錄
cd /d "%~dp0"

REM 檢查 Python
echo [1/6] 檢查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 錯誤: 找不到 Python，請先安裝 Python 3.12
    pause
    exit /b 1
)
python --version
echo ✓ Python 已安裝
echo.

REM 建立虛擬環境
echo [2/6] 建立虛擬環境...
if exist .venv (
    echo ✓ 虛擬環境已存在
) else (
    python -m venv .venv
    if errorlevel 1 (
        echo ❌ 錯誤: 虛擬環境建立失敗
        pause
        exit /b 1
    )
    echo ✓ 虛擬環境建立成功
)
echo.

REM 啟動虛擬環境
echo [3/6] 啟動虛擬環境...
call .venv\Scripts\activate.bat
echo ✓ 虛擬環境已啟動
echo.

REM 升級 pip
echo [4/6] 升級 pip...
python -m pip install --upgrade pip -q
echo ✓ pip 已升級
echo.

REM 安裝依賴
echo [5/6] 安裝依賴套件（這可能需要幾分鐘）...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 警告: 某些套件安裝失敗，請檢查錯誤訊息
    pause
) else (
    echo ✓ 依賴安裝完成
)
echo.

REM 檢查 .env
echo [6/6] 檢查環境設定...
if exist .env (
    echo ✓ .env 檔案已存在
) else (
    if exist env.template (
        copy env.template .env >nul
        echo ✓ 已建立 .env 檔案（從模板複製）
        echo ⚠ 請編輯 .env 檔案，設定你的 MySQL 密碼
    ) else (
        echo ⚠ 警告: .env 檔案不存在，請手動建立
    )
)
echo.

echo ========================================
echo 安裝完成！
echo ========================================
echo.
echo 下一步操作:
echo 1. 編輯 .env 檔案，設定 MySQL 密碼（DB_PASSWORD）
echo 2. 建立 MySQL 資料庫:
echo    mysql -u root -p
echo    CREATE DATABASE issue_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
echo 3. 執行資料庫遷移:
echo    python manage.py makemigrations
echo    python manage.py migrate
echo 4. 啟動開發伺服器:
echo    python manage.py runserver 0.0.0.0:8000
echo.
pause

