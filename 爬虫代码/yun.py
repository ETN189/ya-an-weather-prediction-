from botasaurus.request import request, Request
from botasaurus.soupify import soupify
import matplotlib.pyplot as plt
import json
import pandas as pd
import re
import os
import datetime

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

def save_to_json(data, filename="weather_data.json"):
    """保存数据为JSON文件"""
    # 创建output目录
    if not os.path.exists('output'):
        os.makedirs('output')
    
    filepath = f'output/{filename}'
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n📁 JSON数据已保存至: {filepath}")
    return filepath

@request
def scrape_yun_task(request: Request, data):
    """爬取雅安天气数据"""
    response = request.get("https://www.tianqi.com/yaan/")
    soup = soupify(response)
    
    # 创建output目录
    if not os.path.exists('output'):
        os.makedirs('output')
    
    # 调试：保存完整的HTML以便分析
    with open('output/debug_page.html', 'w', encoding='utf-8') as f:
        f.write(str(soup))
    print("\n✅ 已保存网页HTML到 output/debug_page.html 供调试")
    
    result = []
    
    try:
        # 1. 提取当天详细天气信息
        today_data = {'date': '今天'}
        
        # 提取城市名称
        city_element = soup.find('dd', class_='name')
        if city_element:
            h1 = city_element.find('h1')
            if h1:
                city_text = h1.get_text().strip()
                # 移除"天气"两个字
                today_data['city'] = city_text.replace('天气', '')
        
        # 提取日期
        week_element = soup.find('dd', class_='week')
        if week_element:
            today_data['full_date'] = week_element.get_text().strip()
        
        # 提取天气和温度
        weather_element = soup.find('dd', class_='weather')
        if weather_element:
            # 当前温度
            now_p = weather_element.find('p', class_='now')
            if now_p:
                b_tag = now_p.find('b')
                if b_tag:
                    today_data['current_temp'] = b_tag.get_text().strip() + '℃'
            
            # 天气和温度范围
            span_tag = weather_element.find('span')
            if span_tag:
                b_tag = span_tag.find('b')
                if b_tag:
                    today_data['weather'] = b_tag.get_text().strip()
                
                # 提取完整文本并解析温度
                full_text = span_tag.get_text().strip()
                # 例: "晇11 ~ 17℃"
                temp_match = re.search(r'(\d+)\s*~\s*(\d+)', full_text)
                if temp_match:
                    today_data['low_temp'] = temp_match.group(1) + '℃'
                    today_data['high_temp'] = temp_match.group(2) + '℃'
                    today_data['temperature'] = f"{temp_match.group(1)}~{temp_match.group(2)}℃"
        
        # 提取湿度、风向、紫外线
        shidu_element = soup.find('dd', class_='shidu')
        if shidu_element:
            b_tags = shidu_element.find_all('b')
            for b_tag in b_tags:
                text = b_tag.get_text().strip()
                if '湿度' in text:
                    today_data['humidity'] = text.replace('湿度：', '').strip()
                elif '风向' in text:
                    today_data['wind_direction'] = text.replace('风向：', '').strip()
                elif '紫外线' in text:
                    today_data['uv'] = text.replace('紫外线：', '').strip()
        
        # 提取空气质量和PM值
        kongqi_element = soup.find('dd', class_='kongqi')
        if kongqi_element:
            # 空气质量
            h5_tag = kongqi_element.find('h5')
            if h5_tag:
                quality_text = h5_tag.get_text().strip()
                quality_text = quality_text.replace('空气质量：', '').strip()
                today_data['air_quality_level'] = quality_text
            
            # PM值
            h6_tag = kongqi_element.find('h6')
            if h6_tag:
                pm_text = h6_tag.get_text().strip()
                pm_match = re.search(r'PM:\s*(\d+)', pm_text)
                if pm_match:
                    today_data['pm'] = pm_match.group(1)
                    today_data['air_quality_index'] = pm_match.group(1)
        
        # 2. 提取24小时天气数据
        hourly_data = []
        # 获取当前时间
        now = datetime.datetime.now()
        current_hour = now.strftime('%H时')
        current_weather = None
        current_temperature = None
        current_time_str = now.strftime('%Y-%m-%d %H:%M:%S')
        
        # 找到所有24小时数据的div块(共4个,每个包含6小时数据)
        hour_divs = soup.find_all('div', class_='day7')
        
        for hour_div in hour_divs:
            # 跳过7天预报的div
            if 'hide twty_hour' in str(hour_div.get('class', [])):
                continue
            
            # 提取天气状况
            weather_ul = hour_div.find('ul', class_='txt txt2')
            weather_items = weather_ul.find_all('li', class_='w95') if weather_ul else []
            
            # 提取温度数据(在隐藏的div中)
            temp_div = hour_div.find('div', class_=lambda x: x and 'zxt_shuju' in x)
            temp_items = []
            if temp_div:
                temp_ul = temp_div.find('ul')
                if temp_ul:
                    temp_items = temp_ul.find_all('li', class_='w95')
            
            # 提取风向数据(第一个独立的txt ul，不是txt txt2)
            wind_items = []
            txt_uls = hour_div.find_all('ul', class_='txt')
            if len(txt_uls) >= 1:
                # 确保不是txt txt2类的ul
                for ul in txt_uls:
                    classes = ul.get('class', [])
                    if 'txt2' not in classes and 'canvas_hour' not in classes:
                        wind_items = ul.find_all('li', class_='w95')
                        break
            
            # 提取风力数据(带有mgtop5的li元素)
            wind_level_items = []
            if len(txt_uls) >= 2:
                for ul in txt_uls:
                    classes = ul.get('class', [])
                    if 'txt2' not in classes and 'canvas_hour' not in classes:
                        wind_level_candidates = ul.find_all('li', class_='w95 mgtop5')
                        if wind_level_candidates:
                            wind_level_items = wind_level_candidates
                            break
            
            # 提取时间数据(最后一个带canvas_hour的ul)
            time_ul = hour_div.find('ul', class_='txt canvas_hour')
            time_items = time_ul.find_all('li', class_='w95') if time_ul else []
            
            # 调试信息
            print(f"Debug: 找到天气项 {len(weather_items)} 个")
            print(f"Debug: 找到温度项 {len(temp_items)} 个")
            print(f"Debug: 找到风向项 {len(wind_items)} 个")
            print(f"Debug: 找到风力项 {len(wind_level_items)} 个")
            print(f"Debug: 找到时间项 {len(time_items)} 个")
            
            if len(wind_items) > 0:
                print(f"Debug: 前3个风向: {[item.get_text().strip() for item in wind_items[:3]]}")
            if len(wind_level_items) > 0:
                print(f"Debug: 前3个风力: {[item.get_text().strip() for item in wind_level_items[:3]]}")
            
            # 合并数据
            for i in range(len(time_items)):
                hour_info = {}
                
                # 时间
                if i < len(time_items):
                    hour_text = time_items[i].get_text().strip()
                    hour_info['hour'] = hour_text
                    
                    # 检查是否为当前小时
                    if hour_text == current_hour:
                        if i < len(weather_items):
                            current_weather = weather_items[i].get_text().strip()
                        if i < len(temp_items):
                            temp_span = temp_items[i].find('span')
                            if temp_span:
                                current_temperature = temp_span.get_text().strip() + '℃'
                
                # 天气
                if i < len(weather_items):
                    hour_info['weather'] = weather_items[i].get_text().strip()
                
                # 温度
                if i < len(temp_items):
                    temp_span = temp_items[i].find('span')
                    if temp_span:
                        hour_info['temperature'] = temp_span.get_text().strip() + '℃'
                
                # 风向
                if i < len(wind_items):
                    hour_info['wind_direction'] = wind_items[i].get_text().strip()
                
                # 风力
                if i < len(wind_level_items):
                    hour_info['wind_level'] = wind_level_items[i].get_text().strip()
                
                if hour_info:
                    hourly_data.append(hour_info)
        
        print(f"\n✅ 成功提取 {len(hourly_data)} 小时的天气数据")
        
        # 将当前时间的天气信息添加到today_data
        today_data['current_time'] = current_time_str
        if current_weather:
            today_data['current_hour_weather'] = current_weather
        if current_temperature:
            today_data['current_hour_temperature'] = current_temperature
        
        # 3. 提取7天天气预报 - 修复后的版本
        week_div = soup.find('div', class_='day7 hide twty_hour')
        if week_div:
            # 提取日期和星期
            week_ul = week_div.find('ul', class_='week')
            if week_ul:
                day_items = week_ul.find_all('li')
                
                # 提取天气状况
                weather_ul = week_div.find('ul', class_='txt txt2')
                weather_items = weather_ul.find_all('li') if weather_ul else []
                
                # 提取温度数据
                temp_div = week_div.find('div', class_='zxt_shuju')
                temp_items = []
                if temp_div:
                    temp_ul = temp_div.find('ul')
                    if temp_ul:
                        temp_items = temp_ul.find_all('li')
                
                # 提取风向数据
                wind_uls = week_div.find_all('ul', class_='txt')
                wind_items = []
                if len(wind_uls) >= 1:
                    # 第一个txt ul是风向
                    wind_items = wind_uls[0].find_all('li') if wind_uls[0] else []
                
                # 合并数据
                for i in range(len(day_items)):
                    day_data = {}
                    
                    # 日期和星期
                    day_item = day_items[i]
                    date_b = day_item.find('b')
                    week_span = day_item.find('span')
                    
                    if date_b:
                        day_data['date'] = date_b.get_text().strip()
                    if week_span:
                        day_data['week'] = week_span.get_text().strip()
                    
                    # 天气
                    if i < len(weather_items):
                        day_data['weather'] = weather_items[i].get_text().strip()
                    
                    # 温度
                    if i < len(temp_items):
                        temp_item = temp_items[i]
                        high_span = temp_item.find('span')
                        low_b = temp_item.find('b')
                        
                        if high_span and low_b:
                            high_temp = high_span.get_text().strip()
                            low_temp = low_b.get_text().strip()
                            day_data['high_temp'] = high_temp + '℃'
                            day_data['low_temp'] = low_temp + '℃'
                            day_data['temperature'] = f"{low_temp}~{high_temp}℃"
                    
                    # 风向
                    if i < len(wind_items):
                        day_data['wind'] = wind_items[i].get_text().strip()
                    
                    # 添加当天的详细数据
                    if i == 0:  # 第一天通常就是今天
                        for key in ['humidity', 'wind_direction', 'wind_speed', 
                                   'air_quality_index', 'air_quality_level', 'uv', 'pm', 'pressure']:
                            if key in today_data:
                                day_data[key] = today_data[key]
                    
                    if day_data:
                        result.append(day_data)
        
        # 3. 提取生活指数
        index_section = soup.find('div', class_='shzs')
        if index_section:
            index_items = index_section.find_all('li')
            today_data['living_index'] = {}
            
            for item in index_items:
                index_name = item.find('h5')
                index_value = item.find('span')
                index_desc = item.find('p')
                
                if index_name and index_value:
                    name = index_name.get_text().strip()
                    value = index_value.get_text().strip()
                    desc = index_desc.get_text().strip() if index_desc else ''
                    
                    today_data['living_index'][name] = {
                        'value': value,
                        'description': desc
                    }
            
            # 将生活指数添加到第一天的数据中
            if result and 'living_index' in today_data:
                result[0]['living_index'] = today_data['living_index']
        
        # 如果没有获取到7天数据，至少返回当天数据
        if not result and today_data:
            result.append(today_data)
        
        # 确保当前时间的天气信息被添加到第一条记录（当天数据）中
        if result and len(result) > 0:
            if current_weather:
                result[0]['current_hour_weather'] = current_weather
            if current_temperature:
                result[0]['current_hour_temperature'] = current_temperature
            result[0]['current_time'] = current_time_str
        
    except Exception as e:
        print(f"爬取数据时出错: {e}")
        import traceback
        traceback.print_exc()
        # 返回基础示例数据
        result = [{
            'date': '今天',
            'city': '雅安',
            'weather': '数据获取失败',
            'temperature': 'N/A',
            'humidity': 'N/A',
            'wind_direction': 'N/A',
            'air_quality_index': 'N/A',
            'air_quality_level': 'N/A',
            'uv': 'N/A',
            'pm': 'N/A'
        }]
        hourly_data = []

    # 返回字典，包含7天数据和24小时数据
    return {
        'daily': result,
        'hourly': hourly_data
    }

def visualize_hourly_weather(hourly_data):
    """可视化24小时天气数据 - 拆分为单独图表"""
    if not hourly_data or len(hourly_data) < 2:
        print("没有足够的24小时数据进行可视化")
        return
    
    # 创建output目录
    if not os.path.exists('output'):
        os.makedirs('output')
    
    # 提取数据
    hours = []
    temperatures = []
    weathers = []
    
    for item in hourly_data:
        if 'hour' in item and 'temperature' in item:
            hours.append(item['hour'])
            # 提取温度数字
            temp_match = re.search(r'(-?\d+)', item['temperature'])
            if temp_match:
                temperatures.append(int(temp_match.group(1)))
            else:
                temperatures.append(0)
            weathers.append(item.get('weather', '未知'))
    
    if len(hours) < 2:
        print("没有足够的时间点数据")
        return
    
    # 1. 24小时温度趋势图
    plt.figure(figsize=(12, 6))
    x_pos = range(len(hours))
    plt.plot(x_pos, temperatures, marker='o', linewidth=2.5, 
             markersize=6, color='#FF6B6B', label='温度', linestyle='-', alpha=0.8)
    plt.fill_between(x_pos, temperatures, alpha=0.3, color='#FF6B6B')
    plt.xlabel('时间', fontsize=12, fontweight='bold')
    plt.ylabel('温度 (℃)', fontsize=12, fontweight='bold')
    plt.title('雅安24小时温度变化趋势', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.xticks(x_pos[::2], hours[::2], rotation=45, ha='right')
    
    # 添加温度标注(每4个小时显示一次)
    for i in range(0, len(temperatures), 4):
        plt.text(i, temperatures[i], f'{temperatures[i]}℃', 
                ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    # 添加最高最低温点标记
    max_temp_idx = temperatures.index(max(temperatures))
    min_temp_idx = temperatures.index(min(temperatures))
    plt.scatter([max_temp_idx], [temperatures[max_temp_idx]], 
               color='red', s=100, zorder=5, label=f'最高温 {max(temperatures)}℃')
    plt.scatter([min_temp_idx], [temperatures[min_temp_idx]], 
               color='blue', s=100, zorder=5, label=f'最低温 {temperatures[min_temp_idx]}℃')
    plt.legend(loc='best')
    plt.tight_layout()
    plt.savefig('output/hourly_temperature_trend.png', dpi=300, bbox_inches='tight')
    print("\n📊 24小时温度趋势图已保存至: output/hourly_temperature_trend.png")
    plt.close()
    
    # 4. 24小时详细数据表
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('tight')
    ax.axis('off')
    
    # 准备表格数据(每3小时显示一行)
    table_data = []
    for i in range(0, min(len(hourly_data), 24), 3):
        item = hourly_data[i]
        row = [
            item.get('hour', ''),
            item.get('weather', ''),
            item.get('temperature', ''),
            item.get('wind_direction', '')
        ]
        table_data.append(row)
    
    if table_data:
        columns = ['时间', '天气', '温度', '风向']
        table = ax.table(cellText=table_data, colLabels=columns,
                         cellLoc='center', loc='center',
                         colColours=['#4ECDC4']*len(columns))
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        # 在表格上方显示当天湿度
        # 注意：这里没有湿度数据，因为我们处理的是24小时数据
        
        ax.set_title('24小时天气数据概览', fontsize=14, fontweight='bold', pad=20)    
    plt.tight_layout()
    plt.savefig('output/hourly_weather_table.png', dpi=300, bbox_inches='tight')
    print("\n📊 24小时天气数据表已保存至: output/hourly_weather_table.png")
    plt.close()
    
    # 打印统计信息
    print("\n" + "="*50)
    print("24小时天气数据统计报告")
    print("="*50)
    print(f"数据周期: {len(hourly_data)} 小时")
    print(f"平均温度: {sum(temperatures)/len(temperatures):.1f}℃")
    print(f"最高温度: {max(temperatures)}℃ (出现在 {hours[max_temp_idx]})")
    print(f"最低温度: {min(temperatures)}℃ (出现在 {hours[min_temp_idx]})")
    print(f"温差: {max(temperatures) - min(temperatures)}℃")

def visualize_weather_data(data):
    """可视化天气数据 - 拆分为单独图表"""
    if not data:
        print("没有数据可用于可视化")
        return
    
    # 创建output目录
    if not os.path.exists('output'):
        os.makedirs('output')
    
    # 提取7天数据（如果可用）
    plot_data = []
    for item in data:
        if 'temperature' in item and 'high_temp' in item:
            try:
                # 提取最高温度数字
                high_temp_match = re.search(r'(-?\d+)', item['high_temp'])
                if high_temp_match:
                    plot_item = {
                        'date': item['date'],
                        'high_temp': int(high_temp_match.group(1)),
                        'weather': item.get('weather', '未知'),
                        'wind': item.get('wind', item.get('wind_direction', '未知'))
                    }
                    plot_data.append(plot_item)
            except:
                continue
    
    # 如果没有足够的数据点，尝试其他格式
    if len(plot_data) < 2:
        plot_data = []
        for i, item in enumerate(data[:7]):  # 最多取7天
            if 'temperature' in item:
                try:
                    # 尝试从temperature字段提取温度
                    temp_match = re.search(r'(-?\d+)', item['temperature'])
                    if temp_match:
                        plot_item = {
                            'date': item.get('date', f'第{i+1}天'),
                            'high_temp': int(temp_match.group(1)),
                            'weather': item.get('weather', '未知'),
                            'wind': item.get('wind', item.get('wind_direction', '未知'))
                        }
                        plot_data.append(plot_item)
                except:
                    continue
    
    if len(plot_data) < 2:
        print("没有足够的温度数据进行可视化")
        return
    
    # 创建DataFrame
    df = pd.DataFrame(plot_data)
    
    # 1. 温度折线图
    plt.figure(figsize=(12, 6))
    dates = df['date'].tolist()
    temperatures = df['high_temp'].tolist()
    
    plt.plot(range(len(dates)), temperatures, marker='o', linewidth=2, 
             markersize=8, color='#FF6B6B', label='最高温度')
    plt.xlabel('日期', fontsize=12)
    plt.ylabel('温度 (℃)', fontsize=12)
    plt.title('雅安近期温度趋势图', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.xticks(range(len(dates)), dates, rotation=45, ha='right')
    
    # 添加温度标注
    for i, temp in enumerate(temperatures):
        plt.text(i, temp, f'{temp}℃', ha='center', va='bottom', 
                fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('output/daily_temperature_trend.png', dpi=300, bbox_inches='tight')
    print("\n📊 7天温度趋势图已保存至: output/daily_temperature_trend.png")
    plt.close()
    
    # 4. 数据概览表格
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('tight')
    ax.axis('off')
    
    # 准备表格数据
    table_data = []
    for item in data[:5]:  # 只显示前5天数据
        row = [
            item.get('date', ''),
            item.get('weather', ''),
            item.get('temperature', ''),
            item.get('wind_direction', item.get('wind', ''))
        ]
        table_data.append(row)
    
    if table_data:
        columns = ['日期', '天气', '温度', '风向']
        table = ax.table(cellText=table_data, colLabels=columns,
                         cellLoc='center', loc='center',
                         colColours=['#FFD700']*len(columns))
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 1.5)
        
        # 在表格上方显示当天湿度
        if data and len(data) > 0:
            today_humidity = data[0].get('humidity', '未知')
            ax.text(0.5, 0.95, f'当天湿度: {today_humidity}', 
                    transform=ax.transAxes, fontsize=12, fontweight='bold',
                    ha='center', va='top', 
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='#E8F5E9', edgecolor='#4CAF50', linewidth=2))
        
        ax.set_title('天气数据概览', fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig('output/daily_weather_table.png', dpi=300, bbox_inches='tight')
    print("\n📊 7天天气数据表已保存至: output/daily_weather_table.png")
    plt.close()
    
    # 打印统计信息
    if not df.empty:
        print("\n" + "="*50)
        print("天气数据统计报告")
        print("="*50)
        print(f"数据周期: {len(df)} 天")
        print(f"平均最高温度: {df['high_temp'].mean():.1f}℃")
        print(f"最高温度: {df['high_temp'].max()}℃")
        print(f"最低温度: {df['high_temp'].min()}℃")
        
        # 显示当天详细数据
        if data and len(data) > 0:
            today = data[0]
            print(f"\n今天 ({today.get('date', '今天')}) 详细数据:")
            print(f"  城市: {today.get('city', '雅安')}")
            print(f"  天气: {today.get('weather', '未知')}")
            print(f"  温度: {today.get('temperature', '未知')}")
            print(f"  湿度: {today.get('humidity', '未知')}")
            print(f"  风向: {today.get('wind_direction', today.get('wind', '未知'))}")
            print(f"  空气质量: {today.get('air_quality_index', '未知')} ({today.get('air_quality_level', '未知')})")
            print(f"  紫外线: {today.get('uv', '未知')}")
            print(f"  PM: {today.get('pm', '未知')}")
            
            if 'living_index' in today:
                print(f"\n生活指数:")
                for name, info in today['living_index'].items():
                    print(f"  {name}: {info.get('value', '未知')} - {info.get('description', '')}")

if __name__ == "__main__":
    print("🌤️ 开始爬取雅安天气数据...")
    print("="*50)
    
    # 获取天气数据
    weather_data = scrape_yun_task()
    
    if weather_data and 'daily' in weather_data:
        daily_data = weather_data['daily']
        hourly_data = weather_data['hourly']
        
        print(f"\n✅ 成功获取 {len(daily_data)} 条天气数据")
        print(f"✅ 成功获取 {len(hourly_data)} 小时天气数据")
        
        # 打印每日数据预览
        print("\n每日天气数据预览:")
        for i, item in enumerate(daily_data[:3]):  # 显示前3条数据
            print(f"\n第{i+1}条数据:")
            for key, value in item.items():
                if key != 'living_index':
                    print(f"  {key}: {value}")
        
        # 打印小时数据预览
        print("\n24小时天气数据预览 (前5小时):")
        for i, item in enumerate(hourly_data[:5]):
            print(f"  {item.get('hour', '')}: {item.get('weather', '')} {item.get('temperature', '')} {item.get('wind_direction', '')}")
        
        # 保存为JSON文件
        json_file = save_to_json(daily_data, "yaan_weather.json")
        hourly_json_file = save_to_json(hourly_data, "yaan_hourly_weather.json")
        
        # 24小时数据可视化
        if hourly_data:
            print("\n📊 正在生成24小时天气可视化图表...")
            visualize_hourly_weather(hourly_data)
        
        # 每日数据可视化
        print("\n📈 正在生成7天天气可视化图表...")
        visualize_weather_data(daily_data)
        
        print("\n✨ 所有任务完成!")
        print(f"📁 每日数据JSON: {json_file}")
        print(f"📁 小时数据JSON: {hourly_json_file}")
        print("📊 24小时可视化: output/hourly_weather_visualization.png")
        print("📈 7天可视化: output/weather_visualization.png")
    else:
        print("❌ 未获取到数据")