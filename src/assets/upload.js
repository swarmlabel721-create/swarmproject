// 写真アップロード（/upload/ 専用）
(function () {
  var form = document.getElementById('upload-form');
  if (!form) return;
  var status = form.querySelector('.upload-status');
  var fileInput = form.querySelector('input[name=photo]');
  var preview = form.querySelector('.upload-preview');
  var list = document.querySelector('.upload-list');
  var pw = form.querySelector('input[name=password]');
  var resized = null;

  try { pw.value = sessionStorage.getItem('tt-upload-pw') || ''; } catch (e) {}
  form.querySelector('input[name=date]').value = new Date(Date.now() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 10);

  function say(msg, ok) { status.textContent = msg; status.style.color = ok ? 'var(--neon)' : 'var(--pink)'; }

  // 長辺1600pxのJPEGに縮小（容量制限対策・スマホ写真の向きも反映）
  function resize(file) {
    return new Promise(function (resolve, reject) {
      var img = new Image();
      var url = URL.createObjectURL(file);
      img.onload = function () {
        var max = 1600, w = img.naturalWidth, h = img.naturalHeight;
        var k = Math.min(1, max / Math.max(w, h));
        var c = document.createElement('canvas');
        c.width = Math.round(w * k); c.height = Math.round(h * k);
        c.getContext('2d').drawImage(img, 0, 0, c.width, c.height);
        URL.revokeObjectURL(url);
        c.toBlob(function (b) { b ? resolve(b) : reject(new Error('変換に失敗しました')); }, 'image/jpeg', 0.85);
      };
      img.onerror = function () { URL.revokeObjectURL(url); reject(new Error('この形式の写真は読み込めませんでした（JPEGで保存して再度お試しください）')); };
      img.src = url;
    });
  }

  fileInput.addEventListener('change', function () {
    resized = null;
    var f = fileInput.files[0];
    if (!f) { preview.hidden = true; return; }
    say('写真を準備中…', true);
    resize(f).then(function (b) {
      resized = b;
      preview.querySelector('img').src = URL.createObjectURL(b);
      preview.hidden = false;
      say('', true);
    }).catch(function (err) { say(err.message); });
  });

  function post(fd) {
    return fetch('/api/log-upload', { method: 'POST', body: fd }).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (d) {
        if (!r.ok) throw new Error(d.error || ('エラー ' + r.status));
        return d;
      });
    });
  }

  function refresh() {
    fetch('/api/logs').then(function (r) { return r.json(); }).then(function (d) {
      list.innerHTML = '';
      (d.logs || []).forEach(function (l) {
        var li = document.createElement('li');
        var label = document.createElement('span');
        label.textContent = l.date + '  ' + l.title;
        var del = document.createElement('button');
        del.type = 'button'; del.className = 'btn btn-ghost btn-sm'; del.textContent = '削除';
        del.addEventListener('click', function () {
          if (!confirm('「' + l.title + '」を削除しますか？（元に戻せません）')) return;
          var fd = new FormData();
          fd.append('password', pw.value); fd.append('action', 'delete'); fd.append('id', l.id);
          post(fd).then(function () { say('削除しました', true); refresh(); }).catch(function (e) { say(e.message); });
        });
        li.appendChild(label); li.appendChild(del); list.appendChild(li);
      });
      if (!list.children.length) list.innerHTML = '<li class="dim">まだ投稿はありません</li>';
    }).catch(function () {});
  }
  refresh();

  form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    if (!resized) { say('写真の準備ができていません'); return; }
    var btn = form.querySelector('button[type=submit]');
    var fd = new FormData(form);
    fd.set('photo', resized, 'photo.jpg');
    btn.disabled = true; say('送信中…', true);
    post(fd).then(function () {
      try { sessionStorage.setItem('tt-upload-pw', pw.value); } catch (e) {}
      say('アップしました。EARTH LOG に表示されています。', true);
      ['title', 'place', 'body', 'alt'].forEach(function (n) { form.elements[n].value = ''; });
      fileInput.value = ''; resized = null; preview.hidden = true;
      refresh();
    }).catch(function (e) { say(e.message); }).then(function () { btn.disabled = false; });
  });
})();
