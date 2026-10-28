(() => {
  const root = document.documentElement;
  root.classList.add('js');
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (_) { return null; } },
    set(k, v) { try { v === null ? localStorage.removeItem(k) : localStorage.setItem(k, v); } catch (_) {} },
  };

  // Theme: the button names the theme it switches to.
  const themeButtons = [...document.querySelectorAll('.ftheme')];
  const darkMedia = matchMedia('(prefers-color-scheme: dark)');
  const isDark = () => root.dataset.theme ? root.dataset.theme === 'dark' : darkMedia.matches;

  // Each screenshot is stored once and shared by every place that shows it. A screen with a dark
  // screenshot shows it in the dark theme.
  const images = JSON.parse(document.getElementById('flow-images').textContent);
  const fillImages = (el) => el.querySelectorAll('img[data-img]').forEach((img) => {
    img.src = images[(isDark() && img.dataset.imgDark) || img.dataset.img];
  });
  const paintTheme = () => {
    themeButtons.forEach((b) => { b.textContent = isDark() ? 'Light' : 'Dark'; b.setAttribute('aria-pressed', isDark()); });
    fillImages(document);
  };
  if (store.get('show-me-theme')) root.dataset.theme = store.get('show-me-theme');
  paintTheme();
  darkMedia.addEventListener('change', paintTheme);
  themeButtons.forEach((b) => b.addEventListener('click', () => {
    root.dataset.theme = isDark() ? 'light' : 'dark';
    store.set('show-me-theme', root.dataset.theme);
    paintTheme();
  }));

  const dlg = document.querySelector('.fover');
  const overlayCheck = dlg.querySelector('.fobar .review');
  let open = null;
  const back = [];

  const sections = [...document.querySelectorAll('.flowsec')];
  const flows = sections.map((sec) => {
    const data = JSON.parse(sec.querySelector('.fdata').textContent);
    const map = sec.querySelector('.fmap'), size = sec.querySelector('.fsize'), stage = sec.querySelector('.stage');
    const W = parseFloat(stage.style.width), H = parseFloat(stage.style.height);
    const f = { sec, data, map, size, stage, W, H, zoom: 1 };
    f.key = (id) => 'show-me-flow:' + data.id + ':' + id;
    f.reviewed = (id) => store.get(f.key(id)) === data.states[id].fp;
    return f;
  });

  // ---------- review marks ----------
  function paintReviews(f) {
    const screens = Object.keys(f.data.states).filter((id) => !f.data.states[id].decision);
    let done = 0;
    screens.forEach((id) => {
      const on = f.reviewed(id);
      if (on) done++;
      f.sec.querySelectorAll('[data-review="' + CSS.escape(id) + '"]').forEach((c) => { c.checked = on; });
      f.sec.querySelectorAll('.fnode[data-id="' + CSS.escape(id) + '"]').forEach((n) => n.classList.toggle('reviewed', on));
    });
    f.sec.querySelector('.fcount').textContent = 'Reviewed ' + done + ' / ' + screens.length;
    if (open && open.f === f && !f.data.states[open.id].decision) overlayCheck.checked = f.reviewed(open.id);
  }
  function setReview(f, id, on) { store.set(f.key(id), on ? f.data.states[id].fp : null); paintReviews(f); }

  // ---------- zoom and pan ----------
  function setZoom(f, z, ax, ay) {
    z = Math.max(0.2, Math.min(2, z));
    const m = f.map, px = ax ?? m.clientWidth / 2, py = ay ?? m.clientHeight / 2;
    const cx = (m.scrollLeft + px) / f.zoom, cy = (m.scrollTop + py) / f.zoom;
    f.zoom = z;
    f.stage.style.transform = 'scale(' + z + ')';
    f.size.style.width = f.W * z + 'px';
    f.size.style.height = f.H * z + 'px';
    m.scrollLeft = cx * z - px;
    m.scrollTop = cy * z - py;
    f.sec.querySelector('.zoom output').textContent = Math.round(z * 100) + '%';
  }
  const fitZoom = (f) => Math.min(1, (f.map.clientWidth - 4) / f.W, (innerHeight * 0.72) / f.H);

  flows.forEach((f) => {
    f.sec.querySelectorAll('[data-zoom]').forEach((b) => b.addEventListener('click', () => {
      const v = b.dataset.zoom;
      setZoom(f, v === 'fit' ? fitZoom(f) : Math.round((f.zoom + v * 0.1) * 10) / 10);
    }));
    f.map.addEventListener('wheel', (ev) => {
      if (!ev.ctrlKey && !ev.metaKey) return;
      ev.preventDefault();
      const r = f.map.getBoundingClientRect();
      setZoom(f, f.zoom * (ev.deltaY < 0 ? 1.1 : 0.9), ev.clientX - r.left, ev.clientY - r.top);
    }, { passive: false });
    let drag = null;
    f.map.addEventListener('pointerdown', (ev) => {
      if (ev.target.closest('.fnode,.fdec,button,input') || ev.button !== 0) return;
      drag = { x: ev.clientX, y: ev.clientY, l: f.map.scrollLeft, t: f.map.scrollTop };
      f.map.setPointerCapture(ev.pointerId);
      f.map.classList.add('dragging');
    });
    f.map.addEventListener('pointermove', (ev) => {
      if (!drag) return;
      f.map.scrollLeft = drag.l - (ev.clientX - drag.x);
      f.map.scrollTop = drag.t - (ev.clientY - drag.y);
    });
    const stop = () => { drag = null; f.map.classList.remove('dragging'); };
    f.map.addEventListener('pointerup', stop);
    f.map.addEventListener('pointercancel', stop);
    f.sec.addEventListener('change', (ev) => {
      const c = ev.target.closest('[data-review]');
      if (c) setReview(f, c.dataset.review, c.checked);
    });
    f.sec.addEventListener('click', (ev) => {
      if (ev.target.closest('input')) return;
      const t = ev.target.closest('.fnode,.fdec,[data-open]');
      if (t) openState(f, t.dataset.id || t.dataset.open);
    });
    f.sec.addEventListener('keydown', (ev) => {
      const n = ev.target.closest('.fnode');
      if (n && !ev.target.closest('input') && (ev.key === 'Enter' || ev.key === ' ')) { ev.preventDefault(); openState(f, n.dataset.id); }
    });
    paintReviews(f);
  });

  // ---------- picker ----------
  const picker = document.querySelector('.fpick select');
  let current = flows[0];
  function showFlow(i) {
    current = flows[i];
    flows.forEach((f, j) => { f.sec.hidden = j !== i; });
    if (picker) picker.value = String(i);
    if (!current.fitted) { current.fitted = true; setZoom(current, current.W > current.map.clientWidth ? Math.max(0.4, fitZoom(current)) : 1, 0, 0); }
  }
  if (picker) picker.addEventListener('change', () => showFlow(Number(picker.value)));

  // ---------- path from the start ----------
  function pathTo(f, id) {
    const prev = { [f.data.start]: null }, queue = [f.data.start];
    while (queue.length) {
      const v = queue.shift();
      if (v === id) break;
      f.data.links.forEach((l, n) => { if (l.from === v && !(l.to in prev)) { prev[l.to] = n; queue.push(l.to); } });
    }
    const used = new Set();
    for (let v = id; prev[v] != null; v = f.data.links[prev[v]].from) used.add(prev[v]);
    return used;
  }
  function paintPath(f, id) {
    const used = pathTo(f, id), steps = new Set([id]);
    used.forEach((n) => { steps.add(f.data.links[n].from); });
    const linkEls = [...f.sec.querySelectorAll('.link')], labelEls = [...f.sec.querySelectorAll('.llbl')];
    linkEls.forEach((el, n) => el.classList.toggle('onpath', used.has(n)));
    labelEls.forEach((el, n) => el.classList.toggle('onpath', used.has(n)));
    f.sec.querySelectorAll('.fnode,.fdec').forEach((el) => {
      el.classList.toggle('sel', el.dataset.id === id);
      el.classList.toggle('onpath', steps.has(el.dataset.id) && el.dataset.id !== id);
    });
  }

  // ---------- full-size view ----------
  const button = (f, id, text, cls) => {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = cls || '';
    b.textContent = text;
    b.addEventListener('click', () => openState(f, id, 'step'));
    return b;
  };
  // how: 'map' starts a new trail, 'step' adds to it, 'back' walks it back.
  function openState(f, id, how = 'map') {
    const s = f.data.states[id];
    if (!s) return;
    if (how === 'step' && open) back.push(open.id);
    if (how === 'map') back.length = 0;
    open = { f, id };
    dlg.querySelector('h2').textContent = s.decision ? 'Decision: ' + s.title : s.title;
    dlg.querySelector('.fosub').textContent = s.sub;
    dlg.querySelector('.fonote').textContent = s.note;
    overlayCheck.hidden = s.decision;
    overlayCheck.dataset.review = id;
    overlayCheck.checked = !s.decision && f.reviewed(id);
    overlayCheck.setAttribute('aria-label', 'Reviewed: ' + s.title);

    const inn = dlg.querySelector('.foin');
    inn.replaceChildren();
    const incoming = f.data.links.filter((l) => l.to === id);
    if (incoming.length) {
      const lab = document.createElement('span');
      lab.textContent = 'Comes from';
      inn.append(lab);
      incoming.forEach((l) => inn.append(button(f, l.from, '← ' + f.data.states[l.from].title + ' · ' + l.label, l.error ? 'error' : '')));
    }

    const box = dlg.querySelector('.foscreen');
    const frame = f.sec.dataset.frame;
    box.className = 'foscreen ' + (s.decision ? 'decision' : 'frame-' + frame);
    box.replaceChildren();
    if (s.decision) {
      box.style.maxWidth = '';
      const q = document.createElement('p');
      q.textContent = s.title;
      box.append(q);
    } else {
      const node = f.sec.querySelector('.fnode[data-id="' + CSS.escape(id) + '"]');
      box.style.maxWidth = node.dataset.width + 'px';
      const inner = document.createElement('div');
      inner.className = 'foinner';
      inner.style.width = node.dataset.width + 'px';
      inner.innerHTML = node.querySelector('.scale').innerHTML;
      box.append(inner);
      fillImages(box);
    }

    const out = dlg.querySelector('.foout');
    out.replaceChildren();
    if (back.length) {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'plain';
      b.textContent = '← Back to ' + f.data.states[back[back.length - 1]].title;
      b.addEventListener('click', () => openState(f, back.pop(), 'back'));
      out.append(b);
    }
    const spacer = document.createElement('span');
    spacer.className = 'spacer';
    out.append(spacer);
    f.data.links.filter((l) => l.from === id).forEach((l) => {
      const b = button(f, l.to, l.label + ' → ' + f.data.states[l.to].title, 'fwd' + (l.error ? ' error' : ''));
      out.append(b);
    });
    paintPath(f, id);
    if (!dlg.open) dlg.showModal();
    fitScreen();
    dlg.scrollTop = 0;
    try { history.replaceState(null, '', '#' + encodeURIComponent(f.data.id) + '/' + encodeURIComponent(id)); } catch (_) {}
  }
  // Every screen is drawn at its own width, then scaled to fit the view. A click on a scaled screen
  // shows it at its real width, scrolling inside the view; a second click fits it again.
  const screenBox = dlg.querySelector('.foscreen');
  function fitScreen() {
    const inner = screenBox.querySelector('.foinner');
    if (!inner) return;
    const scale = Math.min(1, screenBox.clientWidth / parseFloat(inner.style.width));
    const actual = screenBox.classList.contains('actual');
    inner.style.zoom = actual ? 1 : scale;
    screenBox.classList.toggle('zoomable', scale < 1);
  }
  screenBox.addEventListener('click', () => {
    if (!screenBox.classList.contains('zoomable')) return;
    screenBox.classList.toggle('actual');
    fitScreen();
  });
  addEventListener('resize', () => { if (dlg.open) fitScreen(); });
  overlayCheck.addEventListener('change', () => setReview(open.f, open.id, overlayCheck.checked));
  dlg.querySelector('.fclose').addEventListener('click', () => dlg.close());
  dlg.addEventListener('click', (ev) => { if (ev.target === dlg) dlg.close(); });
  dlg.addEventListener('close', () => {
    const node = open && open.f.sec.querySelector('[data-id="' + CSS.escape(open.id) + '"]');
    if (node) { node.scrollIntoView({ block: 'nearest', inline: 'nearest' }); node.focus({ preventScroll: true }); }
    try { history.replaceState(null, '', location.pathname + location.search); } catch (_) {}
  });
  dlg.addEventListener('keydown', (ev) => {
    if (ev.target.closest('input,select')) return;
    if (ev.key === 'ArrowRight') { const b = dlg.querySelector('.foout .fwd'); if (b) b.click(); }
    if (ev.key === 'ArrowLeft') { const b = dlg.querySelector('.foout .plain'); if (b) b.click(); }
  });

  document.addEventListener('keydown', (ev) => {
    if (dlg.open || ev.target.closest('input,select,textarea')) return;
    if (ev.key === '+' || ev.key === '=') setZoom(current, current.zoom + 0.1);
    if (ev.key === '-') setZoom(current, current.zoom - 0.1);
    if (ev.key === '0') setZoom(current, fitZoom(current));
  });

  // #flow-id/state-id opens that state.
  const [hf, hs] = location.hash.slice(1).split('/').map(decodeURIComponent);
  const start = Math.max(0, flows.findIndex((f) => f.data.id === hf));
  showFlow(start);
  if (hs && flows[start].data.states[hs]) openState(flows[start], hs);
})();
