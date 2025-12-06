<template>
  <view class="welcome-container">
    <view class="welcome-card">
      <image class="welcome-logo" src="/static/logo.png" mode="aspectFit"></image>
      <view class="title-container">
        <text class="welcome-title">雅安天气</text>
        <text class="welcome-subtitle">为您提供精准的天气预报服务</text>
      </view>
      
      <view class="checkbox-container">
        <label class="checkbox-label">
          <checkbox class="checkbox" :checked="isChecked" @tap="toggleCheckbox"></checkbox>
          <text class="checkbox-text">我不是机器人</text>
        </label>
      </view>
      
      <button class="enter-button" @click="enterSite">开始体验</button>
    </view>
    <view class="welcome-footer">
      <text class="footer-text">© 2025 雅安天气 All Rights Reserved(示例)</text>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      isChecked: false
    }
  },
  methods: {
    toggleCheckbox() {
      this.isChecked = !this.isChecked;
    },
    enterSite() {
      if (!this.isChecked) {
        uni.showToast({
          title: '请确认您不是机器人',
          icon: 'none',
          duration: 2000
        });
        return;
      }
      
      // 使用 redirectTo 避免返回欢迎页
      uni.redirectTo({
        url: '/pages/index/index'
      });
    }
  }
}
</script>

<style scoped>
.welcome-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #74b9ff, #0984e3);
  padding: 20px;
  box-sizing: border-box;
}

.welcome-card {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 20px;
  padding: 40px 30px;
  width: 90%;
  max-width: 400px;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.welcome-logo {
  width: 100px;
  height: 100px;
  margin: 0 auto 20px;
}

.title-container {
  margin-bottom: 30px;
}

.welcome-title {
  font-size: 28px;
  font-weight: bold;
  color: #2d3436;
  display: block;
}

.welcome-subtitle {
  font-size: 16px;
  color: #636e72;
  margin-top: 10px;
  line-height: 1.5;
  display: block;
}

.checkbox-container {
  margin: 20px 0 30px;
  display: flex;
  justify-content: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.checkbox {
  transform: scale(0.8);
}

.checkbox-text {
  color: #636e72;
  font-size: 14px;
  margin-left: 5px;
}

.enter-button {
  background: linear-gradient(to right, #00b894, #00cec9);
  color: white;
  border: none;
  border-radius: 50px;
  padding: 15px 40px;
  font-size: 18px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 184, 148, 0.3);
}

.enter-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 184, 148, 0.4);
}

.enter-button:active {
  transform: translateY(0);
}

.welcome-footer {
  position: absolute;
  bottom: 20px;
  width: 100%;
  text-align: center;
}

.footer-text {
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
}
</style>