# 雅安天气可视化与AI预测项目

## 项目简介

本项目由前端 Uni-App 与后端 Django 组成：
- 前端（`atianqi2/`）提供首页天气、天气详情图表、AI预测、用户中心与设置页；
- 后端（`djangotutorial/`）负责天气数据读取、图表资源提供、触发爬虫更新与 AI 预测接口。

前端主要页面路径：
- `pages/welcome/welcome.vue` 开始页面（人机校验+进入引导）
- `pages/index/index.vue` 首页（今日天气与动态背景）
- `pages/weather-detail/weather-detail.vue` 天气详情（24小时/7天图表与更新）
- `pages/ai-prediction/ai-prediction.vue` AI预测（与后端AI接口对话）
- `pages/profile/profile.vue` 用户中心
- `pages/settings/settings.vue` 设置后端地址

## 用户使用教程（详细）

### 1. 启动后端服务（Django）

在后端项目根目录（包含 `manage.py` 的目录）运行：

```powershell
cd "c:\Users\snaleakpro\Desktop\适配手机\djangotutorial"
python manage.py runserver 0.0.0.0:8000
```

- 此命令使后端监听本机所有 IPv4 地址的 `8000` 端口，便于手机或模拟器访问。
- 如端口占用，可改为其它端口，例如 `0.0.0.0:8080`。

### 2. 配置后端网络与安全（settings.py）

请在 `djangotutorial/mysite/settings.py` 或对应 settings 文件中确认以下内容：
- `ALLOWED_HOSTS`：包含你的局域网 IP、域名或使用通配：
   - 示例：`ALLOWED_HOSTS = ["*"]`（开发阶段）或 `ALLOWED_HOSTS = ["127.0.0.1", "localhost", "192.168.x.x"]`
- `STATIC_URL` 与静态目录已用于图表资源（项目已有 `static/weather_charts/`），若需对外提供静态文件，在开发阶段使用 `runserver` 即可；生产环境请配置静态文件服务。
- 可选：如需跨域访问，开发阶段可在视图中设置 `Access-Control-Allow-Origin: *`（当前已有简单 CORS 处理）。

### 3. 设置 AI 预测接口的 API Key（阿里云通义千问）

在后端文件 `djangotutorial/bigdata/views.py` 中定位 AI 接口：

```python
api_key = "## 请替换为您的阿里云通义千问 API Key ##"
```

请将上述占位符替换为你在阿里云控制台申请的有效 Key。例如：

```python
api_key = "sk-xxxxxxxxxxxxxxxxxxxxxxxx"
```

注意：
- 该 Key用于 `POST https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation` 的鉴权；
- 建议在生产环境改为从环境变量或配置文件读取，避免明文存储。

### 4. 配置前端访问后端地址（Settings 页）

前端可通过设置页配置后端地址：
1. 打开应用到 `设置` 页面（`pages/settings/settings.vue`）；
2. 在输入框填写后端地址，例如：
    - 手机直连电脑：`http://192.168.x.x:8000`
    - 安卓模拟器（Android Studio/AVD）：`http://10.0.2.2:8000`
3. 点击“保存”后，前端将通过 `utils/apiBase.js` 记住该地址；
4. 可点击“测试连接”调用 `GET /api/weather-charts/meta` 验证连通。

### 5. 前后端联调验证

- 首页天气：前端调用 `GET /?GetTodayWea=true`，后端 `bigdata.views.get_today_wea` 返回 `[温度, 天气, 风]` 数组结构；
- 天气详情图表：前端调用 `GET /api/weather-charts/meta` 获取图表 URL 与最后更新时间；点击“更新全部图表”调用 `POST /api/weather-charts/refresh` 触发爬虫并刷新图表；
- AI 预测：前端在 `AI预测` 页调用 `POST /api/ai-prediction/`，后端使用通义千问返回对话消息。

### 6. 常见网络与端口问题

- 若手机无法访问电脑后端：确认电脑与手机在同一局域网；关闭或放行防火墙对 `python` 监听的端口（默认 8000）。
- 若端口被占用：更换端口，例如 `0.0.0.0:8080` 并在设置页同步更新为新地址。
- 若图片不更新：图表地址会追加时间戳参数防止缓存，如仍不显示，请检查后端 `static/weather_charts` 是否存在对应图片，以及终端日志中的爬虫与生成流程。

## 自动化更新（可选）

除页面中的“更新全部图表”外，还可手动运行脚本：

```powershell
cd "c:\Users\snaleakpro\Desktop\适配手机\atianqi2"
python scripts\update_weather.py
```

脚本功能：
- 运行 `爬虫代码/yun.py` 获取最新天气数据；
- 生成图表并复制到 `static/weather_charts/`；
- 输出更新进度与结果。

## 项目结构（简）

```
atianqi2/
   pages/               # 前端页面
   components/          # 组件（含底部导航）
   utils/apiBase.js     # 后端地址管理（get/setBaseUrl）
   static/weather_charts/  # 图表输出目录（后端提供URL）

djangotutorial/
   bigdata/views.py     # 天气与图表接口、AI预测接口
   static/weather_charts/  # 后端静态目录（前端所用图表）
   manage.py            # 后端入口
```

## 免责声明

本项目及随附 APK、脚本、配置仅用于学习、测试与演示，不作为正式商用发布版本。为保护使用者与开发者权益，特作如下声明与提示：

- 未备案 APK 与云端证书：
   - 你所使用/分发的 APK 未进行应用商店/工信部门备案与合规审查，且签名采用云端证书（非本地自有签名）。该方式仅适用于内部测试或演示环境，可能不符合各平台上架与国家相关法规的要求。
   - 由于使用云端证书签名，应用的完整性、来源可信度、更新链路安全性需由使用者自行评估与承担。请勿在生产环境或面对公众发布该 APK。

- 数据来源与准确性：
   - 天气数据与图表来自爬虫与外部站点，存在站点变更、采集失败、延迟或数据偏差等情况。本项目不对数据的时效性、准确性与完整性做任何保证。
   - 可视化图表仅供参考，不构成任何决策或承诺。基于数据做出的旅行、生产及商业决策，请自行承担风险。

- 第三方服务与 API Key：
   - AI 预测接口依赖阿里云通义千问等第三方服务。使用者需合法获取并妥善保管 API Key，不得将密钥明文分发或提交至公共仓库。
   - 因第三方服务变更、限流、费用、政策调整或故障导致的不可用或损失，本项目不承担任何责任。

- 安全与合规：
   - 本项目未进行系统化的安全审计与渗透测试。请在生产环境中增加鉴权、权限控制、速率限制、访问日志、异常监控与防火墙策略。
   - 如需在公网部署，请遵守所在地法律法规和平台政策，确保域名备案、隐私政策、用户协议、数据合规与安全加固到位。

- 版权与使用限制：
   - 项目中示例图片、图标与素材仅用于演示，版权归其各自权利人所有。请在商用前替换为自有或可授权素材。
   - 本项目不对任何直接或间接损失负责，包括但不限于收益损失、数据丢失、业务中断等。

- 使用者责任：
   - 使用者在下载、安装、运行、修改或分发本项目及 APK 时，需自行评估并承担合规与安全风险。
   - 若用于教学或研究，请在受控网络与设备进行，避免对第三方站点造成过度访问或影响。

综上，本项目仅供学习与演示，请勿直接在生产或对公众发布。若需正式上线，请进行合规备案、证书与签名规范化、全面安全评估与运维准备，并对所有第三方依赖与数据来源进行严格审查。

## 示例视频

项目运行的示例视频已包含在项目目录中，您可以通过以下路径找到：

```
./example.mp4
```
视频较大不好直接展示
