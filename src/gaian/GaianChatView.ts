import './gaian-chat.css';
import '../gaian/birth.css';
import '../gaian/gaian.css';
import { GaianBirth, type GaianBirthResult } from './GaianBirth';
import { mountGaianPicker } from './GaianPicker';
import { EngineStatePanel, type EngineStateSnapshot } from '../chat/EngineStatePanel';
import '../chat/engine-state.css';
import { API_BASE } from '../app';

const SLUG_KEY    = 'gaia_active_slug';
const SESSION_KEY = 'gaia_session_id';

export class GaianChatView {
  private root: HTMLElement;
  private slug: string | null = null;
  private gaianName = '';
  private isStreaming = false;
  private abortCtrl: AbortController | null = null;
  private enginePanel: EngineStatePanel | null = null;
  private sessionId: string;
  private inputReady = false;

  constructor(root: HTMLElement) {
    this.root      = root;
    this.sessionId = this._getOrCreateSession();
    this.slug      = localStorage.getItem(SLUG_KEY);
  }

  mount(): void {
    if (this.slug) {
      this.gaianName = this.slug;
      this._mountChatShell(false);
    } else {
      this._mountBirth();
    }
  }

  private _mountBirth(): void {
    this.root.innerHTML = '<div id="gc-birth-container" class="gc-birth-host"></div>';
    const container = this.root.querySelector<HTMLElement>('#gc-birth-container')!;
    const birth = new GaianBirth(container, this.sessionId, (result) => {
      this._onBorn(result);
    });
    birth.mount();
  }

  private _onBorn(result: GaianBirthResult): void {
    this.slug      = result.slug;
    this.gaianName = result.name;
    localStorage.setItem(SLUG_KEY, result.slug);
    this._mountChatShell(true, result);
  }

  private _mountChatShell(isNewBorn: boolean, birthResult?: GaianBirthResult): void {
    this.root.innerHTML = this._buildShellHTML();
    const espSlot = this.root.querySelector<HTMLElement>('#gc-esp-slot')!;
    this.enginePanel = new EngineStatePanel(espSlot);
    this.enginePanel.mount();
    this._updateHeader();
    this._bindShellEvents();
    this._setInputReady(false);

    if (isNewBorn && birthResult) {
      this._playFirstWords(birthResult.first_words, birthResult.name);
    } else {
      this._appendSystemNote(`Resuming with ${this.gaianName || this.slug}.`);
      this._fetchRuntimeStatus();
      this._setInputReady(true);
    }
  }

  private _playFirstWords(text: string, name: string): void {
    this.gaianName = name;
    this._updateHeader();
    const msgEl  = this._appendGaianBubble(true);
    const bb     = msgEl.querySelector<HTMLElement>('.gc-bubble')!;
    const cursor = bb.querySelector<HTMLElement>('.gc-cursor')!;
    let i = 0;
    const CHAR_MS = 26;
    const typeNext = () => {
      if (i < text.length) {
        cursor.insertAdjacentText('beforebegin', text[i]);
        i++;
        setTimeout(typeNext, CHAR_MS + (Math.random() * 14 - 7));
      } else {
        cursor.classList.add('gc-cursor--done');
        setTimeout(() => {
          cursor.remove();
          this._setInputReady(true);
          this.root.querySelector<HTMLTextAreaElement>('#gc-input')?.focus();
        }, 600);
      }
    };
    setTimeout(typeNext, 400);
  }

  private async _send(text: string): Promise<void> {
    if (!text || this.isStreaming || !this.inputReady || !this.slug) return;

    const input = this.root.querySelector<HTMLTextAreaElement>('#gc-input')!;
    input.value = '';
    input.style.height = 'auto';

    this._appendUserBubble(text);
    const msgEl = this._appendGaianBubble(true);
    this.isStreaming = true;
    this._setStreamingUI(true);
    this.abortCtrl = new AbortController();

    try {
      const res = await fetch(`${API_BASE}/gaians/${this.slug}/chat`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ message: text, session_id: this.sessionId }),
        signal:  this.abortCtrl.signal,
      });

      if (!res.ok || !res.body) throw new Error(`Server ${res.status}`);
      const reader  = res.body.getReader();
      const decoder = new TextDecoder();
      let buf = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buf += decoder.decode(value, { stream: true });
        const lines = buf.split('\n');
        buf = lines.pop() ?? '';

        let eventType = '';
        for (const line of lines) {
          if      (line.startsWith('event: ')) eventType = line.slice(7).trim();
          else if (line.startsWith('data: ') && eventType) {
            this._handleSSE(msgEl, eventType, line.slice(6).trim());
            eventType = '';
          }
        }
      }
    } catch (err: unknown) {
      if (err instanceof Error && err.name === 'AbortError') return;
      this._showBubbleError(msgEl, err instanceof Error ? err.message : String(err));
    } finally {
      this.isStreaming = false;
      this._setStreamingUI(false);
      this._finalizeBubble(msgEl);
    }
  }

  private _handleSSE(msgEl: HTMLElement, event: string, data: string): void {
    try {
      const payload = JSON.parse(data);
      switch (event) {
        case 'token':
          this._appendToken(msgEl, payload.text ?? payload);
          break;
        case 'engine_state':
          if (this.enginePanel) this.enginePanel.update(payload as EngineStateSnapshot);
          if (payload.gaian_name && payload.gaian_name !== this.gaianName) {
            this.gaianName = payload.gaian_name;
            this._updateHeader();
          }
          this._updateSettlingBadge(payload as EngineStateSnapshot);
          break;
        case 'done':
          this._removeCursor(msgEl);
          break;
      }
    } catch {}
  }

  private async _fetchRuntimeStatus(): Promise<void> {
    if (!this.slug) return;
    try {
      const res = await fetch(`${API_BASE}/gaians/${this.slug}/runtime-status`, { signal: AbortSignal.timeout(3000) });
      if (!res.ok) return;
      const data = await res.json();
      if (data.gaian_name) { this.gaianName = data.gaian_name; this._updateHeader(); }
      if (this.enginePanel && data.engine_state) {
        this.enginePanel.update(data.engine_state as EngineStateSnapshot);
        this._updateSettlingBadge(data.engine_state as EngineStateSnapshot);
      }
    } catch {}
  }

  private _buildShellHTML(): string { return `<div class="gc-shell"><div class="gc-header"><div class="gc-header__identity"><span class="gc-element-dot" id="gc-element-dot"></span><span class="gc-gaian-name" id="gc-gaian-name">${_esc(this.gaianName || this.slug || 'GAIAN')}</span><span class="gc-settling-badge" id="gc-settling-badge">Fluid</span></div><div class="gc-header__actions"><div id="gc-esp-slot"></div><button class="gc-hdr-btn" id="gc-btn-switch" title="Switch or birth a new GAIAN">⇄ Switch</button><button class="gc-hdr-btn" id="gc-btn-clear" title="Clear conversation">✕</button><button class="gc-hdr-btn" id="gc-btn-stop" title="Stop" disabled>■</button></div></div><div class="gc-messages" id="gc-messages" aria-live="polite"></div><div class="gc-input-area"><div class="gc-input-row"><textarea id="gc-input" class="gc-textarea" rows="1" placeholder="Speak to ${_esc(this.gaianName || 'your GAIAN')}…" aria-label="Message your GAIAN" autocomplete="off" spellcheck="true" disabled></textarea><button id="gc-btn-send" class="gc-send-btn" aria-label="Send"></button></div><div class="gc-input-footer"><span class="gc-footer-note" id="gc-footer-slug">◈ ${_esc(this.slug ?? '')}</span></div></div></div>`; }
  private _appendUserBubble(text: string): void { const list = this.root.querySelector('#gc-messages')!; const row = document.createElement('div'); row.className = 'gc-row gc-row--user'; row.innerHTML = `<div class="gc-bubble gc-bubble--user">${_esc(text)}</div>`; list.appendChild(row); this._scroll(); }
  private _appendGaianBubble(withCursor = false): HTMLElement { const list = this.root.querySelector('#gc-messages')!; const row = document.createElement('div'); row.className = 'gc-row gc-row--gaian'; row.innerHTML = `<div class="gc-avatar">◉</div><div class="gc-bubble gc-bubble--gaian">${withCursor ? '<span class="gc-cursor"></span>' : ''}</div>`; list.appendChild(row); this._scroll(); return row; }
  private _appendToken(msgEl: HTMLElement, token: string): void { const bb = msgEl.querySelector<HTMLElement>('.gc-bubble--gaian')!; const cursor = bb.querySelector('.gc-cursor'); const span = document.createElement('span'); span.textContent = token; cursor ? bb.insertBefore(span, cursor) : bb.appendChild(span); this._scroll(); }
  private _appendSystemNote(text: string): void { const list = this.root.querySelector('#gc-messages')!; if (!list) return; const div = document.createElement('div'); div.className = 'gc-system-note'; div.textContent = text; list.appendChild(div); this._scroll(); }
  private _removeCursor(msgEl: HTMLElement): void { msgEl.querySelector('.gc-cursor')?.remove(); }
  private _finalizeBubble(msgEl: HTMLElement): void { this._removeCursor(msgEl); const bb = msgEl.querySelector<HTMLElement>('.gc-bubble--gaian')!; if (!bb.textContent?.trim()) { bb.innerHTML = '<span class="gc-muted">No response. Is the GAIA server running?</span>'; } }
  private _showBubbleError(msgEl: HTMLElement, error: string): void { const bb = msgEl.querySelector<HTMLElement>('.gc-bubble--gaian')!; bb.innerHTML = `<div class="gc-error">⚠ ${_esc(error)}<br><small>Start server: <code>python core/server.py</code></small></div>`; }
  private _updateHeader(): void { const nameEl = this.root.querySelector<HTMLElement>('#gc-gaian-name'); const footerEl = this.root.querySelector<HTMLElement>('#gc-footer-slug'); const inputEl = this.root.querySelector<HTMLTextAreaElement>('#gc-input'); if (nameEl) nameEl.textContent = this.gaianName || this.slug || 'GAIAN'; if (footerEl) footerEl.textContent = `◈ ${this.slug ?? ''}`; if (inputEl) inputEl.placeholder = `Speak to ${this.gaianName || 'your GAIAN'}…`; }
  private _updateSettlingBadge(s: EngineStateSnapshot): void { const dot = this.root.querySelector<HTMLElement>('#gc-element-dot'); const badge = this.root.querySelector<HTMLElement>('#gc-settling-badge'); if (!dot || !badge) return; const ELEMENT_COLORS: Record<string, string> = { fire:'#f59e0b', water:'#3b82f6', air:'#d1d5db', earth:'#22c55e', aether:'#a78bfa', metal:'#94a3b8', wood:'#4ade80', light:'#fde68a', dark:'#6366f1', quintessence:'#e879f9' }; const color = ELEMENT_COLORS[s.element?.toLowerCase()] ?? '#6b7280'; dot.style.background = color; dot.style.boxShadow = `0 0 7px ${color}`; const phaseLabels: Record<string, string> = { unsettled:'Fluid', narrowing:'Narrowing', crystallising:'Crystallising', settled: s.daemon_form ? `Set · ${s.daemon_form}` : 'Settled' }; badge.textContent = phaseLabels[s.settling_phase?.toLowerCase()] ?? s.settling_phase ?? 'Fluid'; badge.className = `gc-settling-badge gc-settling-badge--${(s.settling_phase ?? 'fluid').toLowerCase()}`; }
  private _bindShellEvents(): void { const input = this.root.querySelector<HTMLTextAreaElement>('#gc-input')!; const sendBtn = this.root.querySelector<HTMLButtonElement>('#gc-btn-send')!; const stopBtn = this.root.querySelector<HTMLButtonElement>('#gc-btn-stop')!; const clearBtn = this.root.querySelector<HTMLButtonElement>('#gc-btn-clear')!; const switchBtn = this.root.querySelector<HTMLButtonElement>('#gc-btn-switch')!; input.addEventListener('input', () => { input.style.height = 'auto'; input.style.height = Math.min(input.scrollHeight, 140) + 'px'; }); input.addEventListener('keydown', (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); this._send(input.value.trim()); } }); sendBtn.addEventListener('click', () => this._send(input.value.trim())); stopBtn.addEventListener('click', () => { this.abortCtrl?.abort(); this.isStreaming = false; this._setStreamingUI(false); this._appendSystemNote('Stream stopped.'); }); clearBtn.addEventListener('click', () => { this.root.querySelector('#gc-messages')!.innerHTML = ''; this._appendSystemNote('Conversation cleared.'); }); switchBtn.addEventListener('click', () => this._mountPicker()); }
  private _mountPicker(): void { this.root.innerHTML = '<div id="gc-picker-host" class="gc-birth-host"></div>'; const host = this.root.querySelector<HTMLElement>('#gc-picker-host')!; void mountGaianPicker(host, this.sessionId, (gaian) => { this.slug = gaian.slug; this.gaianName = gaian.name; localStorage.setItem(SLUG_KEY, gaian.slug); this._mountChatShell(false); }, () => { localStorage.removeItem(SLUG_KEY); this.slug = null; this.gaianName = ''; this._mountBirth(); }); }
  private _setInputReady(ready: boolean): void { this.inputReady = ready; const input = this.root.querySelector<HTMLTextAreaElement>('#gc-input'); const sendBtn = this.root.querySelector<HTMLButtonElement>('#gc-btn-send'); if (input) input.disabled = !ready; if (sendBtn) sendBtn.disabled = !ready; }
  private _setStreamingUI(streaming: boolean): void { const sendBtn = this.root.querySelector<HTMLButtonElement>('#gc-btn-send'); const stopBtn = this.root.querySelector<HTMLButtonElement>('#gc-btn-stop'); const input = this.root.querySelector<HTMLTextAreaElement>('#gc-input'); if (sendBtn) sendBtn.disabled = streaming; if (stopBtn) stopBtn.disabled = !streaming; if (input) input.disabled = streaming; }
  private _scroll(): void { const list = this.root.querySelector<HTMLElement>('#gc-messages'); if (list) list.scrollTop = list.scrollHeight; }
  private _getOrCreateSession(): string { let id = sessionStorage.getItem(SESSION_KEY); if (!id) { id = `sess-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`; sessionStorage.setItem(SESSION_KEY, id); } return id; }
}

export function mountGaianChat(root: HTMLElement): void { const view = new GaianChatView(root); view.mount(); }
function _esc(s: string): string { return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
