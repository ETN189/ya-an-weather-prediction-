<template>
  <view class="weather-detail">
    <view class="header">
      <text>天气详情</text>
    </view>
    
    <view class="content">
      <weather-icon @click="showWeather" />
    </view>
  </view>
</template>

<script>
import weatherIcon from '@/components/weather-icon.vue';

export default {
  components: {
    weatherIcon
  },
  methods: {
    showWeather() {
      uni.showToast({
        title: '当前天气为：晴天 25°C',
        icon: 'none'
      });
    }
  }
}
</script>

<style scoped>
.weather-detail {
  display: flex;
  flex-direction: column;
  padding: 20px;
}

.header {
  font-size: 24px;
  font-weight: bold;
  text-align: center;
  margin-bottom: 20px;
}

.content {
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
