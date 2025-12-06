@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

title 删除天气数据自动更新计划任务

cls
echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                     删除天气数据自动更新计划任务                             ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

echo 此脚本将删除已创建的Windows计划任务。
echo.

set "TaskName=雅安天气数据自动更新"

echo 检查是否存在计划任务: %TaskName%

REM 检查任务是否存在
schtasks /query /tn "%TaskName%" >nul 2>&1

if %errorlevel% equ 0 (
    echo.
    echo 找到计划任务: %TaskName%
    echo.
    choice /c YN /m "确认删除此计划任务"
    if errorlevel 2 (
        echo 用户取消操作
        goto :end
    )
    
    echo.
    echo 正在删除计划任务...
    schtasks /delete /tn "%TaskName%" /f
    
    if %errorlevel% equ 0 (
        echo.
        echo ✅ 计划任务删除成功!
    ) else (
        echo.
        echo ❌ 计划任务删除失败。
        echo 错误代码: %errorlevel%
    )
) else (
    echo.
    echo ❌ 未找到计划任务: %TaskName%
    echo 可能任务已被删除或从未创建。
)

:end
echo.
echo 按任意键退出...
pause >nul
exit