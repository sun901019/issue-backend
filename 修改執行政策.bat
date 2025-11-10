@echo off
chcp 65001 >nul
echo ========================================
echo 修改 PowerShell 執行政策
echo ========================================
echo.
echo 這將允許 PowerShell 執行本地腳本
echo 只影響當前用戶，不需要管理員權限
echo.
echo 執行後，您就可以正常使用:
echo   .venv\Scripts\Activate.ps1
echo.
pause

powershell -Command "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"

echo.
echo ========================================
if errorlevel 1 (
    echo 修改失敗，請以管理員身份執行此腳本
) else (
    echo 執行政策已修改成功！
    echo 現在可以正常使用 PowerShell 腳本了
)
echo ========================================
echo.
pause

