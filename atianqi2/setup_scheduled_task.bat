@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

title 设置天气数据自动更新计划任务

cls
echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                     设置天气数据自动更新计划任务                             ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

echo 此脚本将创建一个Windows计划任务，用于自动更新天气数据。
echo.
echo 计划任务配置:
echo   - 任务名称: 雅安天气数据自动更新
echo   - 执行频率: 每天上午9点执行一次
echo   - 执行程序: PowerShell脚本
echo   - 工作目录: %~dp0
echo.

echo 确认要创建计划任务吗？
echo.
choice /c YN /m "确认创建"
if errorlevel 2 (
    echo 用户取消操作
    goto :end
)

echo.
echo 正在创建计划任务...

REM 获取当前脚本目录
set "ScriptPath=%~dp0"
set "TaskName=雅安天气数据自动更新"
set "PowerShellScript=%ScriptPath%auto_update_weather.ps1"

REM 删除已存在的同名任务
schtasks /delete /tn "%TaskName%" /f >nul 2>&1

REM 创建计划任务
schtasks /create /tn "%TaskName%" /tr "powershell -ExecutionPolicy Bypass -File \"%PowerShellScript%\" -Silent" /sc daily /st 09:00 /f

if %errorlevel% equ 0 (
    echo.
    echo ✅ 计划任务创建成功!
    echo.
    echo 任务详情:
    echo   - 任务名称: %TaskName%
    echo   - 执行时间: 每天上午9:00
    echo   - 执行脚本: %PowerShellScript%
    echo.
    echo 您可以通过以下方式管理计划任务:
    echo   1. 打开"任务计划程序"查看任务状态
    echo   2. 运行"删除计划任务.bat"来移除任务
    echo.
) else (
    echo.
    echo ❌ 计划任务创建失败，请检查权限设置。
    echo 错误代码: %errorlevel%
    echo.
    echo 请确保您具有管理员权限，并且允许创建计划任务。
)

:end
echo.
echo 按任意键退出...
pause >nul
exit