@echo off
chcp 65001 >nul
echo ========================================
echo 直接檢查資料表
echo ========================================
echo.

cd /d "%~dp0"
call .venv\Scripts\activate.bat

echo [方法 1] 使用 Python 檢查資料表...
echo.
python -c "from django.db import connection; cursor = connection.cursor(); cursor.execute('SHOW TABLES'); tables = [row[0] for row in cursor.fetchall()]; print('資料表列表:'); [print(f'  - {t}') for t in tables]; issue_tables = [t for t in tables if 'issue' in t.lower() or 'project' in t.lower() or 'customer' in t.lower()]; print(''); print('Issue 相關表:' if issue_tables else '⚠ 未找到 Issue 相關表'); [print(f'  ✓ {t}') for t in issue_tables]"
echo.

echo [方法 2] 測試 API 連線...
echo.
echo 請在瀏覽器訪問: http://localhost:8000/api/issues/
echo 如果顯示 {"count":0,"results":[]} 表示資料表存在且正常
echo 如果顯示 Table doesn't exist 表示資料表不存在
echo.

echo [方法 3] 使用 MySQL Workbench 檢查
echo 連接到 localhost:3306，資料庫 issue_system
echo 執行: SHOW TABLES;
echo.

pause

