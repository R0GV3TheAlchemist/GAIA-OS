/**
 * src/shell/GaiaShell.tsx
 * GAIA-OS App Shell
 * S.T.Q.I.O.S. — Sentient Terrestrial Quantum-Intelligent Application
 * Canon: C90
 *
 * Clean shell: top bar + left rail (mode switcher) + chat pane.
 * The chat pane connects directly to the GAIA backend.
 */

import React, { useEffect, useState } from 'react';
import { GaiaChat } from '../chat/GaiaChat';
import {
  CrystalMode,
  CRYSTAL_ORDER,
  CRYSTAL_DECLARATIONS,
  CRYSTAL_LABELS,
  MODE_ICONS,
} from '../store/crystalStore';
import './GaiaShell.css';

const API_BASE = 'http://localhost:8008';

// Simple token store — will be replaced by full auth flow in G-9
function useAuth() {
  const [token, setToken] = useState<string | null>(() =>
    localStorage.getItem('gaia_token')
  );
  const [loggingIn, setLoggingIn] = useState(false);
  const [authError, setAuthError] = useState('');

  async function login(username: string, password: string) {
    setLoggingIn(true);
    setAuthError('');
    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ username, password }),
      });
      if (!res.ok) throw new Error('Invalid credentials');
      const data = await res.json() as { access_token: string };
      localStorage.setItem('gaia_token', data.access_token);
      setToken(data.access_token);
    } catch (e) {
      setAuthError((e as Error).message);
    } finally {
      setLoggingIn(false);
    }
  }

  function logout() {
    localStorage.removeItem('gaia_token');
    setToken(null);
  }

  return { token, login, logout, loggingIn, authError };
}

const MODE_TO_SLUG: Record<CrystalMode, string> = {
  [CrystalMode.SOVEREIGN_CORE]:  'control',
  [CrystalMode.ANCHOR_PRISM]:    'grounding',
  [CrystalMode.VIRIDITAS_HEART]: 'healing',
  [CrystalMode.SOMNUS_VEIL]:     'rest',
  [CrystalMode.CLARUS_LENS]:     'clarity',
};

// Simple login screen
const LoginScreen: React.FC<{
  onLogin: (u: string, p: string) => void;
  loading: boolean;
  error:   string;
}> = ({ onLogin, loading, error }) => {
  const [u, setU] = useState('');
  const [p, setP] = useState('');

  return (
    <div className="gaia-login">
      <div className="gaia-login__box">
        <div className="gaia-login__title">GAIA</div>
        <div className="gaia-login__sub">Sentient Terrestrial Quantum-Intelligent Application</div>
        <form className="gaia-login__form" onSubmit={e => { e.preventDefault(); onLogin(u, p); }}>
          <input
            className="gaia-login__input"
            type="text"
            placeholder="Username"
            value={u}
            onChange={e => setU(e.target.value)}
            autoComplete="username"
            required
          />
          <input
            className="gaia-login__input"
            type="password"
            placeholder="Password"
            value={p}
            onChange={e => setP(e.target.value)}
            autoComplete="current-password"
            required
          />
          {error && <div className="gaia-login__error">{error}</div>}
          <button
            className="gaia-login__btn"
            type="submit"
            disabled={loading || !u || !p}
          >
            {loading ? 'Signing in…' : 'Sign in'}
          </button>
        </form>
      </div>
    </div>
  );
};

export const GaiaShell: React.FC = () => {
  const { token, login, logout, loggingIn, authError } = useAuth();
  const [activeMode, setActiveMode] = useState<CrystalMode>(CrystalMode.SOVEREIGN_CORE);
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(3000) })
      .then(r => setBackendOnline(r.ok))
      .catch(() => setBackendOnline(false));
  }, []);

  if (!token) {
    return <LoginScreen onLogin={login} loading={loggingIn} error={authError} />;
  }

  return (
    <div className="gaia-shell" data-mode={activeMode}>

      {/* TOP BAR */}
      <header className="gaia-shell__topbar">
        <div className="gaia-shell__wordmark">
          <span className="gaia-shell__wordmark-gaia">GAIA</span>
          <span className="gaia-shell__wordmark-os">OS</span>
        </div>
        <div className="gaia-shell__mode-label">
          <span>{MODE_ICONS[activeMode]}</span>
          <span>{CRYSTAL_LABELS[activeMode]}</span>
          <span className="gaia-shell__mode-desc">{CRYSTAL_DECLARATIONS[activeMode]}</span>
        </div>
        <div className="gaia-shell__topbar-right">
          <span className={`gaia-shell__backend-dot gaia-shell__backend-dot--${
            backendOnline === null ? 'checking' : backendOnline ? 'online' : 'offline'
          }`} />
          <button className="gaia-shell__logout" onClick={logout} aria-label="Sign out">
            Sign out
          </button>
        </div>
      </header>

      {/* BODY */}
      <div className="gaia-shell__body">

        {/* LEFT RAIL */}
        <nav className="gaia-shell__rail" aria-label="Operating modes">
          {CRYSTAL_ORDER.map(mode => (
            <button
              key={mode}
              className={`gaia-shell__rail-btn${mode === activeMode ? ' gaia-shell__rail-btn--active' : ''}`}
              onClick={() => setActiveMode(mode)}
              aria-pressed={mode === activeMode}
              title={CRYSTAL_DECLARATIONS[mode]}
            >
              <span className="gaia-shell__rail-icon">{MODE_ICONS[mode]}</span>
              <span className="gaia-shell__rail-name">{CRYSTAL_LABELS[mode]}</span>
            </button>
          ))}
        </nav>

        {/* CHAT */}
        <main className="gaia-shell__content">
          <GaiaChat
            token={token}
            gaianSlug="gaia"
            mode={MODE_TO_SLUG[activeMode]}
          />
        </main>

      </div>
    </div>
  );
};

export default GaiaShell;
