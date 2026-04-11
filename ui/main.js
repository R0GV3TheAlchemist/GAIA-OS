/**
 * GAIA-APP — UI Shell v1.2.0
 * Sprint G-9: Auth flow — login screen, token storage, Bearer wiring,
 *             /auth/me verify on load, logout, auth status dot.
 *
 * Requires: ui/auth.js (loaded before this file in index.html)
 *
 * API target: http://localhost:8008 (dev) or window.GAIA_API_URL (production)
 */

(function () {
  'use strict';

  // --- API Configuration ---
  const GAIA_API = (typeof window !== 'undefined' && window.GAIA_API_URL)
    ? window.GAIA_API_URL
    : 'http://localhost:8008';

  /**
   * Authenticated API call.
   * Attaches Authorization: Bearer <token> when a token is present.
   * On 401: clears token, shows login.
   * On 429: surfaces the Retry-After message.
   */
  async function api(path, options = {}) {
    const token = GAIAAuth.getToken();
    const headers = Object.assign({}, options.headers || {});
    if (token) headers['Authorization'] = 'Bearer ' + token;
    try {
      const res = await fetch(GAIA_API + path, { ...options, headers });
      if (res.status === 401) {
        GAIAAuth.logout();
        showLogin('Session expired. Please sign in again.');
        return null;
      }
      if (res.status === 429) {
        const data  = await res.json().catch(() => ({}));
        const retry = res.headers.get('Retry-After') || '?';
        const msg   = data?.error?.message || `Rate limited. Retry after ${retry}s.`;
        showToast(msg, 'warn');
        return null;
      }
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (e) {
      console.warn('[GAIA] API call failed:', path, e.message);
      return null;
    }
  }

  // --- Theme ---
  const root = document.documentElement;
  const themeToggle = document.querySelector('[data-theme-toggle]');
  let currentTheme = 'dark';

  function setTheme(theme) {
    currentTheme = theme;
    root.setAttribute('data-theme', theme);
    if (themeToggle) {
      themeToggle.innerHTML = theme === 'dark'
        ? '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>'
        : '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
      themeToggle.setAttribute('aria-label', `Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`);
    }
  }

  if (themeToggle) {
    themeToggle.addEventListener('click', () => setTheme(currentTheme === 'dark' ? 'light' : 'dark'));
  }

  // --- Navigation ---
  const navBtns = document.querySelectorAll('.nav-btn');
  const views   = document.querySelectorAll('.view');

  function showView(viewId) {
    views.forEach(v => v.classList.add('hidden'));
    const target = document.getElementById('view-' + viewId);
    if (target) target.classList.remove('hidden');
    navBtns.forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-view') === viewId);
    });
    if (viewId === 'memory')  loadMemory();
    if (viewId === 'consent') loadConsent();
    if (viewId === 'canon')   loadCanon();
  }

  navBtns.forEach(btn => {
    btn.addEventListener('click', () => showView(btn.getAttribute('data-view')));
  });

  const btnCanon = document.getElementById('btn-canon');
  if (btnCanon) btnCanon.addEventListener('click', () => showView('canon'));

  // ---------------------------------------------------------------- //
  //  Auth UI                                                          //
  // ---------------------------------------------------------------- //

  const loginOverlay   = document.getElementById('login-overlay');
  const loginForm      = document.getElementById('login-form');
  const loginUserInput = document.getElementById('login-user-id');
  const loginAdminKey  = document.getElementById('login-admin-key');
  const loginError     = document.getElementById('login-error');
  const loginSubmit    = document.getElementById('login-submit');
  const btnLogout      = document.getElementById('btn-logout');
  const userBadge      = document.getElementById('user-badge');

  function showLogin(message) {
    if (!loginOverlay) return;
    loginOverlay.classList.remove('hidden');
    if (message && loginError) {
      loginError.textContent = message;
      loginError.classList.remove('hidden');
    }
  }

  function hideLogin() {
    if (!loginOverlay) return;
    loginOverlay.classList.add('hidden');
    if (loginError) { loginError.textContent = ''; loginError.classList.add('hidden'); }
  }

  function updateAuthUI() {
    const authed  = GAIAAuth.isAuthed();
    const userId  = GAIAAuth.getUserId();
    const role    = GAIAAuth.getRole();

    if (btnLogout)  btnLogout.classList.toggle('hidden', !authed);
    if (userBadge) {
      userBadge.classList.toggle('hidden', !authed);
      if (authed && userId) {
        userBadge.textContent = role === 'admin' ? `⚡ ${userId}` : userId;
        userBadge.title = `Signed in as ${userId} (${role})`;
      }
    }
    setDot('auth',
      authed ? 'green' : 'red',
      authed ? `Auth: ${userId}${role === 'admin' ? ' (admin)' : ''}` : 'Auth: Not signed in'
    );
  }

  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const userId   = loginUserInput  ? loginUserInput.value.trim()  : '';
      const adminKey = loginAdminKey   ? loginAdminKey.value.trim()   : '';

      if (!userId) {
        if (loginError) { loginError.textContent = 'Please enter a user ID.'; loginError.classList.remove('hidden'); }
        return;
      }

      if (loginSubmit) { loginSubmit.disabled = true; loginSubmit.textContent = 'Signing in...'; }

      const result = await GAIAAuth.login(GAIA_API, userId, adminKey || undefined);

      if (loginSubmit) { loginSubmit.disabled = false; loginSubmit.textContent = 'Sign In'; }

      if (result.ok) {
        hideLogin();
        updateAuthUI();
        refreshStatus();
        showToast(`Welcome, ${result.user_id}${result.role === 'admin' ? ' — Admin access granted' : ''}.`, 'success');
      } else {
        if (loginError) { loginError.textContent = result.error; loginError.classList.remove('hidden'); }
      }
    });
  }

  if (btnLogout) {
    btnLogout.addEventListener('click', () => {
      GAIAAuth.logout();
      updateAuthUI();
      showLogin();
      showToast('Signed out.', 'info');
    });
  }

  // Listen for auth events from auth.js
  window.addEventListener('gaia:authed', () => updateAuthUI());
  window.addEventListener('gaia:logout', () => updateAuthUI());

  // ---------------------------------------------------------------- //
  //  Toast Notifications                                              //
  // ---------------------------------------------------------------- //

  function showToast(message, type) {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = `toast toast-${type || 'info'}`;
    toast.textContent = message;
    container.appendChild(toast);
    // Animate in
    requestAnimationFrame(() => toast.classList.add('toast-visible'));
    setTimeout(() => {
      toast.classList.remove('toast-visible');
      toast.addEventListener('transitionend', () => toast.remove(), { once: true });
    }, 3500);
  }

  // ---------------------------------------------------------------- //
  //  Status Bar                                                       //
  // ---------------------------------------------------------------- //

  function setDot(id, color, label) {
    const dot = document.getElementById('dot-' + id);
    const lbl = document.getElementById('label-' + id);
    if (dot) { dot.className = 'status-dot ' + color; }
    if (lbl) lbl.textContent = label;
  }

  async function refreshStatus() {
    const status = await api('/status');
    if (status) {
      setDot('core', 'green', 'Core: Active');
      const docCount   = status.canon_doc_count || 0;
      const docsLoaded = status.canon_loaded;
      setDot('canon',
        docsLoaded ? 'green' : 'yellow',
        docsLoaded ? `Canon: Loaded (${docCount} docs)` : 'Canon: Loading'
      );
      const activeRuntimes = status.active_runtimes || 0;
      const gaianNames     = (status.gaian_names || []).slice(0, 3).join(', ');
      setDot('gaians',
        activeRuntimes > 0 ? 'green' : 'yellow',
        activeRuntimes > 0
          ? `GAIANs: ${activeRuntimes} active${gaianNames ? ' — ' + gaianNames : ''}`
          : `GAIANs: ${status.gaians || 0} born`
      );
    } else {
      setDot('core',   'red', 'Core: Offline — run python core/server.py');
      setDot('canon',  'red', 'Canon: Unreachable');
      setDot('gaians', 'red', 'GAIANs: Unreachable');
    }
    updateAuthUI();
  }

  // ---------------------------------------------------------------- //
  //  Session Start                                                    //
  // ---------------------------------------------------------------- //

  const btnStart = document.getElementById('btn-start');
  if (btnStart) {
    btnStart.addEventListener('click', async () => {
      if (!GAIAAuth.isAuthed()) {
        showLogin();
        return;
      }
      btnStart.textContent = 'Connecting...';
      btnStart.disabled = true;
      await refreshStatus();
      btnStart.textContent = 'Session Active';
      console.log('[GAIA] Session initialized — constitutional core online');
    });
  }

  // ---------------------------------------------------------------- //
  //  Memory View                                                      //
  // ---------------------------------------------------------------- //

  async function loadMemory() {
    const list = document.getElementById('memory-list');
    if (!list) return;
    if (!GAIAAuth.isAuthed()) {
      list.innerHTML = '<div class="empty-state"><p>Sign in to view your memories.</p></div>';
      return;
    }
    list.innerHTML = '<div class="empty-state"><p>Loading...</p></div>';
    const data     = await api('/memory/list');
    const memories = data && data.memories ? data.memories : [];
    if (memories.length === 0) {
      list.innerHTML = '<div class="empty-state"><p>No memories stored yet.</p><p class="muted">Memories appear here as you interact with GAIA.</p></div>';
      return;
    }
    list.innerHTML = memories.map(m => `
      <div class="memory-entry">
        <div class="memory-content">${escHtml(m.query || '')}</div>
        <div class="memory-meta">
          <span class="tag">${m.source_count != null ? m.source_count + ' sources' : ''}</span>
          <span class="muted">${m.timestamp ? new Date(m.timestamp * 1000).toLocaleString() : ''}</span>
        </div>
      </div>
    `).join('');
  }

  const btnRefreshMemory = document.getElementById('btn-refresh-memory');
  if (btnRefreshMemory) btnRefreshMemory.addEventListener('click', loadMemory);

  // ---------------------------------------------------------------- //
  //  Consent View                                                     //
  // ---------------------------------------------------------------- //

  async function loadConsent() {
    const list = document.getElementById('consent-list');
    if (!list) return;
    list.innerHTML = '<div class="empty-state"><p>Consent ledger coming soon.</p><p class="muted">All consents granted to GAIA will appear here. Revoke any at any time.</p></div>';
  }

  // ---------------------------------------------------------------- //
  //  Canon View                                                       //
  // ---------------------------------------------------------------- //

  async function loadCanon() {
    const status = await api('/status');
    const list   = document.getElementById('canon-list');
    if (!list) return;
    const docs   = status && status.canon_docs ? status.canon_docs : [];
    const docHtml = docs.length > 0
      ? docs.map(d => `<div class="canon-entry"><span class="tag">${escHtml(d)}</span></div>`).join('')
      : '';
    list.innerHTML = docHtml + `
      <a href="https://github.com/R0GV3TheAlchemist/GAIA" target="_blank" rel="noopener noreferrer" class="canon-link">
        View full canon on GitHub →
      </a>
    `;
  }

  // ---------------------------------------------------------------- //
  //  Atlas View                                                       //
  // ---------------------------------------------------------------- //

  const btnQueryAtlas = document.getElementById('btn-query-atlas');
  if (btnQueryAtlas) {
    btnQueryAtlas.addEventListener('click', async () => {
      const results = document.getElementById('atlas-results');
      results.innerHTML = '<div class="empty-state"><p>ATLAS module not yet available.</p><p class="muted">Requires Google Earth Engine backend (G-11). Run <code>earthengine authenticate</code> to prepare.</p></div>';
    });
  }

  // ---------------------------------------------------------------- //
  //  Utilities                                                        //
  // ---------------------------------------------------------------- //

  function escHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  // ---------------------------------------------------------------- //
  //  Init                                                             //
  // ---------------------------------------------------------------- //

  async function init() {
    setTheme('dark');
    showView('home');

    // Verify any existing token on load
    if (GAIAAuth.isAuthed()) {
      const payload = await GAIAAuth.verifyToken(GAIA_API);
      if (!payload) {
        // Token was invalid/expired — show login silently
        showLogin();
      }
    } else {
      // No token — show login on first load
      showLogin();
    }

    await refreshStatus();
    setInterval(refreshStatus, 30000);
  }

  init();

})();
