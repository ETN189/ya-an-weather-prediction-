from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from pathlib import Path
import requests
import re
from datetime import datetime
import subprocess
import time
from django.conf import settings
from django.templatetags.static import static

from .crawler_service import (
    run_weather_crawler,
    get_charts_update_time,
)

print("========== bigdata/views.py 已加载 ==========")

# Create your views here.
def score(request):
    """读取月度天气数据"""
    # 获取项目根目录
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    
    # JSON 文件路径
    json_file_path = BASE_DIR / 'output' / 'scrape_heading_task.json'
    
    # 读取 JSON 文件
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return JsonResponse(data, safe=False)  # safe=False 允许返回列表
    except FileNotFoundError:
        return JsonResponse({'error': '文件未找到'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON 格式错误'}, status=400)


def weather(request):
    """读取天气预报数据"""
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    json_file_path = BASE_DIR / 'output' / 'scrape_heading_task2.json'
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return JsonResponse(data, safe=False)
    except FileNotFoundError:
        return JsonResponse({'error': '文件未找到'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON 格式错误'}, status=400)


def _extract_first_int(text: str):
    if not text:
        return None
    m = re.search(r"-?\d+", str(text))
    return int(m.group(0)) if m else None


def _latest_crawler_output_dir() -> Path:
    # bigdata/views.py -> bigdata -> djangotutorial -> WWW
    www_dir = Path(__file__).resolve().parents[2]
    return www_dir / '爬虫代码' / 'output'


def _load_today_from_crawler():
    """Load today's weather from crawler output and normalize for frontend."""
    out_dir = _latest_crawler_output_dir()

    # Try multiple possible output files in order of preference
    candidates = [
        out_dir / 'yaan_weather.json',
        out_dir / 'scrape_yun_task.json',
        out_dir / 'yaan_hourly_weather.json',
    ]

    raw = None
    for p in candidates:
        if p.exists():
            try:
                with open(p, 'r', encoding='utf-8') as f:
                    raw = json.load(f)
                # prefer files that contain useful daily data
                if raw:
                    break
            except Exception:
                continue

    if raw is None:
        raise FileNotFoundError(f"未找到任何爬虫输出文件: {candidates}")

    # Normalize different possible structures
    today = {}
    timestamp = datetime.now().isoformat(timespec='seconds')

    # Case A: yaan_weather.json is a list of daily dicts
    if isinstance(raw, list) and len(raw) > 0:
        today = raw[0]
        timestamp = today.get('current_time') or timestamp

    # Case B: scrape_yun_task.json with {'daily': [...], 'hourly': [...]} 
    elif isinstance(raw, dict) and 'daily' in raw and isinstance(raw['daily'], list) and len(raw['daily']) > 0:
        today = raw['daily'][0]
        timestamp = today.get('current_time') or raw.get('timestamp') or timestamp

    # Case C: hourly-only structure (list)
    elif isinstance(raw, list) and len(raw) == 0:
        # empty hourly
        today = {}

    else:
        # Unknown structure: try to coerce
        if isinstance(raw, dict):
            # try take first list value
            for v in raw.values():
                if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                    today = v[0]
                    break

    # Extract temperature using several candidate fields
    temp_candidates = [
        today.get('current_hour_temperature') if isinstance(today, dict) else None,
        today.get('current_temp') if isinstance(today, dict) else None,
        today.get('current_temperature') if isinstance(today, dict) else None,
        today.get('current') if isinstance(today, dict) else None,
        today.get('high_temp') if isinstance(today, dict) else None,
        today.get('temperature') if isinstance(today, dict) else None,
    ]

    temp_val = None
    for c in temp_candidates:
        v = _extract_first_int(c)
        if v is not None:
            temp_val = v
            break

    status = None
    winds = None

    if isinstance(today, dict):
        status = today.get('current_hour_weather') or today.get('weather') or today.get('description')
        winds = today.get('wind_direction') or today.get('wind') or today.get('winds') or today.get('wind_level')
        timestamp = today.get('current_time') or today.get('current_time') or timestamp

    # Final fallbacks
    if temp_val is None:
        temp_out = '--'
    else:
        temp_out = temp_val

    if not status:
        status = '未知'
    if not winds:
        winds = '未知'

    return {
        'today_weather': [temp_out, status, winds],
        'source': 'crawler',
        'timestamp': timestamp,
    }


def _ensure_crawled(max_age_minutes: int = 60):
    """Ensure crawler has run recently. If missing or too old, run yun.py.

    Blocks until yun.py finishes (synchronous) to guarantee fresh data
    before serving to index.vue.
    """
    out_dir = _latest_crawler_output_dir()
    json_path = out_dir / 'yaan_weather.json'

    need_run = False
    if not json_path.exists():
        need_run = True
    else:
        try:
            mtime = datetime.fromtimestamp(json_path.stat().st_mtime)
            age = (datetime.now() - mtime).total_seconds() / 60.0
            if age > max_age_minutes:
                need_run = True
        except Exception:
            need_run = True

    if not need_run:
        return

    # Run crawler synchronously
    www_dir = Path(__file__).resolve().parents[2]
    crawler_dir = www_dir / '爬虫代码'
    script = str(crawler_dir / 'yun.py')

    # Use the same Python interpreter as Django server
    try:
        subprocess.run(['python', '-X', 'utf8', script], cwd=str(crawler_dir), check=True)
    except subprocess.CalledProcessError as e:
        # Let caller handle missing data; we do not crash here
        print(f"运行爬虫失败: {e}")


def get_today_wea(request):
    """Endpoint: return today's weather in expected array format.

    Response example:
    {
      "today_weather": [23, "晴天", "东北风3级"],
      "source": "crawler",
      "timestamp": "2025-12-05 10:21:03"
    }
    """
    try:
        # Ensure data is fresh before responding
        _ensure_crawled(max_age_minutes=60)
        data = _load_today_from_crawler()
        resp = JsonResponse(data)
    except FileNotFoundError as e:
        resp = JsonResponse({'error': str(e)}, status=404)
    except Exception as e:
        resp = JsonResponse({'error': f'服务器错误: {str(e)}'}, status=500)

    # Simple CORS for local dev
    resp["Access-Control-Allow-Origin"] = "*"
    resp["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    return resp


def root_api(request):
    """Root handler to support query parameter ?GetTodayWea=true
    so frontend calling http://localhost:8000/?GetTodayWea=true works.
    """
    if request.method == 'OPTIONS':
        r = HttpResponse(status=204)
        r["Access-Control-Allow-Origin"] = "*"
        r["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        r["Access-Control-Allow-Headers"] = "Content-Type"
        return r

    if request.GET.get('GetTodayWea'):
        return get_today_wea(request)

    return JsonResponse({'status': 'ok', 'message': 'use ?GetTodayWea=true or /api/GetTodayWea'})


def _build_chart_urls(request):
    """Build absolute URLs for weather chart images under static/weather_charts.

    Returns a dict with keys matching frontend usage.
    """
    names = {
        'hourly_temperature_trend': 'hourly_temperature_trend.png',
        'hourly_weather_table': 'hourly_weather_table.png',
        'daily_temperature_trend': 'daily_temperature_trend.png',
        'daily_weather_table': 'daily_weather_table.png',
    }
    urls = {}
    for k, filename in names.items():
        rel = static(f'weather_charts/{filename}')  # '/static/weather_charts/xxx.png'
        urls[k] = request.build_absolute_uri(rel)
    return urls


def weather_charts_meta(request):
    """GET: return chart image URLs and last update time.

    Response example:
    {
        "last_update": "2025-12-05 12:30:22",
        "urls": {
            "hourly_temperature_trend": "http://host/static/weather_charts/hourly_temperature_trend.png",
            ...
        },
        "charts_mtime": {"hourly_temperature_trend": 1733380000.0, ...}
    }
    """
    if request.method == 'OPTIONS':
        r = HttpResponse(status=204)
        r["Access-Control-Allow-Origin"] = "*"
        r["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        r["Access-Control-Allow-Headers"] = "Content-Type"
        return r

    meta = get_charts_update_time() or {}
    payload = {
        'last_update': meta.get('formatted'),
        'urls': _build_chart_urls(request),
        'charts_mtime': meta.get('charts', {}),
    }
    resp = JsonResponse(payload)
    resp["Access-Control-Allow-Origin"] = "*"
    return resp


@csrf_exempt
def refresh_weather_charts(request):
    """POST: trigger crawler to regenerate charts, then return updated meta."""
    if request.method == 'OPTIONS':
        r = HttpResponse(status=204)
        r["Access-Control-Allow-Origin"] = "*"
        r["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        r["Access-Control-Allow-Headers"] = "Content-Type"
        return r

    if request.method != 'POST':
        return JsonResponse({'error': '仅支持 POST'}, status=405)

    result = run_weather_crawler()
    meta = get_charts_update_time() or {}
    payload = {
        'result': result,
        'last_update': meta.get('formatted'),
        'urls': _build_chart_urls(request),
        'charts_mtime': meta.get('charts', {}),
    }
    resp = JsonResponse(payload)
    resp["Access-Control-Allow-Origin"] = "*"
    return resp


@csrf_exempt
def ai_prediction(request):
    """AI 预测接口 - 调用阿里通义千问"""
    print(f"========== ai_prediction 被调用, method={request.method} ==========")
    print(f"Request body: {request.body}")
    
    if request.method == 'POST':
        try:
            # 解析请求体中的 JSON 数据
            data = json.loads(request.body)
            user_text = data.get('text', '')
            
            # 阿里通义千问 API 配置
            api_key = "## 请替换为您的阿里云通义千问 API Key ##"
            
            # 通义千问 API 地址
            api_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
            
            # 构建请求头
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            # 构建请求体
            payload = {
                "model": "qwen-turbo",  # 可选: qwen-turbo, qwen-plus, qwen-max
                "input": {
                    "messages": [
                        {
                            "role": "user",
                            "content": user_text
                        }
                    ]
                },
                "parameters": {
                    "result_format": "message"
                }
            }
            
            # 调用阿里通义千问 API
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)
            
            # 记录响应详情用于调试
            print(f"API状态码: {response.status_code}")
            print(f"API响应内容: {response.text}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    # 提取 AI 回复
                    ai_message = result['output']['choices'][0]['message']['content']
                    
                    return JsonResponse({
                        'status': 'success',
                        'message': ai_message
                    })
                except (KeyError, IndexError) as e:
                    return JsonResponse({
                        'error': 'API响应格式异常',
                        'details': str(e),
                        'response': response.text
                    }, status=500)
            else:
                return JsonResponse({
                    'error': f'API 调用失败: {response.status_code}',
                    'details': response.text
                }, status=500)
                
        except json.JSONDecodeError as e:
            return JsonResponse({
                'error': 'JSON 格式错误',
                'details': str(e)
            }, status=400)
        except requests.exceptions.Timeout:
            return JsonResponse({'error': 'API 请求超时'}, status=504)
        except Exception as e:
            return JsonResponse({
                'error': f'服务器错误: {str(e)}',
                'type': type(e).__name__
            }, status=500)
    else:
        return JsonResponse({'error': '仅支持 POST 请求'}, status=405)
