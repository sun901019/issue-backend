@echo off
chcp 65001 >nul
echo ========================================
echo 快速驗證資料庫連線
echo ========================================
echo.

cd /d "%~dp0"
call .venv\Scripts\activate.bat

echo 使用 Django 管理命令測試連線...
python manage.py check --database default
if errorlevel 1 (
    echo.
    echo ❌ 連線失敗
) else (
    echo.
    echo ✓✓✓ 連線成功！
    echo.
    echo Django 設置檢查通過，可以執行遷移了！
    echo.
    echo 執行: python manage.py makemigrations
    echo 然後: python manage.py migrate
)
echo.
pause

