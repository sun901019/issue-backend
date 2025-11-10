@echo off
chcp 65001 >nul
echo ========================================
echo 測試 API 連線（最直接的方法）
echo ========================================
echo.

cd /d "%~dp0"
call .venv\Scripts\activate.bat

echo 這是最直接的方法來確認資料表是否存在
echo.
echo [步驟 1] 啟動開發伺服器...
echo 請在新的終端視窗執行:
echo   cd C:\Users\FAE\issue-system\backend
echo   .venv\Scripts\activate.bat
echo   python manage.py runserver 0.0.0.0:8000
echo.
echo [步驟 2] 在瀏覽器訪問:
echo   http://localhost:8000/api/issues/
echo.
echo 結果判斷:
echo   ✓ 如果顯示: {"count":0,"results":[]}
echo     表示資料表存在，一切正常！
echo.
echo   ❌ 如果顯示: Table 'issue_system.issues' doesn't exist
echo     表示資料表不存在，需要執行修復
echo.
pause

echo.
echo [步驟 3] 使用 Python 直接測試...
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local'); import django; django.setup(); from issues.models import Issue; print('✓ Issue 模型可以導入'); count = Issue.objects.count(); print(f'✓ 資料表存在，目前有 {count} 筆資料')" 2>&1
if errorlevel 1 (
    echo.
    echo ❌ 測試失敗，資料表可能不存在
    echo 請執行: 強制重建遷移.bat
) else (
    echo.
    echo ✓✓✓ 資料表存在且正常！
)
echo.
pause

