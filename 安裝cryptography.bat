@echo off
chcp 65001 >nul
echo ========================================
echo 安裝 cryptography 套件
echo ========================================
echo.
echo 此套件為 PyMySQL 連接 MySQL 8.0 所需
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

echo [1/2] 安裝 cryptography...
pip install cryptography
if errorlevel 1 (
    echo ❌ 安裝失敗
    echo.
    echo 如果安裝失敗，可以嘗試:
    echo 1. 升級 pip: python -m pip install --upgrade pip
    echo 2. 使用預編譯版本: pip install --only-binary :all: cryptography
    pause
    exit /b 1
)
echo ✓ cryptography 安裝完成
echo.

echo [2/2] 驗證安裝...
python -c "import cryptography; print(f'✓ cryptography 版本: {cryptography.__version__}')"
if errorlevel 1 (
    echo ❌ 驗證失敗
    pause
    exit /b 1
)
echo.

echo ========================================
echo 安裝完成！
echo ========================================
echo.
echo 現在可以重新執行:
echo   python manage.py migrate
echo   或
echo   python manage.py runserver 0.0.0.0:8000
echo.
pause

