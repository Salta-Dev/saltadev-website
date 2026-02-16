(() => {
  var key = 'sd_fp';
  if (document.cookie.indexOf(key + '=') !== -1) return;
  var existing = null;
  try {
    existing = localStorage.getItem(key);
  } catch (e) {
    existing = null;
  }
  if (!existing) {
    existing = (window.crypto && window.crypto.randomUUID) ? window.crypto.randomUUID() : String(Date.now()) + String(Math.random()).slice(2);
    try {
      localStorage.setItem(key, existing);
    } catch (e) {
    }
  }
  if (existing) {
    var maxAge = 60 * 60 * 24 * 30;
    document.cookie = key + '=' + existing + '; path=/; max-age=' + maxAge + '; samesite=lax';
  }
})();
