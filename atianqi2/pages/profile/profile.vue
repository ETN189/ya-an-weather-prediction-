<template>
  <view class="profile-page">
    <!-- 头像部分 -->
    <view class="header">
      <image src="/static/头部用户头像.png" class="avatar" />
      <text class="username">用户7678</text>
      <text class="membership-info">到期时间: 2025/12/31</text>
    </view>

    <!-- 功能中心 -->
    <view class="function-center">
      <view class="function-item">
        <image src="/static/我的资产.png" class="function-icon" />
        <text class="function-text">我的资产</text>
      </view>
      <view class="function-item">
        <image src="/static/会员权益.png" class="function-icon" />
        <text class="function-text">会员权益</text>
      </view>
      <view class="function-item">
        <image src="/static/绑定手机.png" class="function-icon" />
        <text class="function-text">绑定手机</text>
      </view>
      <view class="function-item">
        <image src="/static/分享，链接.png" class="function-icon" />
        <text class="function-text">分享链接</text>
      </view>
    </view>

    <!-- 会员特权 -->
    <view class="membership-privileges">
      <view class="privilege-item">
        <image src="/static/变电-停电申请单选中pc.png" class="privilege-icon" />
        <text class="privilege-text">海量版本</text>
      </view>
      <view class="privilege-item">
        <image src="/static/ai-icon.png" class="privilege-icon" />
        <text class="privilege-text">更多AI会员</text>
      </view>
      <view class="privilege-item">
        <image src="/static/会员-更大空间.png" class="privilege-icon" />
        <text class="privilege-text">更大空间</text>
      </view>
      <view class="privilege-item">
        <image src="/static/outbounded.png" class="privilege-icon" />
        <text class="privilege-text">更多格式导出</text>
      </view>
    </view>

    <!-- 退出登录按钮 -->
    <view class="logout-button">
      <button class="logout-btn">退出登录</button>
    </view>
  </view>
</template>

<script>
export default {
  methods: {
    // 退出登录功能可以在这里实现，但当前无互动元素，因此不需要添加任何功能
  }
}
</script>

<style scoped>
/* 个人中心页面样式 */
.profile-page {
  display: flex;
  flex-direction: column;
  padding: 20px;
  background-color: #ffffff;
  min-height: 100vh; /* 保证内容占满整个屏幕 */
  border-radius: 10px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
  max-width: 600px;
  margin: auto;
}

/* 头像和用户名部分 */
.header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;
}

.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  margin-bottom: 10px;
  border: 2px solid #ff6347; /* 给头像加上边框 */
}

.username {
  font-size: 20px;
  font-weight: bold;
  margin-top: 10px;
  color: #333;
}

.membership-info {
  font-size: 14px;
  color: #888;
  margin-top: 5px;
}

/* 功能中心 */
.function-center {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 30px;
}

.function-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.function-icon {
  width: 40px;
  height: 40px;
}

.function-text {
  font-size: 16px;
  color: #333;
}

/* 会员特权部分 */
.membership-privileges {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 30px;
}

.privilege-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.privilege-icon {
  width: 40px;
  height: 40px;
}

.privilege-text {
  font-size: 16px;
  color: #333;
}

/* 退出登录按钮 */
.logout-button {
  display: flex;
  justify-content: center;
}

.logout-btn {
  background-color: #ff6347;
  color: white;
  padding: 10px 20px;
  border-radius: 25px;
  font-size: 16px;
  border: none;
  width: 200px;
}

.logout-btn:hover {
  background-color: #ff4500;
}

/* 响应式设计，适配手机端 */
@media (max-width: 480px) {
  .profile-page {
    padding: 10px;
    margin: 0;
  }

  .function-item, .privilege-item {
    width: 100%;
  }

  .function-icon, .privilege-icon {
    width: 35px;
    height: 35px;
  }

  .function-text, .privilege-text {
    font-size: 14px;
  }

  .logout-btn {
    width: 100%;
  }
}
</style>
