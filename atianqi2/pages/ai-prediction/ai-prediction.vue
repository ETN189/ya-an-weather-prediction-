<template>
  <view class="ai-prediction">
    <!-- 页面顶部 -->
    <view class="header">
      <text class="header-text">AI预测</text>
    </view>

    <!-- 对话框部分 -->
    <view class="dialog-box">
      <scroll-view ref="scrollView" :scroll-y="true" class="messages">
        <view v-for="(msg, index) in messages" :key="index" class="message">
          <view v-if="msg.type === 'user'" class="user-message">
            <image class="avatar" :src="userAvatar" />
            <text>{{ msg.content }}</text>
          </view>
          <view v-if="msg.type === 'ai'" class="ai-message">
            <image class="avatar" :src="aiAvatar" />
            <text>{{ msg.content }}</text>
          </view>
        </view>
      </scroll-view>
    </view>

    <!-- 文本输入和发送按钮 -->
    <view class="input-box">
      <input v-model="userInput" placeholder="请输入问题..." class="input" />
      <button @click="sendMessage" class="send-button">➤</button>
    </view>
  </view>
</template>

<script>
import { getBaseUrl } from '@/utils/apiBase.js';
export default {
  data() {
    return {
      userInput: "",  // 用户输入的文本
      messages: [],    // 保存对话记录
      userAvatar: '/static/userc1.png',  // 用户头像
      aiAvatar: '/static/weapre1.png'       // AI头像
    };
  },
  methods: {
    // 发送消息
    sendMessage() {
      if (this.userInput.trim() === "") return;  // 如果没有输入内容，不发送

      // 添加用户输入到消息列表
      this.messages.push({
        type: "user",
        content: this.userInput
      });

      // 调用 Django 后端 API 获取 AI 的回复
      this.getAIResponse(this.userInput);

      // 清空输入框
      this.userInput = "";
    },

    // 调用 Django 后端 API 获取 AI 的回复
    async getAIResponse(inputText) {
      try {
        const response = await uni.request({
          url: `${getBaseUrl()}/api/ai-prediction/`,  // Django 后端 URL
          method: 'POST',
          header: {
            'Content-Type': 'application/json',
          },
          data: {
            text: inputText,  // 用户输入的文本
          },
          success: (response) => {
            // 获取 AI 的回复
            const aiMessage = response.data.message;
            // 将 AI 回复加入消息列表
            this.messages.push({
              type: 'ai',
              content: aiMessage
            });

            // 确保滚动条滚动到最新消息
            this.$nextTick(() => {
              const scrollView = this.$refs.scrollView;
              scrollView.scrollTop = scrollView.scrollHeight;
            });
          },
          fail: (error) => {
            console.error('API 请求失败:', error);
            this.messages.push({
              type: 'ai',
              content: "抱歉，我遇到了一些问题。"
            });
          }
        });
      } catch (error) {
        console.error('请求出错:', error);
        this.messages.push({
          type: 'ai',
          content: "抱歉，我遇到了一些问题。"
        });
      }
    }
  }
};
</script>

<style scoped>
.ai-prediction {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-size: cover;
  background-position: center;
  padding-bottom: 60px;  /* 为底部导航栏留空间 */
}

.header {
  background-color: #007aff;  /* 蓝色主题 */
  padding: 15px;
  text-align: center;
  font-size: 24px;
  color: white;
}

.header-text {
  font-size: 28px;
  font-weight: bold;
}

.dialog-box {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.messages {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.message {
  max-width: 80%;
  margin: 5px;
  display: flex;
  align-items: flex-start;
}

.user-message,
.ai-message {
  display: flex;
  align-items: center;
}

.user-message text,
.ai-message text {
  margin-left: 10px;
  padding: 10px;
  border-radius: 10px;
}

.user-message {
  background-color: #f1f1f1;
  align-self: flex-start;
}

.ai-message {
  background-color: #d1f7ff;
  align-self: flex-end;
}

.avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
}

.input-box {
  display: flex;
  align-items: center;
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  background-color: white;
  padding: 10px;
  border-top: 1px solid #ccc;
  z-index: 10;
}

.input {
  flex: 1;
  padding: 10px;
  margin-right: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.send-button {
  background-color: #007aff;
  color: white;
  padding: 10px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.send-button:hover {
  background-color: #005f8e;
}
</style>
