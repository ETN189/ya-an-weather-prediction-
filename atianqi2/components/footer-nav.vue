<template>
  <view class="footer-nav">
    <view class="nav-item" @click="navigate('weather-detail')">
      <image src="/static/weapre1.png" />
      <text>天气详情</text>
    </view>
    <view class="nav-item" @click="navigate('ai-prediction')">
      <image src="/static/AIpre1.png" />
      <text>AI预测</text>
    </view>
    <view class="nav-item" @click="navigate('profile')">
      <image src="/static/userc1.png" />
      <text>个人页面</text>
    </view>
    <view class="nav-item" @click="navigate('settings')">
      <image src="/static/setting.png" />
      <text>设置</text>
    </view>
  </view>
</template>

<script>
export default {
  methods: {
    // 跳转到指定页面
    navigate(page) {
      uni.navigateTo({
        url: `/pages/${page}/${page}`  // 确保路径是正确的
      });
    }
  }
}
</script>

<style scoped>
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
  z-index: 1000;  /* 保证导航栏在最上层 */
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);  /* 给导航栏添加阴影 */
}

/* 每个导航项的样式 */
.nav-item {
  display: flex;          /* 使用flex布局 */
  flex-direction: column; /* 垂直排列图标和文字 */
  align-items: center;    /* 垂直居中对齐 */
  justify-content: center; /* 垂直居中对齐 */
  text-align: center;
  cursor: pointer;
}

/* 图标样式 */
.nav-item image {
  width: 40px;    /* 控制图标的大小 */
  height: 40px;
  margin-bottom: 5px; /* 控制图标与文字之间的间距 */
}

/* 文字样式 */
.nav-item text {
  font-size: 16px;
  color: #333;
}

/* 鼠标悬停效果 */
.nav-item:hover {
  background-color: #f0f0f0;
  border-radius: 10px;
}

.nav-item:hover image {
  transform: scale(1.1);  /* 鼠标悬停时放大图标 */
  transition: transform 0.3s;
}

.nav-item:hover text {
  color: #ff6347;  /* 鼠标悬停时改变文字颜色 */
  transition: color 0.3s;
}

/* 响应式设计：适配手机屏幕 */
@media (max-width: 480px) {
  .footer-nav {
    padding: 5px;
  }

  .nav-item image {
    width: 30px;
    height: 30px;
  }

  .nav-item text {
    font-size: 14px;
  }
}
</style>
