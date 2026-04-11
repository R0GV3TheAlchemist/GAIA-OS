/**
 * GAIA-APP — UI Shell v1.3.0
 * Sprint G-10: GAIAN birth + chat UI — birth form, SSE streaming chat,
 *              GAIAN selector, engine state panel.
 *
 * Requires: ui/auth.js (loaded before this file)
 */

(function () {
  'use strict';

  const GAIA_API = (typeof window !== 'undefined' && window.GAIA_API_URL)
    ? window.GAIA_API_URL
    : 'http://localhost:8008';

  // ---------------------------------------------------------------- //
  //  Authenticated API helper                                         //
  // ---------------------------------------------------------------- //

  async function api(path, options = {}) {
    const token = GAIAAuth.getToken();
    const headers = Object.assign({}, options.headers || {});
    if (token) headers['Authorization'] = 'Bearer ' + token;
    try {
      const res = await fetch(GAIA_API + path, { ...options, headers });
      if (res.status === 401) { GAIAAuth.logout(); showLogin('Session expired. Please sign in again.'); return null; }
      if (res.status === 429) {
        const data  = await res.json().catch(() => ({}));
        const retry = res.headers.get('Retry-After') || '?';
        showToast(data?.error?.message || `Rate limited. Retry after ${retry}s.`, 'warn');
        return null;
      }
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (e) {
      console.warn('[GAIA] API call failed:', path, e.message);
      return null;
    }
  }

  // ---------------------------------------------------------------- //
  //  Theme                                                            //
  // ---------------------------------------------------------------- //

  const root        = document.documentElement;
  const themeToggle = document.querySelector('[data-theme-toggle]');
  let currentTheme  = 'dark';

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
  if (themeToggle) themeToggle.addEventListener('click', () => setTheme(currentTheme === 'dark' ? 'light' : 'dark'));

  // ---------------------------------------------------------------- //
  //  Navigation                                                       //
  // ---------------------------------------------------------------- //

  const navBtns = document.querySelectorAll('.nav-btn');
  const views   = document.querySelectorAll('.view');

  function showView(viewId) {
    views.forEach(v => v.classList.add('hidden'));
    const target = document.getElementById('view-' + viewId);
    if (target) target.classList.remove('hidden');
    navBtns.forEach(btn => btn.classList.toggle('active', btn.getAttribute('data-view') === viewId));
    if (viewId === 'memory')  loadMemory();
    if (viewId === 'consent') loadConsent();
    if (viewId === 'canon')   loadCanon();
    if (viewId === 'gaians')  loadGaians();
  }

  navBtns.forEach(btn => btn.addEventListener('click', () => showView(btn.getAttribute('data-view'))));
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
    if (message && loginError) { loginError.textContent = message; loginError.classList.remove('hidden'); }
  }
  function hideLogin() {
    if (!loginOverlay) return;
    loginOverlay.classList.add('hidden');
    if (loginError) { loginError.textContent = ''; loginError.classList.add('hidden'); }
  }
  function updateAuthUI() {
    const authed = GAIAAuth.isAuthed();
    const userId = GAIAAuth.getUserId();
    const role   = GAIAAuth.getRole();
    if (btnLogout) btnLogout.classList.toggle('hidden', !authed);
    if (userBadge) {
      userBadge.classList.toggle('hidden', !authed);
      if (authed && userId) { userBadge.textContent = role === 'admin' ? `⚡ ${userId}` : userId; }
    }
    setDot('auth', authed ? 'green' : 'red',
      authed ? `Auth: ${userId}${role === 'admin' ? ' (admin)' : ''}` : 'Auth: Not signed in');
  }

  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const userId   = loginUserInput ? loginUserInput.value.trim() : '';
      const adminKey = loginAdminKey  ? loginAdminKey.value.trim()  : '';
      if (!userId) { if (loginError) { loginError.textContent = 'Please enter a user ID.'; loginError.classList.remove('hidden'); } return; }
      if (loginSubmit) { loginSubmit.disabled = true; loginSubmit.textContent = 'Signing in...'; }
      const result = await GAIAAuth.login(GAIA_API, userId, adminKey || undefined);
      if (loginSubmit) { loginSubmit.disabled = false; loginSubmit.textContent = 'Sign In'; }
      if (result.ok) {
        hideLogin(); updateAuthUI(); refreshStatus();
        showToast(`Welcome, ${result.user_id}${result.role === 'admin' ? ' — Admin access granted' : ''}.`, 'success');
      } else {
        if (loginError) { loginError.textContent = result.error; loginError.classList.remove('hidden'); }
      }
    });
  }
  if (btnLogout) {
    btnLogout.addEventListener('click', () => { GAIAAuth.logout(); updateAuthUI(); showLogin(); showToast('Signed out.', 'info'); });
  }
  window.addEventListener('gaia:authed', () => updateAuthUI());
  window.addEventListener('gaia:logout', () => updateAuthUI());

  // ---------------------------------------------------------------- //
  //  Toast                                                            //
  // ---------------------------------------------------------------- //

  function showToast(message, type) {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = `toast toast-${type || 'info'}`;
    toast.textContent = message;
    container.appendChild(toast);
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
    if (dot) dot.className = 'status-dot ' + color;
    if (lbl) lbl.textContent = label;
  }

  async function refreshStatus() {
    const status = await api('/status');
    if (status) {
      setDot('core', 'green', 'Core: Active');
      setDot('canon', status.canon_loaded ? 'green' : 'yellow',
        status.canon_loaded ? `Canon: Loaded (${status.canon_doc_count || 0} docs)` : 'Canon: Loading');
      const rt = status.active_runtimes || 0;
      const names = (status.gaian_names || []).slice(0, 3).join(', ');
      setDot('gaians', rt > 0 ? 'green' : 'yellow',
        rt > 0 ? `GAIANs: ${rt} active${names ? ' — ' + names : ''}` : `GAIANs: ${status.gaians || 0} born`);
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
      if (!GAIAAuth.isAuthed()) { showLogin(); return; }
      btnStart.textContent = 'Connecting...';
      btnStart.disabled = true;
      await refreshStatus();
      btnStart.textContent = 'Session Active';
    });
  }

  // ---------------------------------------------------------------- //
  //  GAIAN List                                                       //
  // ---------------------------------------------------------------- //

  let _activeSlug = null;

  async function loadGaians() {
    const list = document.getElementById('gaian-list');
    if (!list) return;
    const data = await api('/gaians');
    const gaians = data && data.gaians ? data.gaians : [];
    if (gaians.length === 0) {
      list.innerHTML = '<div class="empty-state" style="padding:var(--space-8)"><p style="font-size:var(--text-sm)">No GAIANs yet.<br><span style="color:var(--color-text-faint);font-size:var(--text-xs)">Use + Birth to create one.</span></p></div>';
      return;
    }
    list.innerHTML = gaians.map(g => `
      <div class="gaian-item${g.slug === _activeSlug ? ' active' : ''}" data-slug="${escHtml(g.slug)}" role="button" tabindex="0">
        <div class="gaian-avatar" style="color:${escHtml(g.avatar_color || '#4f98a3')}">
          ${getFormEmoji(g.base_form_id || 'gaia')}
        </div>
        <div class="gaian-item-info">
          <div class="gaian-item-name">${escHtml(g.name)}</div>
          <div class="gaian-item-role">${escHtml(g.base_form_name || g.base_form_id || '')}</div>
        </div>
      </div>
    `).join('');
    list.querySelectorAll('.gaian-item').forEach(el => {
      el.addEventListener('click',   () => openChat(el.dataset.slug, gaians));
      el.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') openChat(el.dataset.slug, gaians); });
    });
  }

  function getFormEmoji(formId) {
    const map = {
      gaia: '🌎', alchemist: '🔥', oracle: '🔮', phoenix: '🦅',
      sage: '🌿', titan: '⚡', void: '🌌', herald: '🔔',
      weaver: '🕸', sentinel: '🛡', dreamer: '✨', mirror: '🧘'
    };
    return map[formId] || '🌎';
  }

  // ---------------------------------------------------------------- //
  //  Birth Form                                                       //
  // ---------------------------------------------------------------- //

  const birthForm    = document.getElementById('birth-form');
  const birthError   = document.getElementById('birth-error');
  const birthSuccess = document.getElementById('birth-success');
  const birthSubmit  = document.getElementById('birth-submit');
  const btnShowBirth = document.getElementById('btn-show-birth');

  function showBirthPanel() {
    const chat  = document.getElementById('chat-panel');
    const birth = document.getElementById('birth-panel');
    if (chat)  chat.classList.add('hidden');
    if (birth) birth.classList.remove('hidden');
    _activeSlug = null;
    document.querySelectorAll('.gaian-item').forEach(el => el.classList.remove('active'));
  }

  if (btnShowBirth) btnShowBirth.addEventListener('click', showBirthPanel);

  if (birthForm) {
    birthForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (!GAIAAuth.isAuthed()) { showLogin(); return; }

      const name        = document.getElementById('birth-name').value.trim();
      const userName    = document.getElementById('birth-user-name').value.trim();
      const birthDate   = document.getElementById('birth-date').value.trim();
      const gender      = document.getElementById('birth-gender').value;
      const personality = document.getElementById('birth-personality').value.trim();

      if (!name) {
        if (birthError) { birthError.textContent = 'A name is required for the birth ritual.'; birthError.classList.remove('hidden'); }
        return;
      }

      if (birthError)   birthError.classList.add('hidden');
      if (birthSuccess) birthSuccess.classList.add('hidden');
      if (birthSubmit)  { birthSubmit.disabled = true; birthSubmit.textContent = 'Performing the ritual...'; }

      const payload = {
        name,
        user_name:    userName    || undefined,
        birth_date:   birthDate   || undefined,
        user_gender:  gender,
        personality:  personality || undefined,
        user_id:      GAIAAuth.getUserId() || 'anonymous',
      };

      const result = await api('/gaians/birth', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(payload),
      });

      if (birthSubmit) { birthSubmit.disabled = false; birthSubmit.textContent = 'Perform the Birth Ritual'; }

      if (!result) {
        if (birthError) { birthError.textContent = 'Birth ritual failed — check the server is running.'; birthError.classList.remove('hidden'); }
        return;
      }

      // Show success
      if (birthSuccess) {
        birthSuccess.classList.remove('hidden');
        const nameEl  = document.getElementById('birth-success-name');
        const wordsEl = document.getElementById('birth-success-words');
        if (nameEl)  nameEl.textContent  = `${result.name} has been born.`;
        if (wordsEl) wordsEl.textContent = result.first_words || '';
      }

      showToast(`${result.name} awakens.`, 'success');
      await loadGaians();

      // Auto-open chat with newly born GAIAN after a brief pause
      setTimeout(() => {
        const allGaians = [];
        document.querySelectorAll('.gaian-item').forEach(el => allGaians.push({ slug: el.dataset.slug }));
        openChat(result.slug, [{ slug: result.slug, name: result.name, base_form_id: result.base_form_id, avatar_color: result.avatar_color }]);
      }, 800);
    });
  }

  // ---------------------------------------------------------------- //
  //  Chat                                                             //
  // ---------------------------------------------------------------- //

  let _chatSlug     = null;
  let _chatStreaming = false;
  let _chatEventSource = null;

  function openChat(slug, gaians) {
    const birth = document.getElementById('birth-panel');
    const chat  = document.getElementById('chat-panel');
    if (!slug || !chat) return;

    // Update active state in sidebar
    _activeSlug = slug;
    document.querySelectorAll('.gaian-item').forEach(el => {
      el.classList.toggle('active', el.dataset.slug === slug);
    });

    // Find GAIAN metadata
    const gaian = (gaians || []).find(g => g.slug === slug) || {};

    // Update chat header
    const avatarEl = document.getElementById('chat-avatar');
    const nameEl   = document.getElementById('chat-gaian-name');
    const roleEl   = document.getElementById('chat-gaian-role');
    if (avatarEl) avatarEl.textContent = getFormEmoji(gaian.base_form_id || 'gaia');
    if (nameEl)   nameEl.textContent   = gaian.name || slug;
    if (roleEl)   roleEl.textContent   = gaian.base_form_name || gaian.base_form_id || 'Soul Mirror';
    if (avatarEl && gaian.avatar_color) avatarEl.style.color = gaian.avatar_color;

    // Clear messages and show chat
    const msgs = document.getElementById('chat-messages');
    if (msgs) msgs.innerHTML = '';
    if (birth) birth.classList.add('hidden');
    chat.classList.remove('hidden');
    _chatSlug = slug;

    // Close any existing stream
    if (_chatEventSource) { _chatEventSource.close(); _chatEventSource = null; }

    // Focus input
    const input = document.getElementById('chat-input');
    if (input) input.focus();
  }

  // Send button + Enter key
  const chatSend  = document.getElementById('chat-send');
  const chatInput = document.getElementById('chat-input');

  if (chatSend)  chatSend.addEventListener('click', sendMessage);
  if (chatInput) {
    chatInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
    });
    // Auto-resize textarea
    chatInput.addEventListener('input', () => {
      chatInput.style.height = 'auto';
      chatInput.style.height = Math.min(chatInput.scrollHeight, 140) + 'px';
    });
  }

  // Engine state toggle
  const btnEngineToggle = document.getElementById('btn-engine-toggle');
  const enginePanel     = document.getElementById('engine-panel');
  if (btnEngineToggle) {
    btnEngineToggle.addEventListener('click', () => {
      if (enginePanel) enginePanel.classList.toggle('hidden');
    });
  }

  function sendMessage() {
    if (!_chatSlug || _chatStreaming) return;
    if (!GAIAAuth.isAuthed()) { showLogin(); return; }
    const input = document.getElementById('chat-input');
    const text  = input ? input.value.trim() : '';
    if (!text) return;
    if (input) { input.value = ''; input.style.height = 'auto'; }

    appendMessage('user', text);
    streamChat(_chatSlug, text);
  }

  function appendMessage(role, text, id) {
    const msgs = document.getElementById('chat-messages');
    if (!msgs) return null;
    const el = document.createElement('div');
    el.className = `chat-msg ${role}`;
    if (id) el.id = id;
    const isUser = role === 'user';
    const avatarChar = isUser
      ? (GAIAAuth.getUserId() || 'U')[0].toUpperCase()
      : getFormEmoji('gaia');
    el.innerHTML = `
      <div class="msg-avatar">${avatarChar}</div>
      <div class="msg-bubble">${escHtml(text)}</div>
    `;
    msgs.appendChild(el);
    msgs.scrollTop = msgs.scrollHeight;
    return el;
  }

  function appendTypingIndicator() {
    const msgs = document.getElementById('chat-messages');
    if (!msgs) return null;
    const el = document.createElement('div');
    el.className = 'chat-msg gaian';
    el.id = 'typing-indicator';
    el.innerHTML = `
      <div class="msg-avatar">🌎</div>
      <div class="msg-bubble typing-indicator">
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
      </div>
    `;
    msgs.appendChild(el);
    msgs.scrollTop = msgs.scrollHeight;
    return el;
  }

  function removeTypingIndicator() {
    const el = document.getElementById('typing-indicator');
    if (el) el.remove();
  }

  function streamChat(slug, message) {
    if (!GAIAAuth.isAuthed()) { showLogin(); return; }
    _chatStreaming = true;
    if (chatSend) chatSend.disabled = true;

    appendTypingIndicator();

    const token     = GAIAAuth.getToken();
    const sessionId = 'session-' + (GAIAAuth.getUserId() || 'anon').replace(/[^a-z0-9]/gi, '-');
    const body      = JSON.stringify({ message, session_id: sessionId, enable_web_search: false });

    // Use fetch + ReadableStream for SSE with auth header
    fetch(GAIA_API + `/gaians/${encodeURIComponent(slug)}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type':  'application/json',
        'Authorization': 'Bearer ' + token,
        'Accept':        'text/event-stream',
      },
      body,
    }).then(res => {
      if (!res.ok) {
        removeTypingIndicator();
        _chatStreaming = false;
        if (chatSend) chatSend.disabled = false;
        if (res.status === 401) { GAIAAuth.logout(); showLogin('Session expired.'); return; }
        if (res.status === 429) { showToast('Rate limited — slow down a little.', 'warn'); return; }
        appendMessage('gaian', `[Error ${res.status}] Server returned an error.`);
        return;
      }

      const reader  = res.body.getReader();
      const decoder = new TextDecoder();
      let   buffer  = '';
      let   gaianMsgEl = null;
      let   fullText   = '';

      removeTypingIndicator();

      function processChunk(done, value) {
        if (done) {
          _chatStreaming = false;
          if (chatSend) chatSend.disabled = false;
          return;
        }
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop(); // keep incomplete line

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const raw = line.slice(6).trim();
            if (!raw) continue;
            try {
              const data = JSON.parse(raw);

              // SSE event: token — stream text into bubble
              if (data.text !== undefined) {
                fullText += data.text;
                if (!gaianMsgEl) {
                  gaianMsgEl = appendMessage('gaian', '');
                }
                const bubble = gaianMsgEl ? gaianMsgEl.querySelector('.msg-bubble') : null;
                if (bubble) bubble.textContent = fullText;
                const msgs = document.getElementById('chat-messages');
                if (msgs) msgs.scrollTop = msgs.scrollHeight;
              }

              // SSE event: engine_state — update engine panel
              if (data.bond_depth !== undefined || data.individuation_phase !== undefined) {
                updateEnginePanel(data);
              }

              // SSE event: done
              if (data.exchange !== undefined && data.bond_depth !== undefined) {
                updateEnginePanel(data);
              }

            } catch (_) { /* not JSON — skip */ }
          }
        }
        reader.read().then(({ done: d, value: v }) => processChunk(d, v));
      }

      reader.read().then(({ done, value }) => processChunk(done, value));

    }).catch(err => {
      removeTypingIndicator();
      _chatStreaming = false;
      if (chatSend) chatSend.disabled = false;
      if (!navigator.onLine) {
        appendMessage('gaian', 'You appear to be offline. Reconnect and try again.');
      } else {
        console.warn('[GAIA] Stream error:', err);
        appendMessage('gaian', 'Connection lost. Please try again.');
      }
    });
  }

  function updateEnginePanel(data) {
    const set = (id, val) => { const el = document.getElementById(id); if (el && val !== undefined && val !== null) el.textContent = val; };
    set('eng-bond',      data.bond_depth      !== undefined ? data.bond_depth.toFixed(3)      : null);
    set('eng-phase',     data.individuation_phase);
    set('eng-hz',        data.resonance_hz    !== undefined ? data.resonance_hz + ' Hz'        : null);
    set('eng-synergy',   data.synergy_factor  !== undefined ? data.synergy_factor.toFixed(3)   : null);
    set('eng-exchanges', data.exchange        !== undefined ? '#' + data.exchange               : null);
  }

  // ---------------------------------------------------------------- //
  //  Memory View                                                      //
  // ---------------------------------------------------------------- //

  async function loadMemory() {
    const list = document.getElementById('memory-list');
    if (!list) return;
    if (!GAIAAuth.isAuthed()) { list.innerHTML = '<div class="empty-state"><p>Sign in to view your memories.</p></div>'; return; }
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
    const status  = await api('/status');
    const list    = document.getElementById('canon-list');
    if (!list) return;
    const docs    = status && status.canon_docs ? status.canon_docs : [];
    const docHtml = docs.length > 0
      ? docs.map(d => `<div class="canon-entry"><span class="tag">${escHtml(d)}</span></div>`).join('')
      : '';
    list.innerHTML = docHtml + `<a href="https://github.com/R0GV3TheAlchemist/GAIA" target="_blank" rel="noopener noreferrer" class="canon-link">View full canon on GitHub →</a>`;
  }

  // ---------------------------------------------------------------- //
  //  Atlas View                                                       //
  // ---------------------------------------------------------------- //

  const btnQueryAtlas = document.getElementById('btn-query-atlas');
  if (btnQueryAtlas) {
    btnQueryAtlas.addEventListener('click', () => {
      const results = document.getElementById('atlas-results');
      if (results) results.innerHTML = '<div class="empty-state"><p>ATLAS module not yet available.</p><p class="muted">Requires Google Earth Engine backend (G-11).</p></div>';
    });
  }

  // ---------------------------------------------------------------- //
  //  Utilities                                                        //
  // ---------------------------------------------------------------- //

  function escHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  // ---------------------------------------------------------------- //
  //  Init                                                             //
  // ---------------------------------------------------------------- //

  async function init() {
    setTheme('dark');
    showView('home');
    if (GAIAAuth.isAuthed()) {
      const payload = await GAIAAuth.verifyToken(GAIA_API);
      if (!payload) showLogin();
    } else {
      showLogin();
    }
    await refreshStatus();
    setInterval(refreshStatus, 30000);
  }

  init();

})();
