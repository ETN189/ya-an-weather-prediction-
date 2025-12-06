<template>
  <view class="settings-page">
    <view class="card">
      <text class="title">后端服务地址</text>
      <input class="input" v-model="baseUrl" placeholder="http://192.168.x.x:8000 或 https://..." />
      <view class="btns">
        <button class="btn" @click="save">保存</button>
        <button class="btn secondary" @click="test">测试连接</button>
      </view>
      <text class="hint">提示：手机直连电脑请用电脑的局域网IP；模拟器用 http://10.0.2.2:8000。</text>
    </view>
  </view>
</template>

<script>
import { getBaseUrl, setBaseUrl } from '@/utils/apiBase.js';
export default {
  data() {
    return { baseUrl: '' };
  },
  onLoad() {
    this.baseUrl = getBaseUrl();
  },
  methods: {
    save() {
      const ok = setBaseUrl(this.baseUrl);
      if (ok) {
        uni.showToast({ title: '已保存', icon: 'success' });
        setTimeout(() => uni.navigateBack({ delta: 1 }), 500);
      } else {
        uni.showToast({ title: '地址无效，请包含 http(s)://', icon: 'none' });
      }
    },
    test() {
      const url = this.baseUrl && this.baseUrl.trim();
      if (!url) {
        uni.showToast({ title: '请先填写地址', icon: 'none' });
        return;
      }
      uni.request({
        url: `${url.replace(/\/$/, '')}/api/weather-charts/meta`,
        method: 'GET',
        timeout: 8000,
        success: (res) => {
          if (res.statusCode === 200) uni.showToast({ title: '连接成功', icon: 'success' });
          else uni.showToast({ title: `连接失败(${res.statusCode})`, icon: 'none' });
        },
        fail: () => uni.showToast({ title: '无法连接', icon: 'none' }),
      });
    },
  },
};
</script>

<style scoped>
.settings-page { padding: 20px; }
.card { background: #fff; border-radius: 12px; padding: 16px; box-shadow: 0 4px 12px rgba(0,0,0,.06); }
.title { display:block; font-size: 18px; font-weight: 600; margin-bottom: 12px; }
.input { width: 100%; padding: 10px 12px; border: 1px solid #ddd; border-radius: 8px; }
.btns { display: flex; gap: 10px; margin-top: 12px; }
.btn { flex:1; background: #1890ff; color: #fff; border: none; border-radius: 8px; padding: 10px; }
.btn.secondary { background: #f0f0f0; color: #333; }
.hint { display:block; color:#888; font-size:12px; margin-top:10px; }
</style>
