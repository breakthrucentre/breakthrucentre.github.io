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

  // Photo galleries open in a lightbox
  var dlg = document.querySelector('dialog.lightbox');
  if (!dlg) return;
  var img = dlg.querySelector('img');
  var cap = dlg.querySelector('p');
  document.querySelectorAll('.gallery button').forEach(function (b) {
    b.addEventListener('click', function () {
      img.src = b.dataset.full;
      img.alt = b.querySelector('img').alt;
      cap.textContent = b.querySelector('img').alt;
      dlg.showModal();
    });
  });
  dlg.querySelector('.close').addEventListener('click', function () { dlg.close(); });
  dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });
})();
