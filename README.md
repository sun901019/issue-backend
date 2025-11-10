# Backend - Issue System

Django 5.1 + DRF 後端 API。

## 設置步驟

1. 安裝 Poetry（如未安裝）
   ```bash
   pip install poetry
   ```

2. 建立虛擬環境並安裝依賴
   ```bash
   poetry env use 3.12
   poetry install
   poetry shell
   ```

3. 設定環境變數
   ```bash
   cp .env.example .env
   # 編輯 .env 設定資料庫連線等
   ```

4. 建立資料庫並執行遷移
   ```bash
   python manage.py migrate
   ```

5. 建立超級使用者
   ```bash
   python manage.py createsuperuser
   ```

6. 啟動開發伺服器
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

## Celery 設定（選配）

```bash
# 終端 1: 啟動 Redis
redis-server

# 終端 2: 啟動 Celery Worker
celery -A config worker -l info

# 終端 3: 啟動 Celery Beat（排程任務）
celery -A config beat -l info
```

## 測試

```bash
pytest
```

