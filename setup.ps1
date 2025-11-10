# 後端自動設置腳本 (PowerShell)
# 執行方式: .\setup.ps1

Write-Host "=== 後端設置腳本 ===" -ForegroundColor Green

# 檢查 Python
Write-Host "`n[1/6] 檢查 Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "錯誤: 找不到 Python，請先安裝 Python 3.12" -ForegroundColor Red
    exit 1
}
Write-Host "✓ $pythonVersion" -ForegroundColor Green

# 檢查 Poetry
Write-Host "`n[2/6] 檢查 Poetry..." -ForegroundColor Yellow
$poetryVersion = poetry --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Poetry 未安裝，正在安裝..." -ForegroundColor Yellow
    (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
    Write-Host "請重新啟動終端後再執行此腳本" -ForegroundColor Yellow
    exit 1
}
Write-Host "✓ $poetryVersion" -ForegroundColor Green

# 設定 Poetry 環境
Write-Host "`n[3/6] 設定 Poetry 環境..." -ForegroundColor Yellow
poetry env use 3.12
if ($LASTEXITCODE -ne 0) {
    Write-Host "警告: 無法設定 Python 3.12，將使用預設版本" -ForegroundColor Yellow
}

# 安裝依賴
Write-Host "`n[4/6] 安裝依賴套件..." -ForegroundColor Yellow
poetry install
if ($LASTEXITCODE -ne 0) {
    Write-Host "錯誤: 依賴安裝失敗" -ForegroundColor Red
    exit 1
}
Write-Host "✓ 依賴安裝完成" -ForegroundColor Green

# 檢查 .env 檔案
Write-Host "`n[5/6] 檢查環境變數檔案..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host "警告: .env 檔案不存在" -ForegroundColor Yellow
    Write-Host "請建立 .env 檔案並設定資料庫連線資訊" -ForegroundColor Yellow
    Write-Host "參考 .env.example（如果存在）" -ForegroundColor Yellow
} else {
    Write-Host "✓ .env 檔案存在" -ForegroundColor Green
}

# 提示建立資料庫
Write-Host "`n[6/6] 資料庫設置..." -ForegroundColor Yellow
Write-Host "請手動執行以下步驟：" -ForegroundColor Yellow
Write-Host "1. 在 MySQL 中建立資料庫：" -ForegroundColor Cyan
Write-Host "   CREATE DATABASE issue_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" -ForegroundColor White
Write-Host "2. 執行遷移：" -ForegroundColor Cyan
Write-Host "   poetry shell" -ForegroundColor White
Write-Host "   python manage.py makemigrations" -ForegroundColor White
Write-Host "   python manage.py migrate" -ForegroundColor White

Write-Host "`n=== 設置完成 ===" -ForegroundColor Green
Write-Host "下一步: 請按照上述提示完成資料庫設置" -ForegroundColor Yellow

