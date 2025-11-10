@echo off
chcp 65001 >nul
echo ========================================
echo 執行資料庫遷移（完整版）
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

echo [1/4] 檢查 Django 設置...
python manage.py check --database default
if errorlevel 1 (
    echo ❌ Django 設置檢查失敗
    pause
    exit /b 1
)
echo ✓ Django 設置正確
echo.

echo [2/4] 建立遷移檔案...
python manage.py makemigrations
if errorlevel 1 (
    echo ❌ 建立遷移檔案失敗
    pause
    exit /b 1
)
echo ✓ 遷移檔案建立完成
echo.

echo [3/4] 執行資料庫遷移（建立資料表）...
python manage.py migrate
if errorlevel 1 (
    echo ❌ 資料庫遷移失敗
    echo.
    echo 請檢查錯誤訊息
    pause
    exit /b 1
)
echo ✓ 資料庫遷移完成
echo.

echo [4/4] 驗證資料表...
python manage.py dbshell -c "SHOW TABLES;" 2>nul
if errorlevel 1 (
    echo ⚠ 無法驗證資料表（可能正常）
) else (
    echo ✓ 資料表已建立
)
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

