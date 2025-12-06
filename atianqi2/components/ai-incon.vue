<template>
  <view class="ai-prediction">
    <view class="header">
      <text>AI预测</text>
    </view>

    <view class="content">
      <ai-icon @click="showPrediction" />
    </view>
  </view>
</template>

<script>
import aiIcon from '@/components/ai-icon.vue';

export default {
  components: {
    aiIcon
  },
  methods: {
    showPrediction() {
      uni.showToast({
        title: 'AI预测结果：未来24小时内可能有雨',
        icon: 'none'
      });
    }
  }
}
</script>

<style scoped>
.ai-prediction {
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
