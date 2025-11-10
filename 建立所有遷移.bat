@echo off
chcp 65001 >nul
echo ========================================
echo 建立所有 Apps 的遷移檔案
echo ========================================
echo.

cd /d "%~dp0"
call .venv\Scripts\activate.bat

echo [1/2] 為所有 Apps 建立遷移檔案...
echo.
echo 正在為以下 Apps 建立遷移:
echo   - common
echo   - issues
echo   - reports
echo   - settings
echo.

python manage.py makemigrations common issues reports settings
if errorlevel 1 (
    echo.
    echo ⚠ 某些 Apps 可能沒有模型，這是正常的
    echo 繼續執行...
)
echo.

echo [2/2] 執行所有遷移...
python manage.py migrate
if errorlevel 1 (
    echo ❌ 遷移失敗
    pause
    exit /b 1
)
echo.

echo ========================================
echo ✓✓✓ 所有遷移完成！
echo ========================================
echo.
echo 驗證遷移狀態:
python manage.py showmigrations
echo.
echo 現在可以訪問:
echo   http://localhost:8000/api/issues/
echo.
pause

