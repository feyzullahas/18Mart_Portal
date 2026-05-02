// Bu dosya, Vercel sunucusunda artık bulunmayan eski JavaScript (PWA cache) dosyaları istendiğinde otomatik olarak döndürülür.
// Amacı, hata fırlatmak yerine istemcinin (tarayıcının) önbelleğini temizleyip sayfayı yenilemesini sağlamaktır.

var reloadKey = 'portal_auto_reload_fallback';
if (!sessionStorage.getItem(reloadKey)) {
  sessionStorage.setItem(reloadKey, 'true');
  console.warn('Güncel olmayan JS dosyası istendi, sistem yenileniyor...');
  
  var promises = [];
  
  if ('serviceWorker' in navigator) {
    promises.push(navigator.serviceWorker.getRegistrations().then(function(regs) {
      return Promise.all(regs.map(function(reg) { return reg.unregister(); }));
    }).catch(function(){}));
  }
  
  if ('caches' in window) {
    promises.push(caches.keys().then(function(names) {
      return Promise.all(names.map(function(name) { return caches.delete(name); }));
    }).catch(function(){}));
  }
  
  Promise.all(promises).then(function() {
    window.location.reload();
  }).catch(function() {
    setTimeout(function() { window.location.reload(); }, 500);
  });
}
