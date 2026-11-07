// Mobile menu
(function () {
  var btn = document.querySelector('.menu-btn');
  var nav = document.getElementById('site-nav');
  if (btn && nav) {
    btn.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  // Discourage saving photos (right-click, drag and long-press). Note: nothing shown on a website can be fully protected.
  document.addEventListener('contextmenu', function (e) { if (e.target.closest('img, picture, .slide-frame, dialog.lightbox')) e.preventDefault(); });
  document.addEventListener('dragstart', function (e) { if (e.target.tagName === 'IMG') e.preventDefault(); });
  document.querySelectorAll('img').forEach(function (i) { i.setAttribute('draggable', 'false'); });

  // The Google map only loads when the visitor asks for it
  document.querySelectorAll('[data-map-src]').forEach(function (m) {
    var b = m.querySelector('button');
    if (!b) return;
    b.addEventListener('click', function () {
      var f = document.createElement('iframe');
      f.className = 'map'; f.src = m.getAttribute('data-map-src'); f.loading = 'lazy';
      f.title = 'Map showing Breakthrough Centre, 170 Old Main Road, Etete, Groutville';
      f.referrerPolicy = 'strict-origin-when-cross-origin';
      m.replaceWith(f);
    });
  });

  // Moving photo carousels
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var carousels = [];
  document.querySelectorAll('[data-carousel]').forEach(function (c) {
    var track = c.querySelector('.carousel-track');
    var pauseBtn = c.querySelector('.pause');
    var state = { el: c, userPaused: reduce, hover: false, visible: false };
    function step() {
      var s = track.querySelector('.slide');
      return s ? s.getBoundingClientRect().width + parseFloat(getComputedStyle(track).columnGap || 16) : track.clientWidth;
    }
    function atEnd() { return track.scrollLeft + track.clientWidth >= track.scrollWidth - 8; }
    state.next = function () { if (atEnd()) track.scrollTo({ left: 0 }); else track.scrollBy({ left: step() }); };
    function prev() { if (track.scrollLeft <= 8) track.scrollTo({ left: track.scrollWidth }); else track.scrollBy({ left: -step() }); }
    function setPaused(p) {
      state.userPaused = p;
      pauseBtn.setAttribute('aria-label', p ? 'Play the slideshow' : 'Pause the slideshow');
      pauseBtn.innerHTML = p ? '<span aria-hidden="true">&#9654;</span>' : '<span aria-hidden="true">&#10074;&#10074;</span>';
    }
    setPaused(state.userPaused);
    c.querySelector('.next').addEventListener('click', state.next);
    c.querySelector('.prev').addEventListener('click', prev);
    pauseBtn.addEventListener('click', function () { setPaused(!state.userPaused); });
    c.addEventListener('mouseenter', function () { state.hover = true; });
    c.addEventListener('mouseleave', function () { state.hover = false; });
    c.addEventListener('focusin', function () { state.hover = true; });
    c.addEventListener('focusout', function () { state.hover = false; });
    track.addEventListener('touchstart', function () { state.hover = true; }, { passive: true });
    track.addEventListener('touchend', function () { setTimeout(function () { state.hover = false; }, 4000); }, { passive: true });
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (es) { state.visible = es[0].isIntersecting; }, { threshold: 0.3 }).observe(c);
    } else { state.visible = true; }
    carousels.push(state);
  });

  // Photos open in a lightbox
  var dlg = document.querySelector('dialog.lightbox');
  var img = dlg && dlg.querySelector('img');
  var cap = dlg && dlg.querySelector('p');
  if (dlg) {
    document.querySelectorAll('[data-full]').forEach(function (b) {
      b.addEventListener('click', function () {
        var i = b.querySelector('img');
        img.src = b.dataset.full;
        img.alt = i.alt;
        cap.textContent = i.alt;
        dlg.showModal();
      });
    });
    dlg.querySelector('.close').addEventListener('click', function () { dlg.close(); });
    dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });
  }

  if (carousels.length) {
    setInterval(function () {
      if (document.hidden || (dlg && dlg.open)) return;
      carousels.forEach(function (s) { if (!s.userPaused && !s.hover && s.visible) s.next(); });
    }, 4500);
  }
})();
