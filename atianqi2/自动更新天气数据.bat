@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

title 雅安天气数据自动更新工具

cls
echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                        雅安天气数据自动更新工具                              ║
echo ║                                                                              ║
echo ║  功能说明:                                                                   ║
echo ║    1. 自动运行天气爬虫获取最新数据                                           ║
echo ║    2. 生成可视化图表                                                         ║
echo ║    3. 自动更新到微信小程序项目                                               ║
echo ║    4. 记录操作日志                                                           ║
echo ║                                                                              ║
echo ║  使用方法:                                                                   ║
echo ║    - 双击此文件: 执行一次更新                                                 ║
echo ║    - 右键选择"定时更新": 每小时自动更新一次                                  ║
echo ║                                                                              ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

echo 请选择操作模式:
echo 1. 立即更新一次天气数据
echo 2. 每小时自动更新(循环模式)
echo 3. 每天自动更新(循环模式)
echo 4. 查看更新日志
echo 5. 退出
echo.

choice /c 12345 /m "请选择操作"
if errorlevel 5 goto :exit
if errorlevel 4 goto :view_log
if errorlevel 3 goto :daily_update
if errorlevel 2 goto :hourly_update
if errorlevel 1 goto :single_update

:single_update
echo.
echo 🔄 正在执行单次天气数据更新...
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0auto_update_weather.ps1"
goto :end

:hourly_update
echo.
echo 🔁 启动每小时自动更新模式...
echo 按 Ctrl+C 可以随时停止
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0auto_update_weather.ps1" -LoopInterval 60
goto :end

:daily_update
echo.
echo 📅 启动每天自动更新模式...
echo 按 Ctrl+C 可以随时停止
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0auto_update_weather.ps1" -LoopInterval 1440
goto :end

:view_log
echo.
echo 📋 查看最近的更新日志:
echo ================================================================================
if exist "logs\weather_update.log" (
    powershell -Command "Get-Content -Path 'logs\weather_update.log' -Tail 20"
) else (
    echo 暂无日志文件，请先执行一次更新操作。
)
echo ================================================================================
echo.
echo 按任意键返回主菜单...
pause >nul
goto :start

:start
goto :eof

:end
echo.
echo.
echo 按任意键退出...
pause >nul
exit

:exit
exit