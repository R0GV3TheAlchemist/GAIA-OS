// GAIA App — Top-level layout with tab navigation
// Renders SHELL and CHAT as switchable views

import './shell/Shell.css';
import './chat/Chat.css';
import { mountShell } from './shell/Shell';
import { mountChat }  from './chat/Chat';

const root = document.querySelector<HTMLDivElement>('#app')!;

root.innerHTML = `
<div class="gaia-app">
  <nav class="tab-nav">
    <button class="tab-btn active" data-view="chat">&#9670; Chat</button>
    <button class="tab-btn"        data-view="shell">❯ Shell</button>
  </nav>
  <div class="view-container">
    <div id="view-chat"  class="view active"></div>
    <div id="view-shell" class="view"></div>
  </div>
</div>
`;

// Add app-level styles
const style = document.createElement('style');
style.textContent = `
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@400;500;600&display=swap');
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #0F1117; overflow: hidden; }

  .gaia-app {
    display: flex;
    flex-direction: column;
    height: 100vh;
  }

  .tab-nav {
    display: flex;
    gap: 0;
    background: #1A1D27;
    border-bottom: 1px solid #2A2D3A;
    padding: 0 16px;
    flex-shrink: 0;
  }

  .tab-btn {
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    color: #6B7280;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    padding: 10px 20px;
    cursor: pointer;
    letter-spacing: 0.05em;
    transition: color 0.15s, border-color 0.15s;
  }
  .tab-btn:hover  { color: #fff; }
  .tab-btn.active { color: #2D6A4F; border-bottom-color: #2D6A4F; }

  .view-container {
    flex: 1;
    overflow: hidden;
    position: relative;
  }

  .view {
    position: absolute;
    inset: 0;
    display: none;
  }
  .view.active { display: flex; flex-direction: column; }
`;
document.head.appendChild(style);

// Mount both views
mountChat(document.getElementById('view-chat')!);
mountShell(document.getElementById('view-shell')!);

// Tab switching
document.querySelectorAll<HTMLButtonElement>('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const view = btn.dataset.view!;
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById(`view-${view}`)!.classList.add('active');
  });
});
