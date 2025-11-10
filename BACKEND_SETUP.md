# 後端設置完整指南

## 步驟 1: 檢查 Python 版本

```bash
python --version
# 應該顯示 Python 3.12.x
```

如果沒有 Python 3.12，請先安裝。

## 步驟 2: 安裝 Poetry（如未安裝）

```powershell
# PowerShell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

或使用 pip：
```bash
pip install poetry
```

## 步驟 3: 安裝後端依賴

```bash
cd backend

# 設定 Poetry 使用 Python 3.12
poetry env use 3.12

# 安裝所有依賴
poetry install

# 啟動虛擬環境
poetry shell
```

## 步驟 4: 建立環境變數檔案

在 `backend/` 目錄下建立 `.env` 檔案：

```env
DEBUG=True
SECRET_KEY=django-insecure-change-me-in-production-please
ALLOWED_HOSTS=localhost,127.0.0.1

DB_ENGINE=django.db.backends.mysql
DB_NAME=issue_system
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306

REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

**重要**: 請將 `DB_PASSWORD` 改為您的 MySQL 密碼！

## 步驟 5: 建立 MySQL 資料庫

### 方法 1: 使用 MySQL 命令列

```bash
mysql -u root -p
```

在 MySQL 中執行：
```sql
CREATE DATABASE issue_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### 方法 2: 使用 MySQL Workbench

1. 開啟 MySQL Workbench
2. 連接到您的 MySQL 伺服器
3. 執行以下 SQL：
```sql
CREATE DATABASE issue_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 步驟 6: 執行資料庫遷移（建表）

```bash
# 確保在 poetry shell 中
cd backend

# 建立遷移檔案
python manage.py makemigrations

# 執行遷移（建立所有資料表）
python manage.py migrate
```

## 步驟 7: 建立超級使用者（選配）

```bash
python manage.py createsuperuser
```

按照提示輸入使用者名稱、Email 和密碼。

## 步驟 8: 驗證設置

```bash
# 啟動開發伺服器
python manage.py runserver 0.0.0.0:8000
```

訪問：
- API 文件: http://localhost:8000/api/docs/
- Admin 後台: http://localhost:8000/admin/

## 常見問題

### 問題 1: mysqlclient 安裝失敗

**Windows 常見問題**: mysqlclient 需要編譯，可能需要 Visual C++ Build Tools。

**解決方案**:
1. 安裝 MySQL Connector/C 或使用 PyMySQL 替代
2. 或使用預編譯的 wheel 檔案

如果遇到問題，可以暫時使用 PyMySQL：

```bash
# 在 pyproject.toml 中將 mysqlclient 改為 pymysql
# 然後在 settings/base.py 中新增：
import pymysql
pymysql.install_as_MySQLdb()
```

### 問題 2: Poetry 找不到 Python 3.12

```bash
# 指定 Python 完整路徑
poetry env use C:\Python312\python.exe
```

### 問題 3: 資料庫連線失敗

檢查：
1. MySQL 服務是否啟動
2. `.env` 中的資料庫資訊是否正確
3. 資料庫 `issue_system` 是否已建立
4. 使用者權限是否足夠

### 問題 4: 遷移失敗

```bash
# 查看詳細錯誤
python manage.py migrate --verbosity 2

# 如果表已存在，可以重置（注意：會刪除所有資料）
python manage.py migrate --run-syncdb
```

## 下一步

設置完成後，您可以：
1. 訪問 Admin 後台管理資料
2. 使用 API 文件測試端點
3. 開始開發功能

