@echo off
chcp 65001 >nul
echo ========================================
echo 檢查 MySQL 服務狀態
echo ========================================
echo.

echo [1/3] 檢查 MySQL 服務狀態...
sc query MySQL80 >nul 2>&1
if errorlevel 1 (
    echo ⚠ MySQL80 服務未找到，嘗試其他服務名稱...
    sc query MySQL >nul 2>&1
    if errorlevel 1 (
        echo ❌ 找不到 MySQL 服務
        echo.
        echo 請確認:
        echo 1. MySQL 已安裝
        echo 2. MySQL 服務名稱（可能是 MySQL80、MySQL、MySQL57 等）
        echo.
        echo 手動啟動方式:
        echo   net start MySQL80
        echo   或
        echo   在服務管理員中啟動 MySQL 服務
        echo.
    ) else (
        echo ✓ 找到 MySQL 服務
        sc query MySQL | findstr "STATE"
    )
) else (
    echo ✓ 找到 MySQL80 服務
    sc query MySQL80 | findstr "STATE"
)
echo.

echo [2/3] 檢查服務是否運行...
sc query MySQL80 2>nul | findstr "RUNNING" >nul
if errorlevel 1 (
    sc query MySQL 2>nul | findstr "RUNNING" >nul
    if errorlevel 1 (
        echo ❌ MySQL 服務未運行
        echo.
        echo 正在嘗試啟動 MySQL 服務...
        net start MySQL80 2>nul
        if errorlevel 1 (
            net start MySQL 2>nul
            if errorlevel 1 (
                echo ❌ 無法自動啟動 MySQL 服務
                echo.
                echo 請手動啟動:
                echo 1. 開啟「服務」管理員（services.msc）
                echo 2. 找到 MySQL 服務
                echo 3. 右鍵選擇「啟動」
                echo.
                echo 或使用命令（需要管理員權限）:
                echo   net start MySQL80
                echo.
            ) else (
                echo ✓ MySQL 服務已啟動
            )
        ) else (
            echo ✓ MySQL80 服務已啟動
        )
    ) else (
        echo ✓ MySQL 服務正在運行
    )
) else (
    echo ✓ MySQL80 服務正在運行
)
echo.

echo [3/3] 測試資料庫連線...
cd /d "%~dp0"
if exist .venv (
    call .venv\Scripts\activate.bat
    python -c "from django.db import connection; connection.ensure_connection(); print('✓ Django 資料庫連線成功')" 2>nul
    if errorlevel 1 (
        echo ❌ Django 連線失敗
        echo.
        echo 可能的原因:
        echo 1. 密碼錯誤（已設定為: a7638521）
        echo 2. 資料庫 issue_system 不存在（但從圖片看已存在）
        echo 3. 防火牆阻擋
        echo.
    ) else (
        echo ✓ Django 連線成功！
    )
) else (
    echo ⚠ 虛擬環境不存在，跳過 Django 連線測試
)
echo.

pause

