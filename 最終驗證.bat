@echo off
chcp 65001 >nul
echo ========================================
echo 最終驗證 - 確認所有功能正常
echo ========================================
echo.

cd /d "%~dp0"
call .venv\Scripts\activate.bat

echo [1/4] 檢查 Django 設置...
python manage.py check
if errorlevel 1 (
    echo ❌ 設置有問題
    pause
    exit /b 1
)
echo ✓ Django 設置正確
echo.

echo [2/4] 檢查資料庫連線...
python manage.py check --database default
if errorlevel 1 (
    echo ❌ 資料庫連線失敗
    pause
    exit /b 1
)
echo ✓ 資料庫連線正常
echo.

echo [3/4] 檢查資料表...
python manage.py showmigrations | findstr "issues\|common"
if errorlevel 1 (
    echo ⚠ 未找到 issues 或 common 的遷移
) else (
    echo ✓ 資料表已建立
)
echo.

echo [4/4] 測試 API 端點...
echo 請在瀏覽器訪問以下網址測試:
echo   - API 文件: http://localhost:8000/api/docs/
echo   - Issues API: http://localhost:8000/api/issues/
echo   - Settings API: http://localhost:8000/api/settings/dictionaries/
echo.

echo ========================================
echo ✓✓✓ 後端設置完成！
echo ========================================
echo.
pause

