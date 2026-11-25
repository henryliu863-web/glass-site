// 首页/内页通用交互：Banner 轮播、首页“生产设备”轮播、右侧在线客服浮窗
(function () {
  function slider(root, itemSel, dotSel, interval) {
    if (!root) return;
    var items = root.querySelectorAll(itemSel), dots = root.querySelectorAll(dotSel);
    if (items.length < 2) return;
    var i = 0, timer;
    function show(n) {
      items[i].classList.remove('on'); if (dots[i]) dots[i].classList.remove('on');
      i = (n + items.length) % items.length;
      items[i].classList.add('on'); if (dots[i]) dots[i].classList.add('on');
    }
    function start() { timer = setInterval(function () { show(i + 1); }, interval); }
    dots.forEach(function (d, n) { d.addEventListener('mouseenter', function () { show(n); }); d.addEventListener('click', function () { show(n); }); });
    root.addEventListener('mouseenter', function () { clearInterval(timer); });
    root.addEventListener('mouseleave', start);
    start();
  }
  slider(document.getElementById('banner'), '.slides li', '.num span', 4000);
  slider(document.getElementById('equip'), 'img', '.equip-num span', 5000);

  // ---------------- 智能客服 ----------------
  var chat = document.getElementById('chat');
  if (!chat) return;
  var body = document.getElementById('chat-body'), form = document.getElementById('chat-form'),
      input = document.getElementById('chat-text'), sendBtn = document.getElementById('chat-send'),
      quick = document.getElementById('chat-quick'), humanCard = document.getElementById('chat-human-card');
  var KEY = 'glass_chat_v1', state = { sid: '', msgs: [], open: false }, cfg = null, busy = false;

  function load() { try { var v = JSON.parse(sessionStorage.getItem(KEY)); if (v) state = v; } catch (e) {} }
  function save() { try { sessionStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {} }

  function esc(t) { return t.replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function render(t) {   // 只支持站内链接、加粗、换行，其余全部转义
    var h = esc(t);
    h = h.replace(/\[([^\]]{1,80})\]\((\/(?!\/)[^\s)]{0,200})\)/g, '<a href="$2">$1</a>');
    h = h.replace(/\*\*([^*]{1,200})\*\*/g, '<b>$1</b>');
    h = h.replace(/^\s*[-*]\s+/gm, '• ').replace(/^#{1,6}\s*/gm, '');
    return h.replace(/\n/g, '<br>');
  }
  function add(role, text, persist) {
    var d = document.createElement('div');
    d.className = 'msg ' + role;
    d.innerHTML = '<div class="bubble">' + render(text) + '</div>';
    body.appendChild(d); body.scrollTop = body.scrollHeight;
    if (persist !== false) { state.msgs.push({ r: role, t: text }); if (state.msgs.length > 60) state.msgs.shift(); save(); }
    return d;
  }
  function showQuick() {
    quick.innerHTML = '';
    if (!cfg || state.msgs.some(function (m) { return m.r === 'user'; })) return;
    cfg.quick.forEach(function (q) {
      var b = document.createElement('button'); b.type = 'button'; b.textContent = q;
      b.onclick = function () { send(q); }; quick.appendChild(b);
    });
  }
  function init() {
    body.innerHTML = '';
    if (!state.msgs.length && cfg) add('assistant', cfg.welcome);
    else state.msgs.forEach(function (m) { add(m.r, m.t, false); });
    showQuick();
  }
  function open() {
    chat.hidden = false; state.open = true; save();
    if (cfg) { init(); input.focus(); return; }
    fetch('/api/chat/config').then(function (r) { return r.json(); }).then(function (c) { cfg = c; init(); input.focus(); })
      .catch(function () { cfg = { welcome: '您好，请问有什么可以帮您？', quick: [] }; init(); });
  }
  function close() { chat.hidden = true; state.open = false; save(); }

  function send(text) {
    text = (text || '').trim();
    if (!text || busy) return;
    busy = true; sendBtn.disabled = true; input.value = ''; quick.innerHTML = '';
    add('user', text);
    var typing = add('assistant typing', '', false);
    typing.querySelector('.bubble').innerHTML = '正在输入<span>.</span><span>.</span><span>.</span>';
    fetch('/api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sid: state.sid, message: text }) })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        typing.remove();
        if (d.sid) { state.sid = d.sid; save(); }
        add('assistant', d.reply || d.error || '抱歉，出了点问题，请稍后再试。');
      })
      .catch(function () { typing.remove(); add('assistant', '网络不太稳定，请稍后再试，或点击右上角“转人工”联系我们。', false); })
      .then(function () { busy = false; sendBtn.disabled = false; input.focus(); });
  }

  document.getElementById('chat-open').addEventListener('click', open);
  document.getElementById('chat-close').addEventListener('click', close);
  document.getElementById('chat-human').addEventListener('click', function () { humanCard.hidden = !humanCard.hidden; });
  form.addEventListener('submit', function (e) { e.preventDefault(); send(input.value); });
  input.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) { e.preventDefault(); send(input.value); }
  });
  load();
  if (state.open) open();
})();
