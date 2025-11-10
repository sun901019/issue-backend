@echo off
chcp 65001 >nul
echo ========================================
echo 執行資料庫遷移（建立資料表）
echo ========================================
echo.

cd /d "%~dp0"
call .venv\Scripts\activate.bat

echo [1/3] 建立遷移檔案...
python manage.py makemigrations
if errorlevel 1 (
    echo ❌ 建立遷移檔案失敗
    pause
    exit /b 1
)
echo ✓ 遷移檔案建立完成
echo.

echo [2/3] 執行資料庫遷移（建立所有資料表）...
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

echo [3/3] 驗證資料表...
python manage.py showmigrations
echo.

echo ========================================
echo ✓✓✓ 遷移完成！所有資料表已建立
echo ========================================
echo.
echo 現在可以:
echo 1. 重新訪問 http://localhost:8000/api/issues/
echo 2. 應該可以正常顯示 Issue 列表了
echo.
pause

