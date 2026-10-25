const byId = (id) => document.getElementById(id);
const state = { csrf: '', authenticated: false, places: [], users: [] };
const symbols = ['⌂', '✳', '◉', '↗', '✦', '⌘'];

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  })[char]);
}

async function api(url, options = {}) {
  const headers = { ...(options.body ? { 'Content-Type': 'application/json' } : {}), ...options.headers };
  if (options.method && options.method !== 'GET' && state.csrf) headers['X-CSRF-Token'] = state.csrf;
  const response = await fetch(url, { ...options, headers });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.error || `Ошибка ${response.status}`);
  return payload;
}

function showNotice(message, success = false) {
  const notice = byId('notice');
  notice.textContent = message;
  notice.classList.toggle('success', success);
  notice.classList.remove('hidden');
  window.clearTimeout(showNotice.timer);
  showNotice.timer = window.setTimeout(() => notice.classList.add('hidden'), 4500);
}

async function loadFilters() {
  const categories = await api('/api/categories');
  byId('category').insertAdjacentHTML('beforeend', categories.map((category) =>
    `<option value="${category.id}">${escapeHtml(category.name)}</option>`).join(''));
}

function renderPlaces(places) {
  state.places = places;
  byId('result-count').textContent = `${places.length} ${places.length === 1 ? 'место' : places.length > 1 && places.length < 5 ? 'места' : 'мест'}`;
  if (!places.length) {
    byId('places').innerHTML = '<div class="empty-state">Пока здесь тихо. Попробуйте изменить фильтры.</div>';
    fillPlaceSelect();
    return;
  }
  byId('places').innerHTML = places.map((place, index) => `
    <article class="place-card">
      <div class="card-art palette-${index % 6}">
        <span class="art-number">${String(index + 1).padStart(2, '0')} / ГОРОД</span>
        <span class="art-symbol" aria-hidden="true">${symbols[index % symbols.length]}</span>
        <span class="rating-chip"><span>★</span>${place.rating}</span>
      </div>
      <div class="card-body">
        <p class="card-category">${escapeHtml(place.category_name)}</p>
        <h3>${escapeHtml(place.name)}</h3>
        <p class="card-address">${escapeHtml(place.address)}</p>
        <div class="card-footer"><span class="availability">● Открыто для вас</span><span class="card-open">Открыть место ↗</span></div>
      </div>
    </article>`).join('');
  fillPlaceSelect();
}

async function searchPlaces() {
  const params = new URLSearchParams();
  if (byId('search').value.trim()) params.set('q', byId('search').value.trim());
  if (byId('category').value) params.set('category_id', byId('category').value);
  if (byId('rating').value) params.set('min_rating', byId('rating').value);
  try { renderPlaces(await api(`/api/places?${params}`)); }
  catch (error) { showNotice(error.message); }
}

function fillPlaceSelect() {
  const select = byId('place-select');
  if (!select) return;
  const current = select.value;
  select.innerHTML = state.places.map((place) =>
    `<option value="${place.id}">${escapeHtml(place.name)}</option>`).join('');
  if (current && state.places.some((place) => String(place.id) === current)) select.value = current;
}

async function loadRecommendations() {
  if (!state.authenticated) return;
  const [users, recommendations] = await Promise.all([
    api('/api/users'), api('/api/recommendations'),
  ]);
  state.users = users;
  byId('user-select').innerHTML = users.map((user) =>
    `<option value="${user.id}">${escapeHtml(user.name)}</option>`).join('');
  byId('recommendations').innerHTML = recommendations.length ? recommendations.map((item) => `
    <div class="recommendation-row"><span>${escapeHtml(item.user_name)}<small>${escapeHtml(item.place_name)} · ${escapeHtml(item.status)}</small></span>
      <span><span class="status-pill ${item.is_cancelled ? 'cancelled' : ''}">${escapeHtml(item.status)}</span>
      ${item.is_cancelled ? '' : `<button class="cancel-button" data-cancel="${item.id}">Отменить</button>`}</span></div>`).join('')
    : '<div class="empty-state">Рекомендаций пока нет.</div>';
}

function setAuthenticated(authenticated) {
  state.authenticated = authenticated;
  byId('login-open').classList.toggle('hidden', authenticated);
  byId('account-menu').classList.toggle('hidden', !authenticated);
  byId('recommendation-panel').classList.toggle('hidden', !authenticated);
  if (authenticated) loadRecommendations().catch((error) => showNotice(error.message));
}

byId('search-button').addEventListener('click', searchPlaces);
byId('category').addEventListener('change', searchPlaces);
byId('rating').addEventListener('change', searchPlaces);
byId('search').addEventListener('keydown', (event) => { if (event.key === 'Enter') searchPlaces(); });
byId('login-open').addEventListener('click', () => byId('login-dialog').showModal());
byId('login-close').addEventListener('click', () => byId('login-dialog').close());

byId('login-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  try {
    const result = await api('/api/auth/login', {
      method: 'POST', body: JSON.stringify({ username: form.get('username'), password: form.get('password') }),
    });
    state.csrf = result.csrf_token;
    byId('login-error').classList.add('hidden');
    byId('login-dialog').close();
    event.currentTarget.reset();
    setAuthenticated(true);
  } catch (error) {
    byId('login-error').textContent = error.message;
    byId('login-error').classList.remove('hidden');
  }
});

byId('logout').addEventListener('click', async () => {
  try { await api('/api/auth/logout', { method: 'POST' }); setAuthenticated(false); }
  catch (error) { showNotice(error.message); }
});

byId('recommendation-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  try {
    await api('/api/recommendations', {
      method: 'POST', body: JSON.stringify({ user_id: byId('user-select').value, place_id: byId('place-select').value }),
    });
    showNotice('Рекомендация создана.', true);
    await loadRecommendations();
  } catch (error) { showNotice(error.message); }
});

byId('recommendations').addEventListener('click', async (event) => {
  const button = event.target.closest('[data-cancel]');
  if (!button) return;
  try {
    await api(`/api/recommendations/${button.dataset.cancel}/cancel`, { method: 'POST' });
    showNotice('Рекомендация отменена.', true);
    await loadRecommendations();
  } catch (error) { showNotice(error.message); }
});

async function start() {
  try {
    const auth = await api('/api/auth/csrf');
    state.csrf = auth.csrf_token;
    setAuthenticated(auth.authenticated);
    await loadFilters();
    await searchPlaces();
  } catch (error) { showNotice(error.message); }
}
start();
