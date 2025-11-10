# 使用 PyMySQL 替代 mysqlclient（Windows 推薦）

如果 `mysqlclient` 安裝失敗（Windows 常見問題），可以使用 `PyMySQL` 替代。

## 步驟 1: 修改 pyproject.toml

將 `mysqlclient` 改為 `pymysql`：

```toml
[tool.poetry.dependencies]
# 移除這行：
# mysqlclient = "^2.2"

# 新增這行：
pymysql = "^1.1"
```

## 步驟 2: 修改 settings/base.py

在 `backend/src/config/settings/base.py` 檔案的最上方（import 區塊）新增：

```python
import pymysql
pymysql.install_as_MySQLdb()
```

## 步驟 3: 重新安裝依賴

```bash
poetry install
```

## 完成

現在可以正常使用 MySQL 資料庫了，Django 會將 PyMySQL 當作 MySQLdb 使用。

