@echo off
chcp 65001 >nul
echo ========================================
echo 啟動 Django 開發伺服器
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

echo 啟動開發伺服器...
echo 訪問地址:
echo   - API 文件: http://localhost:8000/api/docs/
echo   - Admin 後台: http://localhost:8000/admin/
echo   - API 端點: http://localhost:8000/api/issues/
echo.
echo 按 Ctrl+C 停止伺服器
echo.

python manage.py runserver 0.0.0.0:8000

pause

