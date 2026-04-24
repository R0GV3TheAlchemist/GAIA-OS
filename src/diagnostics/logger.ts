// GAIA Structured Logger
// Writes JSON-lines to AppData/GAIA/logs/gaia-YYYY-MM-DD.log
// Canon Ref: C43 — Sovereign Distribution

import { appDataDir, join } from '@tauri-apps/api/path';
import { writeTextFile, exists, mkdir } from '@tauri-apps/plugin-fs';

export type LogLevel = 'DEBUG' | 'INFO' | 'WARN' | 'ERROR';

export interface LogEntry {
  ts:      string;     // ISO 8601
  level:   LogLevel;
  module:  string;
  msg:     string;
  data?:   unknown;
}

// In-memory ring buffer — last 500 entries for the diagnostics panel
const _buffer: LogEntry[] = [];
const BUFFER_MAX = 500;

let _logPath: string | null = null;

async function getLogPath(): Promise<string> {
  if (_logPath) return _logPath;
  const appData = await appDataDir();
  const logsDir = await join(appData, 'logs');
  if (!(await exists(logsDir))) {
    await mkdir(logsDir, { recursive: true });
  }
  const date = new Date().toISOString().slice(0, 10); // YYYY-MM-DD
  _logPath = await join(logsDir, `gaia-${date}.log`);
  return _logPath;
}

export async function log(
  level: LogLevel,
  module: string,
  msg: string,
  data?: unknown,
): Promise<void> {
  const entry: LogEntry = {
    ts:     new Date().toISOString(),
    level,
    module,
    msg,
    ...(data !== undefined ? { data } : {}),
  };

  // Ring buffer
  _buffer.push(entry);
  if (_buffer.length > BUFFER_MAX) _buffer.shift();

  // Console mirror
  const prefix = `[GAIA:${module}]`;
  if      (level === 'ERROR') console.error(prefix, msg, data ?? '');
  else if (level === 'WARN')  console.warn (prefix, msg, data ?? '');
  else                        console.info (prefix, msg, data ?? '');

  // Persist to disk (best-effort — never throws)
  try {
    const path = await getLogPath();
    await writeTextFile(path, JSON.stringify(entry) + '\n', { append: true });
  } catch (e) {
    console.warn('[GAIA:logger] disk write failed:', e);
  }
}

// Convenience wrappers
export const logDebug = (m: string, msg: string, d?: unknown) => log('DEBUG', m, msg, d);
export const logInfo  = (m: string, msg: string, d?: unknown) => log('INFO',  m, msg, d);
export const logWarn  = (m: string, msg: string, d?: unknown) => log('WARN',  m, msg, d);
export const logError = (m: string, msg: string, d?: unknown) => log('ERROR', m, msg, d);

/** Return a copy of the in-memory ring buffer (newest last). */
export function getLogBuffer(): LogEntry[] {
  return [..._buffer];
}
