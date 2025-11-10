# 立即開始設置後端

## 當前狀態
- ✅ Python 3.12.6 已安裝
- ❌ Poetry 未安裝
- ❌ 後端依賴未安裝
- ❌ 資料庫未建立

## 快速設置步驟

### 步驟 1: 安裝 Poetry

在 PowerShell 中執行：

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

**重要**: 安裝完成後，需要：
1. 關閉當前終端
2. 重新開啟終端
3. 或執行：`$env:Path += ";$env:USERPROFILE\.local\bin"`

驗證安裝：
```powershell
poetry --version
```

### 步驟 2: 進入後端目錄並安裝依賴

```powershell
cd backend
poetry env use 3.12
poetry install
```

### 步驟 3: 建立 .env 檔案

在 `backend/` 目錄下建立 `.env` 檔案，內容：

```env
DEBUG=True
SECRET_KEY=django-insecure-change-me-in-production-please
ALLOWED_HOSTS=localhost,127.0.0.1

DB_ENGINE=django.db.backends.mysql
DB_NAME=issue_system
DB_USER=root
DB_PASSWORD=你的MySQL密碼
DB_HOST=localhost
DB_PORT=3306

REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### 步驟 4: 建立 MySQL 資料庫

**方法 1: 使用 MySQL 命令列**
```bash
mysql -u root -p
```
然後執行：
```sql
CREATE DATABASE issue_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

**方法 2: 使用 MySQL Workbench**
1. 開啟 MySQL Workbench
2. 連接到 MySQL 伺服器
3. 執行：`CREATE DATABASE issue_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;`

**方法 3: 使用 SQL 檔案**
```bash
mysql -u root -p < backend/create_db.sql
```

### 步驟 5: 執行資料庫遷移

```powershell
# 啟動 Poetry 虛擬環境
poetry shell

# 建立遷移檔案
python manage.py makemigrations

# 執行遷移（建立所有資料表）
python manage.py migrate
```

### 步驟 6: 建立超級使用者（選配）

```powershell
python manage.py createsuperuser
```

### 步驟 7: 啟動開發伺服器

```powershell
python manage.py runserver 0.0.0.0:8000
```

## 驗證設置

訪問以下網址確認設置成功：
- API 文件: http://localhost:8000/api/docs/
- Admin 後台: http://localhost:8000/admin/

## 如果遇到問題

### mysqlclient 安裝失敗（Windows 常見）

**解決方案**: 使用 PyMySQL 替代

1. 修改 `backend/pyproject.toml`：
```toml
# 將 mysqlclient 改為 pymysql
pymysql = "^1.1"
```

2. 在 `backend/src/config/settings/base.py` 最上方新增：
```python
import pymysql
pymysql.install_as_MySQLdb()
```

3. 重新安裝：
```powershell
poetry install
```

### Poetry 找不到 Python 3.12

```powershell
# 指定完整路徑
poetry env use C:\Python312\python.exe
# 或
poetry env use C:\Users\你的用戶名\AppData\Local\Programs\Python\Python312\python.exe
```

