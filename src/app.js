(function (root) {
  'use strict';
  function matches(entry, raw) {
    const query = String(raw || '').trim().toLowerCase();
    if (!query) return true;
    const numeric = query.match(/^(?:(?:style|mj-s)\s*)?0*(\d+)$/i);
    if (numeric) return entry.number === Number(numeric[1]);
    return [entry.id, entry.name, entry.family, ...entry.tags, entry.palette,
      entry.lighting, entry.texture, entry.composition, entry.recipe].join(' ').toLowerCase().includes(query);
  }
  function select(entries, family, query) {
    return entries.filter(entry => (family === 'all' || entry.family_id === family) && matches(entry, query));
  }
  const api = { matches, select };
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (!root.document) return;
  const doc = root.document;
  const $ = id => doc.getElementById(id);
  const dataNode = $('catalog-data');
  if (!dataNode) return;
  let data;
  try { data = JSON.parse(dataNode.textContent); } catch (_) { return; }
  const entries = data.entries;
  const cards = Array.from(doc.querySelectorAll('article[data-style]'));
  const lookup = new Map(entries.map(e => [e.id, e]));
  let family = 'all'; let toastTimer; let lastFocus;
  function announce(message) {
    $('toast').textContent = message;
    root.clearTimeout(toastTimer);
    toastTimer = root.setTimeout(() => { $('toast').textContent = ''; }, 4000);
  }
  function filter() {
    const visible = new Set(select(entries, family, $('search').value).map(e => e.id));
    cards.forEach(card => { card.hidden = !visible.has(card.dataset.style); });
    $('count').textContent = visible.size + ' of ' + entries.length + ' styles';
    $('empty').hidden = visible.size !== 0;
    doc.querySelectorAll('[data-family]').forEach(button => {
      if (button.tagName === 'BUTTON') button.setAttribute('aria-pressed', String(button.dataset.family === family));
    });
  }
  function reset() { family = 'all'; $('search').value = ''; filter(); }
  async function copy(entry, button) {
    let copied = false;
    try {
      if (root.navigator.clipboard && root.isSecureContext) {
        await root.navigator.clipboard.writeText(entry.instruction); copied = true;
      }
    } catch (_) { /* Permission denial falls through to a visible, selectable instruction. */ }
    if (!copied) {
      const panel = button.closest('.body').querySelector('.manualcopy');
      panel.hidden = false;
      const field = panel.querySelector('textarea');
      field.focus(); field.select(); field.setSelectionRange(0, field.value.length);
      try { copied = Boolean(doc.execCommand && doc.execCommand('copy')); } catch (_) { /* Manual copy remains visible. */ }
      if (!copied) { announce('Instruction selected. Long-press or use Copy.'); return; }
    }
    button.textContent = 'Copied - use style ' + entry.number;
    announce('Style ' + entry.number + ' copied. Replace [NEW SUBJECT] and [FORMAT].');
    root.setTimeout(() => { button.textContent = 'Copy style instruction'; }, 2600);
  }
  function closeViewer() {
    const viewer = $('viewer');
    if (typeof viewer.close === 'function') viewer.close(); else viewer.removeAttribute('open');
    if (lastFocus) lastFocus.focus();
  }
  function enlarge(entry, button) {
    lastFocus = button;
    const card = doc.getElementById(entry.id);
    $('viewtitle').textContent = String(entry.number).padStart(2, '0') + ' / ' + entry.name;
    $('viewimage').src = card.querySelector('img').src;
    $('viewimage').alt = 'Original source reference for ' + entry.id;
    $('viewsource').replaceChildren(doc.createTextNode('Original reference / ' + entry.source.creator + ' / '));
    const link = doc.createElement('a'); link.href = entry.source.source_url;
    link.target = '_blank'; link.rel = 'noopener noreferrer'; link.textContent = 'View source';
    $('viewsource').appendChild(link);
    const viewer = $('viewer');
    if (typeof viewer.showModal === 'function') viewer.showModal();
    else { viewer.classList.add('viewer-fallback'); viewer.setAttribute('open', ''); }
    $('close').focus();
  }
  $('search').addEventListener('input', filter);
  $('reset').addEventListener('click', reset);
  doc.querySelector('.defaultbar').addEventListener('click', reset);
  $('emptyreset').addEventListener('click', reset);
  $('filters').addEventListener('click', event => {
    const button = event.target.closest('button[data-family]');
    if (!button) return; family = button.dataset.family; filter();
  });
  $('gallery').addEventListener('click', event => {
    const button = event.target.closest('button[data-copy], button[data-view]');
    if (!button) return;
    const entry = lookup.get(button.dataset.copy || button.dataset.view);
    if (!entry) return;
    if (button.dataset.copy) copy(entry, button); else enlarge(entry, button);
  });
  $('close').addEventListener('click', closeViewer);
  $('viewer').addEventListener('click', event => { if (event.target === $('viewer')) closeViewer(); });
  doc.addEventListener('keydown', event => { if (event.key === 'Escape' && $('viewer').hasAttribute('open')) closeViewer(); });
  filter();
  doc.documentElement.classList.add('has-js');
})(typeof window === 'undefined' ? globalThis : window);
