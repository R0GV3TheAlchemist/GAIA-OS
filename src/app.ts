// GAIA App — Top-level layout with tab navigation
// Views: SEARCH | CHAT | GAIAN | SHELL | MEMORY | NOOSPHERE
// Canon Ref: C43, C44

import './app.css';
import './search/Search.css';
import './shell/Shell.css';
import './chat/Chat.css';
import './memory/Memory.css';
import './noosphere/NoosphereTab.css';
import { mountSearch }          from './search/Search';
import { mountShell }           from './shell/Shell';
import { mountChat }            from './chat/Chat';
import { mountMemory }          from './memory/Memory';
import { mountGaianChat }       from './gaian/GaianChatView';
import {
  mountNoosphereTab,
  unmountNoosphereTab,
} from './noosphere';

const BASE_URL = (import.meta as Record<string,unknown>).env
  ? ((import.meta as Record<string,unknown>).env as Record<string,string>).VITE_API_BASE ?? 'http://localhost:8008'
  : 'http://localhost:8008';

export const API_BASE = BASE_URL;

const root = document.querySelector<HTMLDivElement>('#app')!;

root.innerHTML = `
<div class="gaia-app">
  <nav class="tab-nav">
    <button class="tab-btn active" data-view="search">&#128269; Search</button>
    <button class="tab-btn"        data-view="gaian">&#9672; GAIAN</button>
    <button class="tab-btn"        data-view="chat">&#9670; Chat</button>
    <button class="tab-btn"        data-view="shell">&gt; Shell</button>
    <button class="tab-btn"        data-view="memory">&#9638; Memory</button>
    <button class="tab-btn"        data-view="noosphere">&#127760; Noosphere</button>
  </nav>
  <div class="view-container">
    <div id="view-search"     class="view active"></div>
    <div id="view-gaian"      class="view"></div>
    <div id="view-chat"       class="view"></div>
    <div id="view-shell"      class="view"></div>
    <div id="view-memory"     class="view"></div>
    <div id="view-noosphere"  class="view"></div>
  </div>
</div>
`;

// ── Mount all static views ────────────────────────────────────────────
mountSearch(document.getElementById('view-search')!);
mountGaianChat(document.getElementById('view-gaian')!);
mountChat(document.getElementById('view-chat')!);
mountShell(document.getElementById('view-shell')!);
mountMemory(document.getElementById('view-memory')!);

// Noosphere Tab has an SSE lifecycle — mount on boot; the tab-switch
// handler below unmounts/remounts it as the user navigates in and out.
mountNoosphereTab(document.getElementById('view-noosphere')!, { apiBase: API_BASE });

// ── Tab switching ─────────────────────────────────────────────────────
let _activeView = 'search';

document.querySelectorAll<HTMLButtonElement>('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const view = btn.dataset.view!;
    if (view === _activeView) return;

    // Tear down SSE connection when leaving Noosphere
    if (_activeView === 'noosphere') {
      unmountNoosphereTab(document.getElementById('view-noosphere')!);
    }

    // Update nav + view visibility
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById(`view-${view}`)!.classList.add('active');
    _activeView = view;

    // Re-establish SSE connection when entering Noosphere
    if (view === 'noosphere') {
      mountNoosphereTab(document.getElementById('view-noosphere')!, { apiBase: API_BASE });
    }
  });
});
