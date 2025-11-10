@echo off
chcp 65001 >nul
echo ========================================
echo 檢查遷移狀態
echo ========================================
echo.

cd /d "%~dp0"
call .venv\Scripts\activate.bat

echo 顯示所有 Apps 的遷移狀態:
echo.
python manage.py showmigrations
echo.

echo ========================================
echo 檢查特定 Apps 的遷移檔案...
echo ========================================
echo.

if exist "src\issues\migrations\*.py" (
    echo ✓ issues 有遷移檔案
    dir /b "src\issues\migrations\*.py" | findstr /V "__init__"
) else (
    echo ❌ issues 沒有遷移檔案
    echo 需要執行: python manage.py makemigrations issues
)
echo.

if exist "src\common\migrations\*.py" (
    echo ✓ common 有遷移檔案
    dir /b "src\common\migrations\*.py" | findstr /V "__init__"
) else (
    echo ⚠ common 沒有遷移檔案（如果沒有模型，這是正常的）
)
echo.

echo ========================================
echo 檢查資料表是否存在...
echo ========================================
echo.

python manage.py dbshell -c "SHOW TABLES;" 2>nul | findstr "issues\|projects\|customers" >nul
if errorlevel 1 (
    echo ⚠ 未找到 Issue 相關的資料表
    echo 需要執行: python manage.py migrate
) else (
    echo ✓ Issue 相關的資料表已存在
    python manage.py dbshell -c "SHOW TABLES;" 2>nul | findstr "issues\|projects\|customers"
)
echo.

pause

