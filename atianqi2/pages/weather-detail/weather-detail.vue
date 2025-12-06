<template>
  <view class="weather-detail">
    <!-- 页面标题与更新状态 -->
    <view class="header">
      <text class="title">🌤️ 雅安天气数据可视化</text>
      <view class="subtitle">
        <text>最后更新：{{ lastUpdateTime }}</text>
        <text class="data-source">数据来源：本地爬虫分析</text>
      </view>
    </view>

    <!-- 图表导航栏 -->
    <scroll-view scroll-x class="chart-nav">
      <view 
        v-for="(tab, index) in tabs" 
        :key="index"
        class="nav-item"
        :class="{ active: activeTab === index }"
        @click="switchTab(index)"
      >
        <text>{{ tab.name }}</text>
      </view>
    </scroll-view>

    <!-- 图表展示区域 -->
    <view class="chart-container">
      <!-- 24小时数据标签页 -->
      <view v-if="activeTab === 0" class="tab-content">
        <view class="chart-card">
          <text class="chart-title">📈 雅安24小时温度变化趋势</text>
          <image 
            :src="chartUrls.hourly_temperature_trend" 
            mode="widthFix" 
            class="chart-image"
            @load="onImageLoad('hourlyTrend')"
            @error="onImageError('hourlyTrend')"
          />
          <text class="chart-desc">过去24小时温度折线图，帮助您了解全天温差变化。</text>
        </view>
        <view class="chart-card">
          <text class="chart-title">📋 24小时天气数据概览</text>
          <image 
            :src="chartUrls.hourly_weather_table" 
            mode="widthFix" 
            class="chart-image"
            @load="onImageLoad('hourlyTable')"
          />
          <text class="chart-desc">逐小时天气、温度、风向的详细数据表格。</text>
        </view>
      </view>

      <!-- 7天预报数据标签页 -->
      <view v-if="activeTab === 1" class="tab-content">
        <view class="chart-card">
          <text class="chart-title">📊 雅安近期温度趋势图（7天）</text>
          <image 
            :src="chartUrls.daily_temperature_trend" 
            mode="widthFix" 
            class="chart-image"
            @load="onImageLoad('dailyTrend')"
          />
          <text class="chart-desc">未来7天最高最低温度预测趋势，便于规划出行。</text>
        </view>
        <view class="chart-card">
          <text class="chart-title">🗓️ 7天天气数据概览</text>
          <image 
            :src="chartUrls.daily_weather_table" 
            mode="widthFix" 
            class="chart-image"
            @load="onImageLoad('dailyTable')"
          />
          <text class="chart-desc">一周内的天气、温度范围、风向等综合信息表。</text>
        </view>
      </view>

      <!-- 解读与说明标签页 -->
      <view v-if="activeTab === 2" class="tab-content">
        <view class="info-card">
          <text class="info-title">📖 图表解读指南</text>
          <view class="info-section">
            <text class="info-subtitle">温度趋势图</text>
            <text class="info-text">• 折线图展示温度随时间的变化，峰值代表最高温，谷值代表最低温。</text>
            <text class="info-text">• 24小时图反映日内温差，7天图帮助把握未来一周气候趋势。</text>
          </view>
          <view class="info-section">
            <text class="info-subtitle">数据概览表</text>
            <text class="info-text">• 提供精确的数值数据，如具体温度、风速等级和天气状况。</text>
            <text class="info-text">• 表格形式便于对比不同时段或日期的天气差异。</text>
          </view>
        </view>
        <view class="info-card">
          <text class="info-title">🔄 如何更新图表？</text>
          <text class="info-text">点击下方更新全部图表</text>
        </view>
      </view>
    </view>

    <!-- 底部操作栏 -->
    <view class="footer-actions">
      <button class="action-btn" @click="saveImage(activeTab)">
        💾 保存当前图表
      </button>
      <button class="action-btn primary" @click="refreshAllCharts">
        🔄 更新全部图表
      </button>
    </view>

    <!-- 加载状态 -->
    <view v-if="loading" class="loading-overlay">
      <text>正在加载可视化图表...</text>
    </view>
  </view>
</template>

<script>
import { getBaseUrl } from '@/utils/apiBase.js';
export default {
  data() {
    return {
      activeTab: 0, // 当前选中的标签页：0-24小时，1-7天，2-解读
      lastUpdateTime: '未更新',
      loading: false,
      tabs: [
        { name: '24小时趋势' },
        { name: '7天预报' },
        { name: '图表解读' }
      ],
      imageStatus: {
        hourlyTrend: false,
        hourlyTable: false,
        dailyTrend: false,
        dailyTable: false
      },
      chartUrls: {
        hourly_temperature_trend: '',
        hourly_weather_table: '',
        daily_temperature_trend: '',
        daily_weather_table: ''
      }
    };
  },
  onLoad() {
    this.fetchChartsMeta();
  },
  methods: {
    // 切换标签页
    switchTab(index) {
      this.activeTab = index;
    },

    // 从后端获取图表URL与最后更新时间
    fetchChartsMeta() {
      this.loading = true;
      uni.request({
        url: `${getBaseUrl()}/api/weather-charts/meta`,
        method: 'GET',
        success: (res) => {
          if (res.statusCode === 200 && res.data) {
            const { urls, last_update } = res.data;
            const ts = Date.now();
            if (urls) {
              this.chartUrls = {
                hourly_temperature_trend: `${urls.hourly_temperature_trend}?v=${ts}`,
                hourly_weather_table: `${urls.hourly_weather_table}?v=${ts}`,
                daily_temperature_trend: `${urls.daily_temperature_trend}?v=${ts}`,
                daily_weather_table: `${urls.daily_weather_table}?v=${ts}`,
              };
            }
            this.lastUpdateTime = last_update || '未知';
          } else {
            uni.showToast({ title: '获取图表信息失败', icon: 'none' });
          }
        },
        fail: () => {
          uni.showToast({ title: '服务器不可用', icon: 'none' });
        },
        complete: () => {
          this.loading = false;
        }
      });
    },

    // 图片加载成功
    onImageLoad(imgName) {
      console.log(`${imgName} 图表加载成功`);
      this.imageStatus[imgName] = true;
    },

    // 图片加载失败
    onImageError(imgName) {
      console.error(`${imgName} 图表加载失败，请检查路径`);
      uni.showToast({
        title: `图表加载失败`,
        icon: 'none'
      });
    },

    // 刷新页面（从后端重新拉取）
    refreshPage() {
      this.fetchChartsMeta();
    },

    // 保存当前显示的图片
    saveImage(tabIndex) {
      let imageName = '';
      if (tabIndex === 0) imageName = '雅安24小时天气图表';
      else if (tabIndex === 1) imageName = '雅安7天天气预报图表';
      
      uni.showModal({
        title: '保存图表',
        content: `是否保存${imageName}到本地？`,
        success: (res) => {
          if (res.confirm) {
            // 在实际应用中，这里可以实现真正的图片保存功能
            uni.showToast({
              title: '已保存（示例功能）',
              icon: 'success'
            });
          }
        }
      });
    },

    // 更新全部图表（调用后端触发爬虫）
    refreshAllCharts() {
      uni.showModal({
        title: '更新图表数据',
        content: '将调用后端更新图表，可能需要一些时间。是否继续？',
        confirmText: '立即更新',
        cancelText: '取消',
        success: (res) => {
          if (res.confirm) {
            this.startAutoUpdate();
          }
        }
      });
    },

    // 开始自动更新流程
    startAutoUpdate() {
      this.loading = true;
      uni.showToast({ title: '开始更新...', icon: 'loading', duration: 10000 });

      uni.request({
        url: `${getBaseUrl()}/api/weather-charts/refresh`,
        method: 'POST',
        header: { 'Content-Type': 'application/json' },
        success: (res) => {
          if (res.statusCode === 200 && res.data) {
            const { urls, last_update, result } = res.data;
            const ts = Date.now();
            if (urls) {
              this.chartUrls = {
                hourly_temperature_trend: `${urls.hourly_temperature_trend}?v=${ts}`,
                hourly_weather_table: `${urls.hourly_weather_table}?v=${ts}`,
                daily_temperature_trend: `${urls.daily_temperature_trend}?v=${ts}`,
                daily_weather_table: `${urls.daily_weather_table}?v=${ts}`,
              };
            }
            this.lastUpdateTime = last_update || this.lastUpdateTime;
            const ok = result && result.success;
            uni.showModal({
              title: ok ? '更新完成' : '更新失败',
              content: ok ? '图表已更新至最新状态！' : (result && (result.message || result.error)) || '未知错误',
              showCancel: false,
              confirmText: '确定',
              success: () => this.refreshPage()
            });
          } else {
            uni.showToast({ title: '更新失败', icon: 'none' });
          }
        },
        fail: () => {
          uni.showToast({ title: '服务器不可用', icon: 'none' });
        },
        complete: () => {
          this.loading = false;
        }
      });
    }
  }
};
</script>

<style scoped>
.weather-detail {
  min-height: 100vh;
  background: linear-gradient(180deg, #f8fdff 0%, #f0f9ff 100%);
  padding-bottom: 120rpx;
}

/* 头部样式 */
.header {
  padding: 40rpx 30rpx 30rpx;
  background: white;
  border-bottom: 1rpx solid #eaeff5;
}
.title {
  display: block;
  font-size: 44rpx;
  font-weight: bold;
  color: #1890ff;
  margin-bottom: 15rpx;
}
.subtitle {
  display: flex;
  justify-content: space-between;
  font-size: 26rpx;
  color: #666;
}
.data-source {
  color: #52c41a;
  font-weight: 500;
}

/* 图表导航栏 */
.chart-nav {
  white-space: nowrap;
  background: white;
  padding: 20rpx 0;
  border-bottom: 1rpx solid #eaeff5;
}
.nav-item {
  display: inline-block;
  padding: 20rpx 40rpx;
  margin: 0 15rpx;
  border-radius: 50rpx;
  font-size: 30rpx;
  color: #666;
  transition: all 0.3s;
}
.nav-item.active {
  background: #1890ff;
  color: white;
  font-weight: bold;
  box-shadow: 0 6rpx 20rpx rgba(24, 144, 255, 0.3);
}

/* 图表容器 */
.chart-container {
  padding: 30rpx;
}
.tab-content {
  animation: fadeIn 0.5s ease;
}

/* 图表卡片 */
.chart-card {
  background: white;
  border-radius: 32rpx;
  padding: 40rpx 35rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 10rpx 40rpx rgba(24, 144, 255, 0.08);
  border: 1rpx solid #f0f7ff;
}
.chart-title {
  display: block;
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 30rpx;
  padding-left: 20rpx;
  border-left: 8rpx solid #1890ff;
}
.chart-image {
  width: 100%;
  border-radius: 20rpx;
  margin-bottom: 25rpx;
  border: 1rpx solid #e8f4ff;
}
.chart-desc {
  display: block;
  font-size: 28rpx;
  line-height: 1.6;
  color: #555;
  padding: 20rpx;
  background: #f8fbff;
  border-radius: 16rpx;
}

/* 解读信息卡片 */
.info-card {
  background: white;
  border-radius: 32rpx;
  padding: 40rpx 35rpx;
  margin-bottom: 30rpx;
}
.info-title {
  display: block;
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 35rpx;
}
.info-section {
  margin-bottom: 40rpx;
}
.info-subtitle {
  display: block;
  font-size: 32rpx;
  font-weight: 600;
  color: #1890ff;
  margin-bottom: 20rpx;
}
.info-text {
  display: block;
  font-size: 28rpx;
  line-height: 1.8;
  color: #444;
  margin-bottom: 15rpx;
  padding-left: 20rpx;
}

/* 按钮样式 */
.refresh-btn {
  width: 100%;
  height: 90rpx;
  background: linear-gradient(135deg, #36cfc9, #1890ff);
  color: white;
  border: none;
  border-radius: 50rpx;
  font-size: 32rpx;
  font-weight: 500;
  margin-top: 30rpx;
}

/* 底部操作栏 */
.footer-actions {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.95);
  padding: 20rpx 30rpx;
  display: flex;
  justify-content: space-between;
  border-top: 1rpx solid #eaeff5;
  backdrop-filter: blur(10rpx);
}
.action-btn {
  flex: 1;
  height: 90rpx;
  margin: 0 15rpx;
  border-radius: 50rpx;
  font-size: 30rpx;
  background: #f0f7ff;
  color: #1890ff;
  border: 1rpx solid #d1e8ff;
}
.action-btn.primary {
  background: linear-gradient(135deg, #1890ff, #096dd9);
  color: white;
  border: none;
  box-shadow: 0 6rpx 25rpx rgba(24, 144, 255, 0.3);
}

/* 加载状态 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 34rpx;
  color: #1890ff;
}

/* 动画 */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20rpx); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
