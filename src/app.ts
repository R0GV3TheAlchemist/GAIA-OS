// GAIA App — Top-level layout with tab navigation
// Views: SEARCH | GAIAN | CHAT | SHELL | MEMORY | NOOSPHERE | CANON | QUANTUM | DIMENSIONS | ARCHETYPES
// Canon Ref: C42, C43, C44

import './app.css';
import './search/Search.css';
import './shell/Shell.css';
import './chat/Chat.css';
import './memory/Memory.css';
import './noosphere/NoosphereTab.css';
import './canon/CanonTab.css';
import './dimensions/DimensionalMonitor.css';
import './gaian/GaianHome.css';
import { mountSearch }             from './search/Search';
import { mountShell }              from './shell/Shell';
import { mountChat }               from './chat/Chat';
import { mountMemory }             from './memory/Memory';
import { mountGaianHome, GaianHome } from './gaian/GaianHome';
import {
  mountNoosphereTab,
  unmountNoosphereTab,
} from './noosphere';
import { mountCanonTab }           from './canon/CanonTab';
import { mountQuantumTab }         from './quantum/QuantumTab';
import { mountDimensionalMonitor } from './dimensions/DimensionalMonitor';
import { mountArchetypalTab }      from './archetypes/ArchetypalTab';
import { appDataDir, join, resolveResource } from '@tauri-apps/api/path';
import { exists, mkdir, copyFile, readDir }  from '@tauri-apps/plugin-fs';
import { listen }                  from '@tauri-apps/api/event';
import { checkForUpdates }         from './updater';
import { logInfo, logWarn, logError } from './diagnostics';
import { API_BASE } from './config';

export { API_BASE };

// ── First-launch: seed %APPDATA%\GAIA\canon\ from bundled resources ────
async function ensureAppDataDirs(): Promise<void> {
  try {
    const appData = await appDataDir();
    const dirs = ['canon', 'logs', 'config'];
    for (const dir of dirs) {
      const dirPath = await join(appData, dir);
      if (!(await exists(dirPath))) {
        await mkdir(dirPath, { recursive: true });
        logInfo('app', `Created AppData dir: ${dir}`);
      }
    }
    const canonDest = await join(appData, 'canon');
    const canonDestEntries = await readDir(canonDest);
    if (canonDestEntries.length === 0) {
      try {
        const canonSrc = await resolveResource('canon');
        const srcEntries = await readDir(canonSrc);
        for (const entry of srcEntries) {
          const srcFile  = await join(canonSrc,  entry.name);
          const destFile = await join(canonDest, entry.name);
          await copyFile(srcFile, destFile);
        }
        logInfo('app', `Seeded ${srcEntries.length} canon docs to AppData`);
      } catch (e) {
        logWarn('app', 'Could not seed canon docs (may not be bundled yet)', e);
      }
    }
  } catch (e) {
    logError('app', 'ensureAppDataDirs failed', e);
  }
}

// ── Updater ─────────────────────────────────────────────────────────────────
async function initUpdater(): Promise<void> {
  const unlisten = await listen('sidecar:ready', async () => {
    unlisten();
    logInfo('updater', 'sidecar:ready received — scheduling update check');
    await new Promise(r => setTimeout(r, 2000));
    await checkForUpdates();
  });
}

// ── Helper: switch active tab view ──────────────────────────────────────────
function switchView(view: string, _activeView: { current: string }): void {
  document.querySelectorAll<HTMLButtonElement>('.tab-btn').forEach(b => {
    b.classList.toggle('active', b.dataset.view === view);
  });
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.getElementById(`view-${view}`)?.classList.add('active');
  logInfo('app', `View switched: ${_activeView.current} → ${view}`);
  _activeView.current = view;
}

export class App {
  constructor() {
    logInfo('app', 'GAIA App initialising');
    this.mount();
    ensureAppDataDirs();
    initUpdater();
  }

  private mount() {
    const root = document.querySelector<HTMLDivElement>('#app')!;
    root.innerHTML = `
<div class="gaia-app">
  <nav class="tab-nav">
    <button class="tab-btn active" data-view="gaian">&#9632; Home</button>
    <button class="tab-btn"        data-view="search">&#128269; Search</button>
    <button class="tab-btn"        data-view="chat">&#9670; Chat</button>
    <button class="tab-btn"        data-view="shell">&gt; Shell</button>
    <button class="tab-btn"        data-view="memory">&#9638; Memory</button>
    <button class="tab-btn"        data-view="noosphere">&#127760; Noosphere</button>
    <button class="tab-btn"        data-view="canon">&#128220; Canon</button>
    <button class="tab-btn"        data-view="quantum">&#10731; Quantum</button>
    <button class="tab-btn"        data-view="dimensions">&#11042; Dimensions</button>
    <button class="tab-btn"        data-view="archetypes">&#9672; Archetypes</button>
  </nav>
  <div class="view-container">
    <div id="view-gaian"       class="view active"></div>
    <div id="view-search"      class="view"></div>
    <div id="view-chat"        class="view"></div>
    <div id="view-shell"       class="view"></div>
    <div id="view-memory"      class="view"></div>
    <div id="view-noosphere"   class="view"></div>
    <div id="view-canon"       class="view"></div>
    <div id="view-quantum"     class="view"></div>
    <div id="view-dimensions"  class="view"></div>
    <div id="view-archetypes"  class="view"></div>
  </div>
</div>
`;

    // Track active view
    const activeView = { current: 'gaian' };

    // ── Mount Home (GaianHome replaces mountGaianChat) ──────────────────────
    // The dock's onNavigate callback drives tab switching directly,
    // so clicking Chat/Memory/Search/Shell in the orb screen navigates there.
    let gaianHome: GaianHome | null = mountGaianHome(
      document.getElementById('view-gaian')!,
      (target) => {
        if (target === activeView.current) return;
        if (activeView.current === 'noosphere') unmountNoosphereTab();
        teardowns[activeView.current]?.();
        switchView(target, activeView);
        handleLazyMount(target);
      },
    );

    // ── Eager mounts ────────────────────────────────────────────────────────
    mountSearch(document.getElementById('view-search')!);
    mountChat(document.getElementById('view-chat')!);
    mountShell(document.getElementById('view-shell')!);
    mountMemory(document.getElementById('view-memory')!);
    mountNoosphereTab({ root: document.getElementById('view-noosphere')!, apiBase: API_BASE });

    // ── Lazy-mount flags ─────────────────────────────────────────────────────
    let canonMounted      = false;
    let quantumMounted    = false;
    let dimensionsMounted = false;
    let archetypesMounted = false;

    // Teardown registry
    const teardowns: Record<string, (() => void) | null> = {
      gaian:      () => { gaianHome?.dispose(); gaianHome = null; },
      dimensions: null,
      archetypes: null,
    };

    function handleLazyMount(view: string): void {
      if (view === 'noosphere') {
        mountNoosphereTab({ root: document.getElementById('view-noosphere')!, apiBase: API_BASE });
      }
      if (view === 'canon' && !canonMounted) {
        mountCanonTab(document.getElementById('view-canon')!);
        canonMounted = true;
      }
      if (view === 'quantum' && !quantumMounted) {
        mountQuantumTab(document.getElementById('view-quantum')!);
        quantumMounted = true;
      }
      if (view === 'dimensions' && !dimensionsMounted) {
        teardowns.dimensions = mountDimensionalMonitor(document.getElementById('view-dimensions')!);
        dimensionsMounted = true;
      }
      if (view === 'archetypes' && !archetypesMounted) {
        teardowns.archetypes = mountArchetypalTab(document.getElementById('view-archetypes')!);
        archetypesMounted = true;
      }
    }

    logInfo('app', 'All views mounted — Home is primary');

    // ── Tab nav click handler ────────────────────────────────────────────────
    document.querySelectorAll<HTMLButtonElement>('.tab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const view = btn.dataset.view!;
        if (view === activeView.current) return;

        if (activeView.current === 'noosphere') unmountNoosphereTab();
        teardowns[activeView.current]?.();

        switchView(view, activeView);
        handleLazyMount(view);
      });
    });
  }
}
