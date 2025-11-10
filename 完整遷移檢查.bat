@echo off
chcp 65001 >nul
echo ========================================
echo 完整遷移檢查與修復
echo ========================================
echo.

cd /d "%~dp0"
call .venv\Scripts\activate.bat

echo [步驟 1] 檢查遷移檔案...
echo.
python manage.py showmigrations | findstr "issues\|common"
if errorlevel 1 (
    echo ⚠ 未找到 issues 或 common 的遷移
    echo.
    echo [步驟 2] 建立遷移檔案...
    python manage.py makemigrations
    if errorlevel 1 (
        echo ❌ 建立遷移檔案失敗
        pause
        exit /b 1
    )
    echo ✓ 遷移檔案建立完成
    echo.
) else (
    echo ✓ 遷移檔案已存在
    echo.
)

echo [步驟 3] 檢查資料表...
python manage.py dbshell -c "SHOW TABLES;" 2>nul | findstr "issues" >nul
if errorlevel 1 (
    echo ⚠ issues 資料表不存在
    echo.
    echo [步驟 4] 執行遷移...
    python manage.py migrate
    if errorlevel 1 (
        echo ❌ 遷移失敗
        pause
        exit /b 1
    )
    echo ✓ 遷移完成
    echo.
) else (
    echo ✓ issues 資料表已存在
    echo.
)

echo [步驟 5] 最終驗證...
echo.
python manage.py showmigrations
echo.

echo ========================================
echo 檢查完成！
echo ========================================
echo.
echo 如果看到 issues 和 common 的遷移標記為 [X]，
echo 表示所有遷移都已執行完成。
echo.
pause

