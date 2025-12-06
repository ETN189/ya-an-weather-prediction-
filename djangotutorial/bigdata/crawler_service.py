"""
爬虫服务模块 - 处理天气数据爬取和图表生成
"""
import os
import subprocess
import time
import sys
import shutil
from pathlib import Path
from datetime import datetime


def get_project_root():
    """获取项目根目录"""
    # 从当前文件向上查找项目根目录
    current = Path(__file__).resolve()
    # 当前在 djangotutorial/bigdata/crawler_service.py
    # 需要向上两级到达项目根目录
    return current.parent.parent.parent


def get_crawler_path():
    """获取爬虫脚本路径"""
    project_root = get_project_root()
    return project_root / '爬虫代码' / 'yun.py'


def get_static_charts_path():
    """获取静态图表目录路径"""
    project_root = get_project_root()
    return project_root / 'djangotutorial' / 'static' / 'weather_charts'


def get_crawler_output_path():
    """获取爬虫输出目录路径 (生成的 png/json 在这里)"""
    return get_project_root() / '爬虫代码' / 'output'


def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)


def sync_charts_to_static():
    """将爬虫输出的图表复制到 Django 静态目录"""
    src = get_crawler_output_path()
    dst = get_static_charts_path()
    ensure_dir(dst)

    files = [
        'hourly_temperature_trend.png',
        'hourly_weather_table.png',
        'daily_temperature_trend.png',
        'daily_weather_table.png',
    ]

    copied = []
    for name in files:
        s = src / name
        d = dst / name
        if s.exists():
            shutil.copy2(str(s), str(d))
            copied.append(str(d))
    return copied


def run_weather_crawler():
    """
    运行天气爬虫脚本
    返回: dict - 包含执行结果信息
    """
    crawler_path = get_crawler_path()
    
    if not crawler_path.exists():
        return {
            'success': False,
            'message': f'爬虫脚本不存在: {crawler_path}'
        }
    
    try:
        # 在爬虫目录中使用当前 Django 解释器执行，并启用 UTF-8
        result = subprocess.run(
            [sys.executable, '-X', 'utf8', str(crawler_path)],
            cwd=str(crawler_path.parent),
            capture_output=True,
            text=True,
            timeout=180,
        )

        # 无论成功与否，尽量同步生成的图表到静态目录
        copied = sync_charts_to_static()

        if result.returncode == 0:
            return {
                'success': True,
                'message': '天气数据更新成功',
                'output': result.stdout,
                'synced': copied,
            }
        else:
            return {
                'success': False,
                'message': '爬虫执行失败',
                'error': result.stderr,
                'output': result.stdout,
                'synced': copied,
            }

    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'message': '爬虫执行超时'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'执行错误: {str(e)}'
        }


def get_charts_update_time():
    """
    获取图表文件的更新时间
    返回: dict - 包含时间戳和格式化时间
    """
    static_path = get_static_charts_path()
    
    if not static_path.exists():
        return None
    
    # 检查图表文件
    charts = {
        'hourly_temperature_trend': static_path / 'hourly_temperature_trend.png',
        'hourly_weather_table': static_path / 'hourly_weather_table.png',
        'daily_temperature_trend': static_path / 'daily_temperature_trend.png',
        'daily_weather_table': static_path / 'daily_weather_table.png'
    }
    
    latest_time = None
    chart_times = {}
    
    for chart_name, chart_path in charts.items():
        if chart_path.exists():
            mtime = os.path.getmtime(chart_path)
            chart_times[chart_name] = mtime
            if latest_time is None or mtime > latest_time:
                latest_time = mtime
    
    if latest_time:
        dt = datetime.fromtimestamp(latest_time)
        return {
            'timestamp': latest_time,
            'formatted': dt.strftime('%Y-%m-%d %H:%M:%S'),
            'charts': chart_times
        }
    
    return None
