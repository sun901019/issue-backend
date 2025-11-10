@echo off
REM 使用 pip + venv 安裝後端依賴（Windows 批次檔）

echo ========================================
echo 後端依賴安裝腳本（不使用 Poetry）
echo ========================================
echo.

REM 檢查 Python
python --version
if errorlevel 1 (
    echo 錯誤: 找不到 Python，請先安裝 Python 3.12
    pause
    exit /b 1
)

echo.
echo [1/5] 建立虛擬環境...
if exist .venv (
    echo 虛擬環境已存在，跳過建立
) else (
    python -m venv .venv
    if errorlevel 1 (
        echo 錯誤: 虛擬環境建立失敗
        pause
        exit /b 1
    )
    echo 虛擬環境建立成功
)

echo.
echo [2/5] 啟動虛擬環境...
call .venv\Scripts\activate.bat

echo.
echo [3/5] 升級 pip...
python -m pip install --upgrade pip

echo.
echo [4/5] 安裝依賴套件...
echo 注意: 如果 mysqlclient 安裝失敗，將使用 PyMySQL
python -m pip install django==5.1 djangorestframework pymysql pendulum drf-spectacular django-cors-headers celery redis python-dotenv

if errorlevel 1 (
    echo.
    echo 警告: 某些套件安裝失敗，請檢查錯誤訊息
) else (
    echo.
    echo 依賴安裝完成！
)

echo.
echo [5/5] 檢查 .env 檔案...
if exist .env (
    echo .env 檔案已存在
) else (
    echo 警告: .env 檔案不存在
    echo 請複製 env.template 為 .env 並設定資料庫連線
    copy env.template .env
    echo 已建立 .env 檔案，請編輯設定資料庫密碼
)

echo.
echo ========================================
echo 安裝完成！
echo ========================================
echo.
echo 下一步:
echo 1. 編輯 .env 檔案，設定 MySQL 密碼
echo 2. 建立 MySQL 資料庫: CREATE DATABASE issue_system;
echo 3. 執行: python manage.py makemigrations
echo 4. 執行: python manage.py migrate
echo.
pause

