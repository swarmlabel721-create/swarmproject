// モバイルメニューの開閉
(function () {
  var btn = document.querySelector('.nav-toggle');
  var nav = document.getElementById('nav-menu');
  if (!btn || !nav) return;
  btn.addEventListener('click', function () {
    var open = btn.getAttribute('aria-expanded') === 'true';
    btn.setAttribute('aria-expanded', String(!open));
    btn.setAttribute('aria-label', open ? 'メニューを開く' : 'メニューを閉じる');
    document.body.classList.toggle('menu-open', !open);
  });
  document.addEventListener('keydown', function (ev) {
    if (ev.key === 'Escape' && document.body.classList.contains('menu-open')) btn.click();
  });
})();

// EARTH LOG：アップロードされた記録を読み込んで並べる
(function () {
  var lists = document.querySelectorAll('[data-live-logs]');
  if (!lists.length || !window.fetch) return;
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function card(l) {
    var text = String(l.body || '').split(/\n{2,}/).filter(Boolean).map(function (p) {
      return '<p>' + esc(p).replace(/\n/g, '<br>') + '</p>';
    }).join('');
    var el = document.createElement('article');
    el.className = 'log-card';
    el.setAttribute('data-date', l.date || '');
    el.innerHTML =
      '<div class="log-img"><img src="' + esc(l.image) + '" alt="' + esc(l.alt || l.title) + '" loading="lazy"></div>' +
      '<div class="log-body"><p class="meta"><span class="date">' + esc(l.date) + '</span>' +
      (l.place ? '<span class="tag">LOCATION: ' + esc(l.place) + '</span>' : '') + '</p>' +
      '<h3 class="log-title">' + esc(l.title) + '</h3><div class="text">' + text + '</div></div>';
    return el;
  }
  fetch('/api/logs').then(function (r) { return r.ok ? r.json() : { logs: [] }; }).then(function (d) {
    var logs = (d && d.logs) || [];
    if (!logs.length) return;
    lists.forEach(function (list) {
      var cards = Array.prototype.slice.call(list.querySelectorAll('.log-card'));
      logs.forEach(function (l) { cards.push(card(l)); });
      cards.sort(function (a, b) { return (b.getAttribute('data-date') || '').localeCompare(a.getAttribute('data-date') || ''); });
      var limit = parseInt(list.getAttribute('data-limit') || '0', 10);
      if (limit) cards = cards.slice(0, limit);
      list.innerHTML = '';
      cards.forEach(function (c) { list.appendChild(c); });
    });
    var count = document.querySelector('.rec-count .rec-num');
    if (count && document.querySelector('[data-live-logs]:not([data-limit])')) {
      count.textContent = String(document.querySelectorAll('[data-live-logs] .log-card').length).padStart(2, '0');
    }
  }).catch(function () {});
})();
