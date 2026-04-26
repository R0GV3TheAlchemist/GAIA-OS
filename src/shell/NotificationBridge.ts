/**
 * NotificationBridge.ts — P4 Proactive Notifications
 *
 * Polls the backend every 5 minutes for pending notifications.
 * Fires OS desktop notifications via tauri_plugin_notification.
 * Clicking a notification navigates GAIA to the relevant section.
 *
 * Quiet hours are enforced server-side; this module handles
 * the client-side permission request and click routing only.
 */

import {
  isPermissionGranted,
  requestPermission,
  sendNotification,
} from '@tauri-apps/plugin-notification';
import { invoke } from '@tauri-apps/api/core';

const POLL_INTERVAL_MS = 5 * 60 * 1000; // 5 minutes
const BACKEND_URL = 'http://localhost:8008';

interface PendingNotification {
  id: string;
  title: string;
  body: string;
  trigger: string;
  section: string;
}

export class NotificationBridge {
  private pollTimer: ReturnType<typeof setInterval> | null = null;
  private permissionGranted = false;

  async init(): Promise<void> {
    this.permissionGranted = await this.ensurePermission();
    if (!this.permissionGranted) {
      console.warn('[NotificationBridge] Permission denied — notifications disabled.');
      return;
    }

    // Poll immediately on init, then on interval
    await this.poll();
    this.pollTimer = setInterval(() => this.poll(), POLL_INTERVAL_MS);
  }

  destroy(): void {
    if (this.pollTimer !== null) {
      clearInterval(this.pollTimer);
      this.pollTimer = null;
    }
  }

  // ── Permission ──────────────────────────────────────────────────────────────

  private async ensurePermission(): Promise<boolean> {
    try {
      let granted = await isPermissionGranted();
      if (!granted) {
        const permission = await requestPermission();
        granted = permission === 'granted';
      }
      return granted;
    } catch (err) {
      console.error('[NotificationBridge] Permission check failed:', err);
      return false;
    }
  }

  // ── Poll ────────────────────────────────────────────────────────────────────

  private async poll(): Promise<void> {
    try {
      const res = await fetch(`${BACKEND_URL}/notifications/pending`);
      if (!res.ok) return;

      const notification: PendingNotification | null = await res.json();
      if (!notification) return;

      await this.fire(notification);
    } catch (err) {
      // Backend may not be up yet — silent fail
      console.debug('[NotificationBridge] Poll failed (backend may be starting):', err);
    }
  }

  // ── Fire ────────────────────────────────────────────────────────────────────

  private async fire(notification: PendingNotification): Promise<void> {
    try {
      // Send the OS notification
      sendNotification({
        title: notification.title,
        body: notification.body,
      });

      // Mark as delivered on the backend so it won't repeat today
      await fetch(`${BACKEND_URL}/notifications/dismiss`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ notification_id: notification.id }),
      });

      // tauri_plugin_notification doesn't support click callbacks natively
      // on all platforms yet, so we navigate proactively after a short delay
      // only for memory-triggered notifications (time ones are ambient).
      if (notification.trigger === 'memory') {
        setTimeout(() => {
          invoke('navigate_main', { section: notification.section }).catch(console.error);
        }, 500);
      }
    } catch (err) {
      console.error('[NotificationBridge] Failed to fire notification:', err);
    }
  }
}

// Singleton export for use in main app bootstrap
export const notificationBridge = new NotificationBridge();
