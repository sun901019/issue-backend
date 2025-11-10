-- 建立 issue_system 資料庫
-- 執行方式: mysql -u root -p < create_db.sql
-- 或在 MySQL Workbench 中執行

CREATE DATABASE IF NOT EXISTS issue_system 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

-- 顯示建立的資料庫
SHOW DATABASES LIKE 'issue_system';

-- 使用資料庫（選配，Django migrations 會自動處理）
-- USE issue_system;

