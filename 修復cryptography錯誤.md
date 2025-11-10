# 修復 cryptography 錯誤

## 問題說明

MySQL 8.0 預設使用 `caching_sha2_password` 認證方式，PyMySQL 需要 `cryptography` 套件來支援此認證方式。

## 解決方案

### 方案 1: 安裝 cryptography 套件（推薦）

在虛擬環境中安裝：

```cmd
cd C:\Users\FAE\issue-system\backend
.venv\Scripts\activate.bat
pip install cryptography
```

### 方案 2: 修改 MySQL 用戶認證方式（如果方案 1 失敗）

如果不想安裝 cryptography，可以將 MySQL 用戶改為使用 `mysql_native_password`：

```sql
-- 連接到 MySQL
mysql -u root -p

-- 修改 root 用戶認證方式
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '你的密碼';
FLUSH PRIVILEGES;
```

### 方案 3: 在 requirements.txt 中加入 cryptography

已更新 `requirements.txt`，包含 `cryptography`。

## 快速修復

執行以下命令：

```cmd
cd C:\Users\FAE\issue-system\backend
.venv\Scripts\activate.bat
pip install cryptography
```

然後重新執行遷移或啟動伺服器。

