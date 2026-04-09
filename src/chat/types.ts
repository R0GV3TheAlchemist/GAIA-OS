// GAIA Chat — Type Definitions
// Connects to the streaming SSE backend at POST /query/stream
// Canonical source: C21 (Interface & Shell Grammar), C17 (Memory), C20 (Source Triage)

export type MessageRole = 'user' | 'gaia' | 'system';

export type SSEEventType = 'token' | 'citation' | 'suggestions' | 'done' | 'error';

export interface CanonCitation {
  doc_id: string;
  title: string;
  excerpt: string;
}

export interface ChatMessage {
  id: string;
  role: MessageRole;
  text: string;          // accumulated token stream
  citations: CanonCitation[];
  suggestions: string[];
  timestamp: string;
  streaming: boolean;    // true while tokens are still arriving
  canonStatus?: string;  // green | yellow | red
  docsSearched?: number;
  refsFound?: number;
}

export interface ChatState {
  messages: ChatMessage[];
  isStreaming: boolean;
  inputValue: string;
  error: string | null;
}

export const API_BASE = 'http://127.0.0.1:8008';
