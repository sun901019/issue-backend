@echo off
chcp 65001 >nul
echo ========================================
echo 簡單檢查資料表
echo ========================================
echo.

cd /d "%~dp0"
call .venv\Scripts\activate.bat

echo 使用 Python 檢查資料表...
echo.
python -c "import os; import sys; sys.path.insert(0, 'src'); os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local'); import django; django.setup(); from django.db import connection; cursor = connection.cursor(); cursor.execute('SHOW TABLES'); tables = [row[0].decode() if isinstance(row[0], bytes) else row[0] for row in cursor.fetchall()]; print('所有資料表:'); [print(f'  - {t}') for t in sorted(tables)]; print(''); issue_tables = [t for t in tables if any(keyword in t.lower() for keyword in ['issue', 'project', 'customer', 'site', 'asset'])]; print('Issue 系統相關表:'); [print(f'  ✓ {t}') for t in sorted(issue_tables)] if issue_tables else print('  ⚠ 未找到 Issue 相關表')"
echo.

pause

