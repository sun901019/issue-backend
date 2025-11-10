# 不使用 Poetry 的設置方法（使用 pip + venv）

如果 Poetry 安裝有問題，可以使用傳統的 pip + venv 方式。

## 步驟 1: 建立虛擬環境

```powershell
# 在 backend 目錄下
cd C:\Users\FAE\issue-system\backend

# 建立虛擬環境
python -m venv .venv

# 啟動虛擬環境
.venv\Scripts\Activate.ps1
```

如果遇到執行政策錯誤，執行：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 步驟 2: 安裝依賴

```powershell
# 確保虛擬環境已啟動（提示符前會有 (.venv)）
# 升級 pip
python -m pip install --upgrade pip

# 安裝依賴（使用 PyMySQL 替代 mysqlclient，Windows 更穩定）
pip install django==5.1 djangorestframework mysqlclient pendulum drf-spectacular django-cors-headers celery redis python-dotenv

# 如果 mysqlclient 安裝失敗，使用 PyMySQL：
pip install django==5.1 djangorestframework pymysql pendulum drf-spectacular django-cors-headers celery redis python-dotenv
```

## 步驟 3: 設定 PyMySQL（如果使用）

在 `backend/src/config/settings/base.py` 最上方新增：

```python
import pymysql
pymysql.install_as_MySQLdb()
```

## 步驟 4: 建立 .env 檔案

```powershell
# 複製模板
Copy-Item env.template .env

# 編輯 .env
notepad .env
```

修改 `DB_PASSWORD` 為你的 MySQL 密碼。

## 步驟 5: 建立 MySQL 資料庫

```sql
CREATE DATABASE issue_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 步驟 6: 執行遷移

```powershell
# 確保虛擬環境已啟動
python manage.py makemigrations
python manage.py migrate
```

## 步驟 7: 啟動伺服器

```powershell
python manage.py runserver 0.0.0.0:8000
```

## 以後使用時

每次開啟終端後，需要先啟動虛擬環境：

```powershell
cd C:\Users\FAE\issue-system\backend
.venv\Scripts\Activate.ps1
```

