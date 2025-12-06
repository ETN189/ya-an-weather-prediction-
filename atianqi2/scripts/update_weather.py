#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import shutil
from pathlib import Path
import time

def print_colored(text, color_code="\033[0m"):
    """彩色打印"""
    colors = {
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "purple": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "reset": "\033[0m"
    }
    print(f"{colors.get(color_code, '')}{text}{colors['reset']}")

def run_crawler():
    """运行爬虫脚本"""
    print_colored("🌤️ 开始更新天气数据...", "cyan")
    print_colored("🕷️ 正在运行爬虫脚本...", "yellow")
    
    # 获取项目路径
    project_root = Path(__file__).parent.parent
    crawler_dir = project_root.parent / "爬虫代码"
    output_dir = crawler_dir / "output"
    
    print_colored(f"项目根目录: {project_root}", "blue")
    print_colored(f"爬虫目录: {crawler_dir}", "blue")
    
    # 切换到爬虫目录并运行爬虫
    original_dir = os.getcwd()
    try:
        os.chdir(crawler_dir)
        print_colored("正在执行爬虫脚本...", "yellow")
        
        # 运行爬虫脚本，不捕获输出以避免编码问题
        result = subprocess.run([sys.executable, "yun.py"])
        
        if result.returncode == 0:
            print_colored("✅ 爬虫执行完成", "green")
        else:
            print_colored("❌ 爬虫执行出错，返回码: " + str(result.returncode), "red")
            return False
            
    except Exception as e:
        print_colored(f"❌ 执行爬虫时发生异常: {str(e)}", "red")
        return False
    finally:
        # 切换回原始目录
        os.chdir(original_dir)
    
    return True

def copy_chart_files():
    """复制图表文件到静态资源目录"""
    print_colored("📂 开始复制图表文件...", "yellow")
    
    # 路径配置
    project_root = Path(__file__).parent.parent
    crawler_dir = project_root.parent / "爬虫代码"
    output_dir = crawler_dir / "output"
    static_charts_dir = project_root / "static" / "weather_charts"
    
    # 确保目标目录存在
    static_charts_dir.mkdir(parents=True, exist_ok=True)
    
    # 需要复制的文件列表
    chart_files = [
        'hourly_temperature_trend.png',
        'hourly_weather_table.png',
        'daily_temperature_trend.png',
        'daily_weather_table.png'
    ]
    
    copied_count = 0
    
    for file in chart_files:
        source_path = output_dir / file
        dest_path = static_charts_dir / file
        
        # 检查源文件是否存在
        if source_path.exists():
            try:
                shutil.copy2(source_path, dest_path)
                print_colored(f"✅ 已复制: {file}", "green")
                copied_count += 1
            except Exception as e:
                print_colored(f"❌ 复制失败 {file}: {str(e)}", "red")
        else:
            print_colored(f"⚠️ 文件不存在: {source_path}", "yellow")
    
    print_colored(f"📋 共复制了 {copied_count}/{len(chart_files)} 个文件", "cyan")
    return copied_count > 0

def main():
    """主函数"""
    try:
        start_time = time.time()
        
        # 1. 运行爬虫
        if not run_crawler():
            print_colored("❌ 爬虫执行失败，终止更新流程", "red")
            return False
        
        # 2. 复制图表文件
        if not copy_chart_files():
            print_colored("⚠️ 未成功复制任何图表文件", "yellow")
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        print_colored("✨ 天气数据更新完成!", "green")
        print_colored(f"⏰ 总耗时: {elapsed_time:.2f} 秒", "cyan")
        
        # 显示文件位置
        project_root = Path(__file__).parent.parent
        static_charts_dir = project_root / "static" / "weather_charts"
        print_colored(f"📁 图表文件位置: {static_charts_dir}", "blue")
        
        return True
        
    except Exception as e:
        print_colored(f"❌ 更新过程中发生错误: {str(e)}", "red")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)