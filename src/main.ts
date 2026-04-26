import { initSidecar } from './sidecar';
import { App } from './app';
import { notificationBridge } from './shell/NotificationBridge';

// Wait for sidecar to be ready before mounting the UI
initSidecar().then(() => {
  new App();

  // Start proactive notification polling now that the backend is live
  notificationBridge.init().catch(console.error);
});
