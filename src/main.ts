import { initSidecar } from './sidecar';
import { App } from './app';

// Wait for sidecar to be ready before mounting the UI
initSidecar().then(() => {
  new App();
});
