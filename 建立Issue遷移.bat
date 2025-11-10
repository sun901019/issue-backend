@echo off
chcp 65001 >nul
echo ========================================
echo 建立 Issue 系統的遷移檔案
echo ========================================
echo.

cd /d "%~dp0"
call .venv\Scripts\activate.bat

echo [1/3] 確保 migrations 目錄存在...
if not exist "src\common\migrations" mkdir "src\common\migrations"
if not exist "src\issues\migrations" mkdir "src\issues\migrations"
if not exist "src\reports\migrations" mkdir "src\reports\migrations"
if not exist "src\settings\migrations" mkdir "src\settings\migrations"
echo ✓ migrations 目錄已建立
echo.

echo [2/3] 建立遷移檔案...
python manage.py makemigrations
if errorlevel 1 (
    echo ❌ 建立遷移檔案失敗
    echo.
    echo 請檢查錯誤訊息
    pause
    exit /b 1
)
echo ✓ 遷移檔案建立完成
echo.

echo [3/3] 執行遷移（建立資料表）...
python manage.py migrate
if errorlevel 1 (
    echo ❌ 遷移失敗
    pause
    exit /b 1
)
echo.

echo ========================================
echo ✓✓✓ 遷移完成！
echo ========================================
echo.
echo 驗證遷移狀態:
python manage.py showmigrations
echo.
echo 現在應該可以看到:
echo   - common
echo   - issues (包含所有 Issue 相關表)
echo   - reports
echo   - settings
echo.
echo 重新訪問 http://localhost:8000/api/issues/
echo 應該可以正常顯示了！
echo.
pause

