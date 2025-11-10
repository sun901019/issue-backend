@echo off
chcp 65001 >nul
echo ========================================
echo 修復遷移問題 - 重建資料表
echo ========================================
echo.

cd /d "%~dp0"
call .venv\Scripts\activate.bat

echo [步驟 1] 檢查當前資料表...
python manage.py dbshell -c "SHOW TABLES;" 2>nul
echo.

echo [步驟 2] 檢查 django_migrations 表...
python manage.py dbshell -c "SELECT app, name FROM django_migrations WHERE app='issues';" 2>nul
echo.

echo [步驟 3] 方案選擇:
echo.
echo 如果資料表不存在但遷移記錄存在，有兩種解決方式:
echo.
echo 方案 A: 偽造遷移（推薦，如果資料表真的不存在）
echo   這會刪除 issues 的遷移記錄，然後重新執行遷移
echo.
echo 方案 B: 手動檢查資料表
echo   確認是否真的不存在，還是只是檢查腳本的問題
echo.
set /p choice="請選擇方案 (A/B): "

if /i "%choice%"=="A" goto fake_migration
if /i "%choice%"=="B" goto check_tables
goto end

:fake_migration
echo.
echo [執行] 刪除 issues 的遷移記錄...
python manage.py dbshell -c "DELETE FROM django_migrations WHERE app='issues';" 2>nul
echo ✓ 已刪除遷移記錄
echo.

echo [執行] 重新執行遷移...
python manage.py migrate issues
if errorlevel 1 (
    echo ❌ 遷移失敗
    pause
    exit /b 1
)
echo ✓ 遷移完成
echo.

echo [驗證] 檢查資料表...
python manage.py dbshell -c "SHOW TABLES;" 2>nul | findstr "issues\|projects\|customers"
if errorlevel 1 (
    echo ❌ 資料表仍未建立
    echo 請檢查錯誤訊息
) else (
    echo ✓ 資料表已建立
)
goto end

:check_tables
echo.
echo [檢查] 列出所有資料表...
python manage.py dbshell -c "SHOW TABLES;" 2>nul
echo.
echo 請確認是否看到 issues、projects、customers 等表
goto end

:end
echo.
pause

