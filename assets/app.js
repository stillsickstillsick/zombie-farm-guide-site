(function () {
  'use strict';
  const toggle = document.querySelector('.theme-toggle');
  function updateThemeButton() {
    if (!toggle) return;
    const dark = document.documentElement.dataset.theme === 'dark';
    toggle.textContent = dark ? '☀ Светлая тема' : '☾ Тёмная тема';
    toggle.setAttribute('aria-label', dark ? 'Включить светлую тему' : 'Включить тёмную тему');
    toggle.setAttribute('aria-pressed', String(dark));
  }
  updateThemeButton();
  if (toggle) toggle.addEventListener('click', function () {
    const theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = theme;
    try { localStorage.setItem('farm-theme', theme); } catch (e) { /* works without storage */ }
    updateThemeButton();
  });
  const root = document.body.dataset.root || './';
  const index = window.SEARCH_INDEX || [];
  const search = document.querySelector('#search');
  const results = document.querySelector('#results');

  // Numeric amounts are compared only within a known currency. Unknown and
  // non-purchasable items are last; dates in descriptive text are not prices.
  function priceKey(text) {
    const match = String(text || '').match(/^\s*(\d[\d\s\u00a0\u202f]*)\s*(зб(?=\s|[.,;]|$)|зомбакс\w*|монет\w*|голос\w*)/i);
    if (!match) return null;
    const amount = Number(match[1].replace(/\s/g, ''));
    const unit = match[2].toLocaleLowerCase('ru');
    const currency = unit.startsWith('монет') ? 'монеты' : unit.startsWith('голос') ? 'голоса' : 'зомбаксы';
    return { amount, currency };
  }
  function comparePrice(a, b) {
    const x = priceKey(a), y = priceKey(b);
    if (!x && !y) return 0;
    if (!x) return 1;
    if (!y) return -1;
    return x.currency.localeCompare(y.currency, 'ru') || x.amount - y.amount;
  }

  if (search && results) {
    const category = document.querySelector('#search-category');
    const order = document.querySelector('#search-order');
    function render() {
      const query = search.value.trim().toLocaleLowerCase('ru');
      results.replaceChildren();
      if (!query) { results.hidden = true; return; }
      results.hidden = false;
      const matches = index.filter(item =>
        item.text.toLocaleLowerCase('ru').includes(query) &&
        (!category.value || item.section === category.value)
      );
      matches.sort((a, b) =>
        (order.value === 'price' ? comparePrice(a.purchase, b.purchase) : 0) ||
        a.name.localeCompare(b.name, 'ru')
      );
      const title = document.createElement('p');
      title.textContent = 'Найдено: ' + matches.length;
      results.append(title);
      matches.slice(0, 100).forEach(item => {
        const link = document.createElement('a');
        link.className = 'searchhit';
        link.href = root + item.url;
        if (item.thumbnail) {
          const image = document.createElement('img');
          image.className = 'list-thumb';
          image.loading = 'lazy';
          image.src = root + item.thumbnail;
          image.alt = item.thumbnail_alt || item.name;
          link.append(image);
        } else {
          const placeholder = document.createElement('span');
          placeholder.className = 'list-placeholder';
          placeholder.textContent = '—';
          link.append(placeholder);
        }
        const label = document.createElement('span');
        label.textContent = item.name + ' · ' + item.section;
        link.append(label);
        results.append(link);
      });
      if (matches.length > 100) {
        const notice = document.createElement('p');
        notice.textContent = 'Показаны первые 100 результатов; уточните запрос.';
        results.append(notice);
      }
    }
    search.addEventListener('input', render);
    category.addEventListener('change', render);
    order.addEventListener('change', render);
  }

  const table = document.querySelector('table[data-sortable]');
  if (table) {
    const tbody = table.tBodies[0];
    table.querySelectorAll('th button').forEach((button, index) => {
      button.addEventListener('click', () => {
        const direction = button.dataset.dir === 'asc' ? 'desc' : 'asc';
        button.dataset.dir = direction;
        const isPrice = /^(Покупка|Продажа)$/.test(button.textContent.trim());
        const rows = Array.from(tbody.rows);
        rows.sort((a, b) => {
          const x = a.cells[index]?.textContent.trim() || '';
          const y = b.cells[index]?.textContent.trim() || '';
          let result;
          if (isPrice) {
            // Keep unknown prices at the end even when reversing the order.
            const px = priceKey(x), py = priceKey(y);
            if (!px || !py) return !px && !py ? 0 : (!px ? 1 : -1);
            result = comparePrice(x, y);
          } else {
            result = x.localeCompare(y, 'ru', { numeric: true });
          }
          return result * (direction === 'asc' ? 1 : -1);
        });
        rows.forEach(row => tbody.append(row));
      });
    });
    const filter = document.querySelector('#table-filter');
    if (filter) filter.addEventListener('input', () => {
      const query = filter.value.toLocaleLowerCase('ru').trim();
      // textContent works for rows already hidden by the previous query.
      Array.from(tbody.rows).forEach(row => {
        row.hidden = !row.textContent.toLocaleLowerCase('ru').includes(query);
      });
    });
  }
})();
