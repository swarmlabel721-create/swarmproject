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
