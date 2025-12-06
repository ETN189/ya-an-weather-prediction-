<template>
  <view class="home">
    <!-- 头部部分 -->
    <view class="header">
      <view class="header-content">
        <text class="city-name">雅安</text>
        <text class="weather-title">天气</text>
      </view>
      <view class="header-decoration">
        <view class="decoration-line"></view>
        <view class="decoration-dot"></view>
        <view class="decoration-line"></view>
      </view>
    </view>

    <!-- 今日天气 -->
    <view class="today-weather">
      <image v-if="weatherIcon" :src="weatherIcon" class="weather-icon" mode="aspectFit" />
      <view v-else class="loading-icon">⏳</view>
      <view class="weather-info">
        <text class="temperature">{{ weatherData.temperature }}</text>
        <text class="status">{{ weatherData.status }}</text>
        <text class="winds">{{ weatherData.winds }}</text>
      </view>
    </view>

    <!-- 底部导航栏 -->
    <footer-nav @navigate="navigateTo" />
    
    <!-- 飘动的云朵背景 -->
    <view class="cloud-background">
      <view class="cloud-wrapper cloud-wrapper-1" @click="scatterCloud(1)">
        <image class="cloud cloud-1" src="/static/Cloud.png" mode="aspectFit" :class="{ scattered: scatteredClouds[1] }"></image>
      </view>
      <view class="cloud-wrapper cloud-wrapper-2" @click="scatterCloud(2)">
        <image class="cloud cloud-2" src="/static/0Cloud.png" mode="aspectFit" :class="{ scattered: scatteredClouds[2] }"></image>
      </view>
      <view class="cloud-wrapper cloud-wrapper-3" @click="scatterCloud(3)">
        <image class="cloud cloud-3" src="/static/Cloud.png" mode="aspectFit" :class="{ scattered: scatteredClouds[3] }"></image>
      </view>
      <view class="cloud-wrapper cloud-wrapper-4" @click="scatterCloud(4)">
        <image class="cloud cloud-4" src="/static/0Cloud.png" mode="aspectFit" :class="{ scattered: scatteredClouds[4] }"></image>
      </view>
      <view class="cloud-wrapper cloud-wrapper-5" @click="scatterCloud(5)">
        <image class="cloud cloud-5" src="/static/Cloud.png" mode="aspectFit" :class="{ scattered: scatteredClouds[5] }"></image>
      </view>

      <!-- 彩虹图片 -->
      <image class="rainbow" src="/static/rainbow.png" mode="aspectFit"></image>
    </view>
  </view>
</template>

<script>
import footerNav from '@/components/footer-nav.vue';
import { getBaseUrl } from '@/utils/apiBase.js';

export default {
  components: {
    footerNav,
  },
  data() {
    return {
      weatherData: {
        temperature: '--°C',
        status: '加载中...',
        winds: '风速: --',
      },
      weatherIcon: '', // 默认不显示图标，显示加载状态
      scatteredClouds: {
        1: false,
        2: false,
        3: false,
        4: false,
        5: false,
      },
    };
  },
  methods: {
    navigateTo(page) {
      uni.navigateTo({
        url: `/pages/${page}/${page}`  // 确保路径是正确的
      });
    },
    fetchWeather() {
      console.log('Fetching weather data...');
      
      // 使用后端接口获取天气数据
      uni.request({
        url: `${getBaseUrl()}/?GetTodayWea=true`, // 使用可配置的后端接口地址
        method: 'GET',
        success: (res) => {
          console.log('Weather data fetched:', res);
          if (res.statusCode === 200 && res.data && res.data.today_weather) {
            const data = res.data.today_weather;
            this.weatherData = {
              temperature: `${data[0]}°C`,
              status: data[1],
              winds: `风速: ${data[2]}`,
            };
            this.updateWeatherIcon(data[1]);
          } else {
            // 如果后端返回无效数据，保持加载状态
            console.log('Invalid data received from backend');
          }
        },
        fail: (err) => {
          console.error('Failed to fetch weather data:', err);
          // 请求失败，保持加载状态
        },
      });
    },
    updateWeatherIcon(status) {
      const map = {
        '晴天': '/static/wb-sunny.png',
        '晴': '/static/wb-sunny.png',
        '多云': '/static/Cloudy.png',
        '阴天': '/static/Cloudy.png',
        '阴': '/static/Cloudy.png',
        '小雨': '/static/Rain.png',
        '中雨': '/static/Rain.png',
        '大雨': '/static/Rain.png',
        '阵雨': '/static/Rain.png',
        '雷阵雨': '/static/Rain.png',
        '雨': '/static/Rain.png',
      };
      const fallback = '/static/wb-sunny.png';

      if (!status || typeof status !== 'string') {
        this.weatherIcon = fallback;
        return;
      }

      // 先尝试精确匹配
      if (map[status]) {
        this.weatherIcon = map[status];
        return;
      }
      // 再做包含判断以覆盖更多服务端文案
      const s = status.trim();
      if (s.includes('晴')) this.weatherIcon = '/static/wb-sunny.png';
      else if (s.includes('云') || s.includes('阴')) this.weatherIcon = '/static/Cloudy.png';
      else if (s.includes('雨')) this.weatherIcon = '/static/Rain.png';
      else if (s.includes('风')) this.weatherIcon = '/static/windy.png';
      else this.weatherIcon = fallback;
    },
    scatterCloud(cloudNumber) {
      // 切换云朵的散开状态
      this.scatteredClouds[cloudNumber] = !this.scatteredClouds[cloudNumber];
    },
  },
  onLoad() {
    this.fetchWeather();
  },
  created() {
    console.log('Component created');
  },
};
</script>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: linear-gradient(135deg, #74b9ff, #0984e3);
  padding-bottom: 60px; /* 为底部导航留出空间 */
  box-sizing: border-box;
  position: relative;
  overflow: hidden;
}

/* 头部部分样式 */
.header {
  padding: 20px;
  background-color: rgba(255, 255, 255, 0.2);
  text-align: center;
  backdrop-filter: blur(10px);
  position: relative;
  z-index: 2;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.city-name {
  font-size: 32px;
  font-weight: bold;
  color: white;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  letter-spacing: 2px;
}

.weather-title {
  font-size: 20px;
  color: rgba(255, 255, 255, 0.95);
  margin-top: 5px;
  letter-spacing: 1px;
}

.header-decoration {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 15px;
}

.decoration-line {
  width: 50px;
  height: 2px;
  background: linear-gradient(to right, transparent, rgba(255, 255, 255, 0.7), transparent);
}

.decoration-dot {
  width: 10px;
  height: 10px;
  background-color: rgba(255, 255, 255, 0.7);
  border-radius: 50%;
  margin: 0 12px;
  box-shadow: 0 0 8px rgba(255, 255, 255, 0.5);
}

/* 今日天气样式 */
.today-weather {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  padding: 20px;
  position: relative;
  z-index: 2;
}

.weather-icon {
  width: 120px;
  height: 120px;
  margin-bottom: 20px;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2));
}

.loading-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.weather-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.temperature {
  font-size: 48px;
  font-weight: bold;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.status {
  font-size: 24px;
  color: rgba(255, 255, 255, 0.9);
}

.winds {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.8);
}

/* 云朵背景 */
.cloud-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
  z-index: 3; /* 确保云朵在最上层 */
}

/* 云朵样式 */
.cloud-wrapper {
  position: absolute;
  width: 100px;
  height: 100px;
  cursor: pointer;
  z-index: 4;
}

.cloud-wrapper-1 {
  top: 15%;
  left: -100px;
  animation: float 25s infinite linear;
}

.cloud-wrapper-2 {
  top: 30%;
  left: -100px;
  animation: float 30s infinite linear;
  animation-delay: 5s;
}

.cloud-wrapper-3 {
  top: 45%;
  left: -100px;
  animation: float 35s infinite linear;
  animation-delay: 10s;
}

.cloud-wrapper-4 {
  top: 60%;
  left: -100px;
  animation: float 40s infinite linear;
  animation-delay: 15s;
}

.cloud-wrapper-5 {
  top: 75%;
  left: -100px;
  animation: float 45s infinite linear;
  animation-delay: 20s;
}

.cloud {
  width: 100px;
  height: 100px;
  transition: all 0.3s ease;
  pointer-events: none;
}

.cloud-1 {
  opacity: 0.9;
  filter: hue-rotate(0deg) saturate(300%) brightness(1.3) contrast(120%);
}

.cloud-2 {
  opacity: 0.8;
  filter: hue-rotate(60deg) saturate(300%) brightness(1.2) contrast(120%);
}

.cloud-3 {
  opacity: 0.7;
  filter: hue-rotate(120deg) saturate(300%) brightness(1.1) contrast(120%);
}

.cloud-4 {
  opacity: 0.85;
  filter: hue-rotate(240deg) saturate(300%) brightness(1.25) contrast(120%);
}

.cloud-5 {
  opacity: 0.75;
  filter: hue-rotate(300deg) saturate(300%) brightness(1.15) contrast(120%);
}

.cloud.scattered {
  transform: scale(0.5);
  opacity: 0.3 !important;
}

@keyframes float {
  0% {
    transform: translateX(0) translateY(0);
  }
  25% {
    transform: translateX(25vw) translateY(10px);
  }
  50% {
    transform: translateX(50vw) translateY(-10px);
  }
  75% {
    transform: translateX(75vw) translateY(5px);
  }
  100% {
    transform: translateX(calc(100vw + 100px)) translateY(0);
  }
}

/* 彩虹图片样式 */
.rainbow {
  position: absolute;
  bottom: 20px;
  right: 20px;
  width: 120px;
  height: 120px;
  z-index: 5;
  opacity: 0.9;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5));
  animation: rainbowFloat 3s ease-in-out infinite alternate;
  pointer-events: none;
}

@keyframes rainbowFloat {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(-10px);
  }
}

/* 底部导航栏样式 */
.footer-nav {
  display: flex;
  justify-content: space-around;
  align-items: center;
  background-color: #f5f5f5;
  padding: 10px;
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  z-index: 1000;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
}
</style>
