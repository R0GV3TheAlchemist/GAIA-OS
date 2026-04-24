// GAIA Dev Suite — Bottom Panel (Terminal | Logs | Tests | Diagnostics)

import { mountDiagnostics } from '../diagnostics';

export function mountBottomPanel(root: HTMLElement): void {
  root.innerHTML = `
    <div class="bottom-panel">
      <div class="bottom-tabs">
        <button class="btab active" data-tab="terminal">Terminal</button>
        <button class="btab" data-tab="logs">Logs</button>
        <button class="btab" data-tab="tests">Tests</button>
        <button class="btab" data-tab="diagnostics">&#9881; Diagnostics</button>
      </div>
      <div class="bottom-content">
        <div id="btab-terminal"    class="btab-pane active">
          <div class="terminal-placeholder">[ xterm.js terminal — Phase 4.4 ]</div>
        </div>
        <div id="btab-logs"        class="btab-pane">
          <div class="logs-placeholder">[ Log stream — Phase 4.5 ]</div>
        </div>
        <div id="btab-tests"       class="btab-pane">
          <div class="tests-placeholder">[ Test runner — Phase 4.8 ]</div>
        </div>
        <div id="btab-diagnostics" class="btab-pane"></div>
      </div>
    </div>
  `;

  let diagMounted = false;

  root.querySelectorAll<HTMLButtonElement>('.btab').forEach(btn => {
    btn.addEventListener('click', () => {
      root.querySelectorAll('.btab').forEach(b => b.classList.remove('active'));
      root.querySelectorAll('.btab-pane').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      const pane = document.getElementById(`btab-${btn.dataset.tab}`);
      pane?.classList.add('active');

      // Lazy-mount diagnostics panel on first open
      if (btn.dataset.tab === 'diagnostics' && !diagMounted) {
        const diagRoot = document.getElementById('btab-diagnostics');
        if (diagRoot) { mountDiagnostics(diagRoot); diagMounted = true; }
      }
    });
  });
}
