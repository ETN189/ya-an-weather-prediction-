# 天气数据自动更新脚本 (增强版)
# 功能: 自动运行爬虫、生成图表并更新到Vue项目
# 支持定时执行和日志记录

param(
    [Parameter(Mandatory=$false)]
    [int]$LoopInterval = 0,  # 循环间隔(分钟)，0表示只执行一次
    [Parameter(Mandatory=$false)]
    [switch]$Silent = $false  # 静默模式，不显示详细输出
)

# 设置 UTF-8 编码
$OutputEncoding = New-Object -Type System.Text.UTF8Encoding
[System.Console]::OutputEncoding = New-Object -Type System.Text.UTF8Encoding

# 日志函数
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    
    # 输出到控制台
    if (-not $Silent) {
        switch ($Level) {
            "ERROR" { Write-Host $logMessage -ForegroundColor Red }
            "WARN"  { Write-Host $logMessage -ForegroundColor Yellow }
            "INFO"  { Write-Host $logMessage -ForegroundColor Green }
            "DEBUG" { Write-Host $logMessage -ForegroundColor Gray }
            default { Write-Host $logMessage -ForegroundColor White }
        }
    }
    
    # 写入日志文件
    $logDir = "logs"
    if (!(Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir | Out-Null
    }
    
    $logFile = Join-Path $logDir "weather_update.log"
    Add-Content -Path $logFile -Value $logMessage
}

# 主函数
function Update-WeatherData {
    try {
        Write-Log "开始更新雅安天气数据" "INFO"
        
        # 记录开始时间
        $startTime = Get-Date
        Write-Log "开始时间: $($startTime.ToString('yyyy-MM-dd HH:mm:ss'))" "INFO"
        
        # 1. 进入爬虫代码目录
        Write-Log "切换到爬虫代码目录" "INFO"
        Push-Location "..\爬虫代码"
        
        # 2. 运行爬虫脚本
        Write-Log "正在运行爬虫脚本获取最新天气数据..." "INFO"
        $process = Start-Process -FilePath "python" -ArgumentList "yun.py" -NoNewWindow -Wait -PassThru
        
        if ($process.ExitCode -ne 0) {
            throw "爬虫脚本运行失败，退出代码: $($process.ExitCode)"
        }
        
        Write-Log "爬虫脚本运行完成" "INFO"
        
        # 3. 检查生成的文件
        Write-Log "检查生成的图表文件..." "INFO"
        $outputDir = "output"
        $requiredFiles = @(
            "hourly_temperature_trend.png",
            "hourly_weather_table.png",
            "daily_temperature_trend.png",
            "daily_weather_table.png"
        )
        
        $allFilesExist = $true
        foreach ($file in $requiredFiles) {
            $filePath = Join-Path $outputDir $file
            if (Test-Path $filePath) {
                $fileSize = (Get-Item $filePath).Length
                Write-Log "✓ $file (大小: $fileSize 字节)" "INFO"
            } else {
                Write-Log "缺少必要文件: $filePath" "ERROR"
                $allFilesExist = $false
            }
        }
        
        if (-not $allFilesExist) {
            throw "部分必要文件缺失，请检查爬虫执行结果"
        }
        
        # 4. 复制文件到Vue项目
        Write-Log "正在将图表文件复制到Vue项目..." "INFO"
        $targetDir = "..\WWW\atianqi2\static\weather_charts"
        
        # 确保目标目录存在
        if (!(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir | Out-Null
            Write-Log "创建目录: $targetDir" "INFO"
        }
        
        # 复制文件
        $filesCopied = 0
        foreach ($file in $requiredFiles) {
            $sourcePath = Join-Path $outputDir $file
            $destinationPath = Join-Path $targetDir $file
            
            Copy-Item $sourcePath -Destination $destinationPath -Force
            Write-Log "✓ $file 已复制到 $targetDir" "INFO"
            $filesCopied++
        }
        
        # 5. 记录完成时间
        $endTime = Get-Date
        $duration = $endTime - $startTime
        
        Write-Log "========================================" "INFO"
        Write-Log "✅ 天气数据更新完成! 成功复制 $filesCopied 个文件" "INFO"
        Write-Log "结束时间: $($endTime.ToString('yyyy-MM-dd HH:mm:ss'))" "INFO"
        Write-Log "总耗时: $($duration.Minutes)分$($duration.Seconds)秒" "INFO"
        Write-Log "========================================" "INFO"
        
        # 6. 提示用户
        if (-not $Silent) {
            Write-Host "📢 请在微信小程序中刷新天气详情页面查看最新数据" -ForegroundColor Magenta
        }
        
        return $true
    } catch {
        Write-Log "错误: $($_.Exception.Message)" "ERROR"
        Write-Log "脚本执行失败，请检查错误信息并重试。" "ERROR"
        return $false
    } finally {
        # 返回原始目录
        Pop-Location
    }
}

# 主程序入口
Write-Host "🌤️ 雅安天气数据自动更新工具 (增强版)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ($LoopInterval -gt 0) {
    Write-Host "🔁 循环模式: 每 $LoopInterval 分钟更新一次" -ForegroundColor Yellow
    Write-Host "按下 Ctrl+C 可以随时停止" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Cyan
    
    while ($true) {
        $result = Update-WeatherData
        if ($result) {
            Write-Host "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - 等待 $LoopInterval 分钟后下次更新..." -ForegroundColor Blue
        } else {
            Write-Host "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - 上次更新失败，将在 $LoopInterval 分钟后重试..." -ForegroundColor Red
        }
        
        Start-Sleep -Seconds ($LoopInterval * 60)
    }
} else {
    Write-Host "➡️ 单次执行模式" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Cyan
    
    $result = Update-WeatherData
    if ($result) {
        Write-Host "🎉 所有操作已完成!" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "❌ 操作失败，请查看日志了解详情" -ForegroundColor Red
        exit 1
    }
}