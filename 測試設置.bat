@echo off
chcp 65001 >nul
echo ========================================
echo 測試 Django 設置
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

echo [1/4] 檢查 Python 路徑...
python -c "import sys; print('Python 路徑:'); [print(p) for p in sys.path[:5]]"
echo.

echo [2/4] 檢查 Django 安裝...
python -c "import django; print(f'Django 版本: {django.get_version()}')"
if errorlevel 1 (
    echo ❌ Django 未安裝
    pause
    exit /b 1
)
echo ✓ Django 已安裝
echo.

echo [3/4] 檢查 config 模組...
python -c "import sys; sys.path.insert(0, 'src'); import config; print('✓ config 模組可導入')"
if errorlevel 1 (
    echo ❌ config 模組無法導入
    pause
    exit /b 1
)
echo.

echo [4/4] 檢查 Django 設置...
python manage.py check
if errorlevel 1 (
    echo ❌ Django 設置有問題
    pause
    exit /b 1
)
echo ✓ Django 設置正確
echo.

echo ========================================
echo 所有檢查通過！
echo ========================================
echo.
pause

