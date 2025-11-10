@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo 建立 Customer 模型遷移
echo ========================================
echo.

if exist .venv\Scripts\activate.bat (
    echo [1/2] 激活虛擬環境...
    call .venv\Scripts\activate.bat
) else (
    echo 警告: 未找到虛擬環境，使用系統 Python
)

echo [2/2] 建立遷移...
python manage.py makemigrations issues

echo.
echo ========================================
echo 遷移建立完成！
echo 請執行: python manage.py migrate
echo ========================================
pause

