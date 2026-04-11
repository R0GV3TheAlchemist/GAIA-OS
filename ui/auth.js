/**
 * ui/auth.js
 * GAIA Auth Module — Sprint G-9
 *
 * Manages JWT token lifecycle in the browser:
 *   - login(userId, adminKey?)  — POST /auth/token, store token
 *   - logout()                  — clear token, emit event
 *   - getToken()                — return stored token or null
 *   - isAuthed()                — boolean, token present
 *   - verifyToken(apiBase)      — GET /auth/me to confirm token still valid
 *   - getPayload()              — decode JWT payload (no signature verify — server does that)
 *
 * Storage: sessionStorage (cleared on tab close — sovereign default).
 * Key:     'gaia_token'
 *
 * Events dispatched on window:
 *   gaia:authed   { detail: { user_id, role, expires_in } }
 *   gaia:logout   {}
 *
 * Canon Ref: C01 (Sovereignty), C15 (Consent)
 */

(function (global) {
  'use strict';

  const TOKEN_KEY  = 'gaia_token';
  const USER_KEY   = 'gaia_user_id';
  const ROLE_KEY   = 'gaia_role';

  // ---------------------------------------------------------------- //
  //  Storage helpers                                                  //
  // ---------------------------------------------------------------- //

  function _store(token, userId, role) {
    try {
      sessionStorage.setItem(TOKEN_KEY, token);
      sessionStorage.setItem(USER_KEY,  userId);
      sessionStorage.setItem(ROLE_KEY,  role);
    } catch (e) {
      console.warn('[GAIA Auth] sessionStorage write failed:', e);
    }
  }

  function _clear() {
    try {
      sessionStorage.removeItem(TOKEN_KEY);
      sessionStorage.removeItem(USER_KEY);
      sessionStorage.removeItem(ROLE_KEY);
    } catch (e) {}
  }

  // ---------------------------------------------------------------- //
  //  Public API                                                       //
  // ---------------------------------------------------------------- //

  /**
   * POST /auth/token — exchange user_id (+ optional admin_key) for a JWT.
   * Returns { ok: true, role, user_id, expires_in } or { ok: false, error }.
   */
  async function login(apiBase, userId, adminKey) {
    if (!userId || !userId.trim()) {
      return { ok: false, error: 'user_id is required.' };
    }
    try {
      const body = { user_id: userId.trim() };
      if (adminKey && adminKey.trim()) body.admin_key = adminKey.trim();

      const res = await fetch(apiBase + '/auth/token', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(body),
      });

      if (res.status === 429) {
        const data = await res.json().catch(() => ({}));
        const msg  = data?.error?.message || 'Too many login attempts. Please wait.';
        return { ok: false, error: msg };
      }

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        return { ok: false, error: data?.detail || `Login failed (HTTP ${res.status}).` };
      }

      const data = await res.json();
      _store(data.access_token, data.user_id, data.role);

      window.dispatchEvent(new CustomEvent('gaia:authed', {
        detail: { user_id: data.user_id, role: data.role, expires_in: data.expires_in }
      }));

      return { ok: true, role: data.role, user_id: data.user_id, expires_in: data.expires_in };
    } catch (e) {
      return { ok: false, error: 'Network error — is the GAIA server running?' };
    }
  }

  /**
   * Clear token and emit gaia:logout.
   */
  function logout() {
    _clear();
    window.dispatchEvent(new CustomEvent('gaia:logout'));
  }

  /**
   * Return the stored JWT string, or null.
   */
  function getToken() {
    try { return sessionStorage.getItem(TOKEN_KEY); }
    catch (e) { return null; }
  }

  /**
   * Return true if a token is present in storage.
   */
  function isAuthed() {
    return !!getToken();
  }

  /**
   * GET /auth/me — verify token is still valid server-side.
   * Returns the TokenPayload or null.
   */
  async function verifyToken(apiBase) {
    const token = getToken();
    if (!token) return null;
    try {
      const res = await fetch(apiBase + '/auth/me', {
        headers: { 'Authorization': 'Bearer ' + token }
      });
      if (!res.ok) {
        if (res.status === 401) logout();
        return null;
      }
      return await res.json();
    } catch (e) {
      return null;
    }
  }

  /**
   * Decode JWT payload (base64url) without verifying signature.
   * Signature verification happens server-side.
   * Returns the payload object or null.
   */
  function getPayload() {
    const token = getToken();
    if (!token) return null;
    try {
      const parts   = token.split('.');
      if (parts.length !== 3) return null;
      const padded  = parts[1].replace(/-/g, '+').replace(/_/g, '/')
                               + '=='.slice((parts[1].length + 3) % 4 ? 0 : 4);
      return JSON.parse(atob(padded));
    } catch (e) {
      return null;
    }
  }

  /**
   * Return stored user_id (from sessionStorage, no decode needed).
   */
  function getUserId() {
    try { return sessionStorage.getItem(USER_KEY) || null; }
    catch (e) { return null; }
  }

  /**
   * Return stored role ('user' | 'admin' | null).
   */
  function getRole() {
    try { return sessionStorage.getItem(ROLE_KEY) || null; }
    catch (e) { return null; }
  }

  // ---------------------------------------------------------------- //
  //  Export to global scope (consumed by main.js)                    //
  // ---------------------------------------------------------------- //

  global.GAIAAuth = { login, logout, getToken, isAuthed, verifyToken, getPayload, getUserId, getRole };

})(window);
