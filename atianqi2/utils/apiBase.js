export function getBaseUrl() {
  try {
    const saved = uni.getStorageSync('BASE_URL');
    if (saved && typeof saved === 'string') return saved;
  } catch (e) {}
  // Default for emulator; change in Settings when running on device
  return 'http://10.0.2.2:8000';
}

export function setBaseUrl(url) {
  if (!url || typeof url !== 'string') return false;
  // normalize: remove trailing slash
  const normalized = url.trim().replace(/\/$/, '');
  if (!/^https?:\/\//i.test(normalized)) return false;
  uni.setStorageSync('BASE_URL', normalized);
  return true;
}
