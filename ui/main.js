/**
 * GAIA-APP — UI Shell
 * Handles navigation, theme toggle, and basic view management.
 * The constitutional core logic lives in core/ (Python, bridged via Tauri).
 */

(function () {
  'use strict';

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
    themeToggle.addEventListener('click', () => {
      setTheme(currentTheme === 'dark' ? 'light' : 'dark');
    });
  }

  // --- Navigation ---
  const navBtns = document.querySelectorAll('.nav-btn');
  const views = document.querySelectorAll('.view');

  function showView(viewId) {
    views.forEach(v => v.classList.add('hidden'));
    const target = document.getElementById('view-' + viewId);
    if (target) target.classList.remove('hidden');
    navBtns.forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-view') === viewId);
    });
  }

  navBtns.forEach(btn => {
    btn.addEventListener('click', () => showView(btn.getAttribute('data-view')));
  });

  // Canon button in hero
  const btnCanon = document.getElementById('btn-canon');
  if (btnCanon) btnCanon.addEventListener('click', () => showView('canon'));

  // Start session placeholder
  const btnStart = document.getElementById('btn-start');
  if (btnStart) {
    btnStart.addEventListener('click', () => {
      btnStart.textContent = 'Session Active';
      btnStart.disabled = true;
      // TODO: invoke Tauri command to initialize GAIA core session
      // window.__TAURI__.invoke('start_gaia_session');
      console.log('[GAIA] Session started — core invocation pending Tauri bridge');
    });
  }

  // Initial state
  setTheme('dark');
  showView('home');

})();
