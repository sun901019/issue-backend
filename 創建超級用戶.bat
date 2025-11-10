@echo off
chcp 65001 >nul
echo ========================================
echo 創建 Django 超級用戶
echo ========================================
echo.

cd /d "%~dp0"
call .venv\Scripts\activate.bat

echo 這將創建一個超級用戶，用於登入 Admin 後台
echo 訪問: http://localhost:8000/admin/
echo.
echo 按照提示輸入:
echo   - 使用者名稱
echo   - Email（可選，直接按 Enter 跳過）
echo   - 密碼（輸入兩次）
echo.
pause

python manage.py createsuperuser

if errorlevel 1 (
    echo.
    echo ❌ 創建失敗
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✓ 超級用戶創建成功！
echo ========================================
echo.
echo 現在可以訪問 Admin 後台:
echo   http://localhost:8000/admin/
echo.
pause

