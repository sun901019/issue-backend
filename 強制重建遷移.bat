@echo off
chcp 65001 >nul
echo ========================================
echo 強制重建 issues 遷移
echo ========================================
echo.
echo ⚠ 警告: 這將刪除 issues 的遷移記錄並重新執行
echo 如果資料表已存在，可能會出錯
echo.
pause

cd /d "%~dp0"
call .venv\Scripts\activate.bat

echo [1/4] 檢查當前資料表...
python -c "import os; import sys; sys.path.insert(0, 'src'); os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local'); import django; django.setup(); from django.db import connection; cursor = connection.cursor(); cursor.execute('SHOW TABLES'); tables = [row[0].decode() if isinstance(row[0], bytes) else row[0] for row in cursor.fetchall()]; print('現有資料表:'); [print(f'  - {t}') for t in sorted(tables)]"
echo.

echo [2/4] 刪除 issues 的遷移記錄...
python -c "import os; import sys; sys.path.insert(0, 'src'); os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local'); import django; django.setup(); from django.db import connection; cursor = connection.cursor(); cursor.execute(\"DELETE FROM django_migrations WHERE app='issues'\"); print('✓ 已刪除 issues 的遷移記錄')"
if errorlevel 1 (
    echo ⚠ 無法刪除遷移記錄（可能表不存在或已刪除）
)
echo.

echo [3/4] 重新執行 issues 遷移...
python manage.py migrate issues --fake-initial
if errorlevel 1 (
    echo.
    echo 嘗試不使用 --fake-initial...
    python manage.py migrate issues
    if errorlevel 1 (
        echo ❌ 遷移失敗
        echo.
        echo 請檢查錯誤訊息
        pause
        exit /b 1
    )
)
echo ✓ 遷移執行完成
echo.

echo [4/4] 驗證資料表...
python manage.py dbshell -c "SHOW TABLES;" 2>nul | findstr "issues\|projects\|customers\|sites\|assets"
if errorlevel 1 (
    echo ⚠ 未找到 Issue 相關資料表
    echo.
    echo 請手動檢查:
    echo   python manage.py dbshell
    echo   然後執行: SHOW TABLES;
) else (
    echo ✓ Issue 相關資料表已存在
    python manage.py dbshell -c "SHOW TABLES;" 2>nul | findstr "issues\|projects\|customers\|sites\|assets"
)
echo.

echo ========================================
echo 完成！
echo ========================================
echo.
pause

