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

  var online = document.getElementById('online');
  if (online) {
    online.querySelector('.online-tab').addEventListener('mouseenter', function () { online.classList.add('open'); });
    online.querySelector('.online-tab').addEventListener('click', function () { online.classList.toggle('open'); });
    online.querySelector('.x').addEventListener('click', function () { online.classList.remove('open'); });
  }
})();
