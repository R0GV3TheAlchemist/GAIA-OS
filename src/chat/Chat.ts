// GAIA Chat — Perplexity-style streaming chat UI
// Canonical source: C21 (Interface & Shell Grammar), C19 (Color Doctrine)
//
// Architecture:
//   User types → POST /query/stream → SSE stream →
//     citation events  → source cards panel (like Perplexity)
//     token events     → streamed text bubble (real-time)
//     suggestions      → follow-up question chips
//     done             → stream closes, message finalized

import type { ChatMessage, CanonCitation } from './types';
import { API_BASE } from './types';

let _messages: ChatMessage[] = [];
let _isStreaming = false;
let _abortController: AbortController | null = null;

function makeId(): string {
  return `msg-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`;
}

function ts(): string {
  return new Date().toISOString();
}

// ------------------------------------------------------------------ //
//  Mount                                                               //
// ------------------------------------------------------------------ //

export function mountChat(root: HTMLElement): void {
  root.innerHTML = buildChatHTML();
  bindEvents(root);
  appendSystemMessage(root, 'GAIA is online. Constitutional floor held. Ask anything.');
}

// ------------------------------------------------------------------ //
//  HTML Template                                                       //
// ------------------------------------------------------------------ //

function buildChatHTML(): string {
  return `
<div class="gaia-chat" role="main">

  <!-- Header -->
  <div class="chat-header">
    <div class="chat-title">
      <span class="gaia-wordmark">GAIA</span>
      <span class="chat-subtitle">Constitutional Intelligence</span>
    </div>
    <div class="chat-header-actions">
      <button class="hdr-btn" id="btn-clear" title="Clear conversation">✕ Clear</button>
      <button class="hdr-btn" id="btn-stop"  title="Stop streaming" disabled>■ Stop</button>
    </div>
  </div>

  <!-- Message list -->
  <div class="chat-messages" id="chat-messages" aria-live="polite" aria-label="Chat messages">
  </div>

  <!-- Input area -->
  <div class="chat-input-area">
    <div class="input-row">
      <textarea
        id="chat-input"
        rows="1"
        placeholder="Ask GAIA anything…"
        aria-label="Chat input"
        autocomplete="off"
        spellcheck="true"
      ></textarea>
      <button id="btn-send" aria-label="Send">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="22" y1="2" x2="11" y2="13"/>
          <polygon points="22 2 15 22 11 13 2 9 22 2"/>
        </svg>
      </button>
    </div>
    <div class="input-footer">
      <span class="footer-note">Responses are grounded in the GAIA constitutional canon.</span>
      <span class="canon-status" id="canon-status-badge">● Checking…</span>
    </div>
  </div>

</div>
`;
}

// ------------------------------------------------------------------ //
//  Events                                                              //
// ------------------------------------------------------------------ //

function bindEvents(root: HTMLElement): void {
  const input   = root.querySelector<HTMLTextAreaElement>('#chat-input')!;
  const sendBtn = root.querySelector<HTMLButtonElement>('#btn-send')!;
  const stopBtn = root.querySelector<HTMLButtonElement>('#btn-stop')!;
  const clearBtn = root.querySelector<HTMLButtonElement>('#btn-clear')!;

  // Auto-resize textarea
  input.addEventListener('input', () => {
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 160) + 'px';
  });

  // Submit on Enter (Shift+Enter = newline)
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(root, input.value.trim());
    }
  });

  sendBtn.addEventListener('click', () => sendMessage(root, input.value.trim()));

  stopBtn.addEventListener('click', () => {
    _abortController?.abort();
    _isStreaming = false;
    setStreamingUI(root, false);
    appendSystemMessage(root, 'Stream stopped by user.');
  });

  clearBtn.addEventListener('click', () => {
    _messages = [];
    root.querySelector('#chat-messages')!.innerHTML = '';
    appendSystemMessage(root, 'Conversation cleared.');
  });

  // Check backend status
  checkCanonStatus(root);
}

// ------------------------------------------------------------------ //
//  Send & Stream                                                       //
// ------------------------------------------------------------------ //

async function sendMessage(root: HTMLElement, text: string): Promise<void> {
  if (!text || _isStreaming) return;

  const input = root.querySelector<HTMLTextAreaElement>('#chat-input')!;
  input.value = '';
  input.style.height = 'auto';

  // Render user bubble
  const userMsg: ChatMessage = {
    id: makeId(), role: 'user', text,
    citations: [], suggestions: [], timestamp: ts(), streaming: false,
  };
  _messages.push(userMsg);
  renderUserBubble(root, userMsg);

  // Create GAIA response placeholder
  const gaiaMsg: ChatMessage = {
    id: makeId(), role: 'gaia', text: '',
    citations: [], suggestions: [], timestamp: ts(), streaming: true,
  };
  _messages.push(gaiaMsg);
  const msgEl = renderGaiaBubble(root, gaiaMsg);

  _isStreaming = true;
  setStreamingUI(root, true);
  _abortController = new AbortController();

  try {
    const response = await fetch(`${API_BASE}/query/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: text, max_canon_refs: 4 }),
      signal: _abortController.signal,
    });

    if (!response.ok || !response.body) {
      throw new Error(`Server returned ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() ?? '';

      let eventType = '';
      let dataLine = '';

      for (const line of lines) {
        if (line.startsWith('event: ')) {
          eventType = line.slice(7).trim();
        } else if (line.startsWith('data: ')) {
          dataLine = line.slice(6).trim();
          if (eventType && dataLine) {
            handleSSEEvent(root, msgEl, gaiaMsg, eventType, dataLine);
            eventType = '';
            dataLine = '';
          }
        }
      }
    }
  } catch (err: unknown) {
    if (err instanceof Error && err.name === 'AbortError') return;
    const errMsg = err instanceof Error ? err.message : String(err);
    showBackendError(root, msgEl, errMsg);
  } finally {
    gaiaMsg.streaming = false;
    _isStreaming = false;
    setStreamingUI(root, false);
    finalizeMessage(msgEl, gaiaMsg);
  }
}

function handleSSEEvent(
  root: HTMLElement,
  msgEl: HTMLElement,
  msg: ChatMessage,
  event: string,
  data: string
): void {
  try {
    const payload = JSON.parse(data);

    switch (event) {
      case 'citation':
        msg.citations.push(payload as CanonCitation);
        renderCitationCard(msgEl, payload as CanonCitation);
        break;

      case 'token':
        msg.text += payload.text;
        appendToken(msgEl, payload.text);
        scrollToBottom(root);
        break;

      case 'suggestions':
        msg.suggestions = payload.items ?? [];
        renderSuggestions(root, msgEl, msg.suggestions);
        break;

      case 'done':
        msg.canonStatus = payload.canon_status;
        msg.docsSearched = payload.docs_searched;
        msg.refsFound = payload.refs_found;
        renderDoneMeta(msgEl, payload);
        updateCanonBadge(root, payload.canon_status);
        break;

      case 'error':
        showBackendError(root, msgEl, payload.message ?? 'Unknown error');
        break;
    }
  } catch {
    // malformed SSE line — skip silently
  }
}

// ------------------------------------------------------------------ //
//  Render helpers                                                      //
// ------------------------------------------------------------------ //

function renderUserBubble(root: HTMLElement, msg: ChatMessage): void {
  const list = root.querySelector('#chat-messages')!;
  const div = document.createElement('div');
  div.className = 'message-row user-row';
  div.innerHTML = `
<div class="bubble user-bubble">${escHtml(msg.text)}</div>
<div class="msg-time">${formatTime(msg.timestamp)}</div>
  `;
  list.appendChild(div);
  scrollToBottom(root);
}

function renderGaiaBubble(root: HTMLElement, msg: ChatMessage): HTMLElement {
  const list = root.querySelector('#chat-messages')!;
  const row = document.createElement('div');
  row.className = 'message-row gaia-row';
  row.id = msg.id;
  row.innerHTML = `
<div class="gaia-avatar">◉</div>
<div class="gaia-message">
  <div class="citations-panel" id="cp-${msg.id}"></div>
  <div class="bubble gaia-bubble" id="bb-${msg.id}">
    <span class="typing-cursor"></span>
  </div>
  <div class="suggestions-row" id="sr-${msg.id}"></div>
  <div class="msg-meta" id="meta-${msg.id}"></div>
</div>
  `;
  list.appendChild(row);
  scrollToBottom(root);
  return row;
}

function appendToken(msgEl: HTMLElement, token: string): void {
  const bb = msgEl.querySelector<HTMLElement>('[id^="bb-"]')!;
  const cursor = bb.querySelector('.typing-cursor');
  const span = document.createElement('span');
  span.textContent = token;
  if (cursor) bb.insertBefore(span, cursor);
  else bb.appendChild(span);
}

function renderCitationCard(msgEl: HTMLElement, c: CanonCitation): void {
  const panel = msgEl.querySelector<HTMLElement>('[id^="cp-"]')!;
  const card = document.createElement('div');
  card.className = 'citation-card';
  card.innerHTML = `
<div class="citation-id">${escHtml(c.doc_id)}</div>
<div class="citation-title">${escHtml(c.title)}</div>
<div class="citation-excerpt">${escHtml(c.excerpt)}</div>
  `;
  panel.appendChild(card);
}

function renderSuggestions(root: HTMLElement, msgEl: HTMLElement, items: string[]): void {
  const sr = msgEl.querySelector<HTMLElement>('[id^="sr-"]')!;
  if (!items.length) return;
  sr.innerHTML = items.map(s =>
    `<button class="suggestion-chip">${escHtml(s)}</button>`
  ).join('');
  // Clicking a chip sends it as the next query
  sr.querySelectorAll<HTMLButtonElement>('.suggestion-chip').forEach(btn => {
    btn.addEventListener('click', () => sendMessage(root, btn.textContent ?? ''));
  });
}

function renderDoneMeta(msgEl: HTMLElement, payload: Record<string, unknown>): void {
  const meta = msgEl.querySelector<HTMLElement>('[id^="meta-"]')!;
  const status = payload.canon_status as string ?? 'unknown';
  const searched = payload.docs_searched as number ?? 0;
  const refs = payload.refs_found as number ?? 0;
  meta.innerHTML = `
<span class="meta-dot canon-${status}"></span>
<span class="meta-text">Canon ${status} · ${searched} docs searched · ${refs} refs cited</span>
  `;
  // Remove typing cursor
  msgEl.querySelector('.typing-cursor')?.remove();
}

function finalizeMessage(msgEl: HTMLElement, msg: ChatMessage): void {
  msgEl.querySelector('.typing-cursor')?.remove();
  if (!msg.text && !msg.citations.length) {
    const bb = msgEl.querySelector<HTMLElement>('[id^="bb-"]')!;
    bb.innerHTML = '<span class="muted-text">No response received. Is the GAIA server running?</span>';
  }
}

function showBackendError(root: HTMLElement, msgEl: HTMLElement, error: string): void {
  const bb = msgEl.querySelector<HTMLElement>('[id^="bb-"]')!;
  bb.innerHTML = `
<div class="backend-error">
  <span class="err-label">⚠ Backend unreachable</span>
  <span class="err-detail">${escHtml(error)}</span>
  <span class="err-hint">Start the server: <code>python core/server.py</code></span>
</div>
  `;
}

function appendSystemMessage(root: HTMLElement, text: string): void {
  const list = root.querySelector('#chat-messages')!;
  const div = document.createElement('div');
  div.className = 'system-msg';
  div.textContent = text;
  list.appendChild(div);
  scrollToBottom(root);
}

// ------------------------------------------------------------------ //
//  UI State                                                            //
// ------------------------------------------------------------------ //

function setStreamingUI(root: HTMLElement, streaming: boolean): void {
  const sendBtn = root.querySelector<HTMLButtonElement>('#btn-send')!;
  const stopBtn = root.querySelector<HTMLButtonElement>('#btn-stop')!;
  const input   = root.querySelector<HTMLTextAreaElement>('#chat-input')!;
  sendBtn.disabled = streaming;
  stopBtn.disabled = !streaming;
  input.disabled   = streaming;
}

async function checkCanonStatus(root: HTMLElement): Promise<void> {
  const badge = root.querySelector<HTMLElement>('#canon-status-badge')!;
  try {
    const res = await fetch(`${API_BASE}/canon/status`, { signal: AbortSignal.timeout(3000) });
    const data = await res.json();
    const s = data.status ?? 'unknown';
    badge.className = `canon-status canon-badge-${s}`;
    badge.textContent = `● Canon ${s.toUpperCase()} — ${data.loaded_count ?? 0} docs`;
    updateCanonBadge(root, s);
  } catch {
    badge.className = 'canon-status canon-badge-offline';
    badge.textContent = '○ Canon offline — start server';
  }
}

function updateCanonBadge(root: HTMLElement, status: string): void {
  const badge = root.querySelector<HTMLElement>('#canon-status-badge')!;
  if (!badge) return;
  badge.className = `canon-status canon-badge-${status}`;
}

function scrollToBottom(root: HTMLElement): void {
  const list = root.querySelector<HTMLElement>('#chat-messages')!;
  list.scrollTop = list.scrollHeight;
}

function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function escHtml(s: string): string {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
