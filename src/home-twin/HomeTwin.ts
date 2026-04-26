/**
 * HomeTwin.ts
 *
 * Orchestrates the Home Twin experience:
 *   1. Load existing room scan → go straight to RoomRenderer
 *   2. No scan yet → launch RoomScanner flow
 *   3. After scan → RoomRenderer + SurfaceDetector overlay
 *
 * Canon Ref: C20 (Home Twin — Spatial Presence)
 */

import './home-twin.css';
import { RoomScanner } from './RoomScanner';
import { RoomRenderer } from './RoomRenderer';
import { SurfaceDetector } from './SurfaceDetector';
import { RoomStore }      from './RoomStore';

export class HomeTwin {
  private root: HTMLElement;
  private renderer: RoomRenderer | null = null;
  private scanner:  RoomScanner  | null = null;

  constructor(root: HTMLElement) {
    this.root = root;
  }

  async mount(): Promise<void> {
    const store = new RoomStore();
    const room  = await store.loadRoom();

    if (room?.panoramaDataUrl) {
      await this._mountRenderer(room.panoramaDataUrl);
    } else {
      this._mountScanPrompt();
    }
  }

  dispose(): void {
    this.renderer?.dispose();
    this.scanner?.dispose();
  }

  // ------------------------------------------------------------------ //
  //  Scan prompt                                                         //
  // ------------------------------------------------------------------ //

  private _mountScanPrompt(): void {
    this.root.innerHTML = `
<div class="ht-prompt">
  <div class="ht-prompt-icon">◉</div>
  <h2 class="ht-prompt-title">Bring GAIA Home</h2>
  <p class="ht-prompt-desc">Scan your room once and GAIA will live in your space permanently.</p>
  <p class="ht-prompt-sub">Takes about 2 minutes. Works without any AR headset.</p>
  <button id="ht-btn-scan" class="ht-btn-primary">◎ Start Room Scan</button>
  <button id="ht-btn-skip" class="ht-btn-ghost">Use gradient background</button>
</div>`;

    this.root.querySelector('#ht-btn-scan')?.addEventListener('click', () => this._mountScanner());
    this.root.querySelector('#ht-btn-skip')?.addEventListener('click', () => this._mountRenderer(null));
  }

  // ------------------------------------------------------------------ //
  //  Scanner                                                             //
  // ------------------------------------------------------------------ //

  private _mountScanner(): void {
    this.root.innerHTML = '<div id="ht-scanner-host" class="ht-scanner-host"></div>';
    const host = this.root.querySelector<HTMLElement>('#ht-scanner-host')!;

    this.scanner = new RoomScanner(host, async (panoramaDataUrl) => {
      this.scanner?.dispose();
      await this._mountRenderer(panoramaDataUrl);
      // Run surface detection after render is up
      this._runSurfaceDetection(panoramaDataUrl);
    });

    host.addEventListener('rs:cancel', () => this._mountScanPrompt());
    void this.scanner.mount();
  }

  // ------------------------------------------------------------------ //
  //  Renderer                                                            //
  // ------------------------------------------------------------------ //

  private async _mountRenderer(panoramaDataUrl: string | null): Promise<void> {
    this.root.innerHTML = '<div class="ht-room-container" id="ht-room-container"></div>';
    const container = this.root.querySelector<HTMLElement>('#ht-room-container')!;

    // Rescan button
    const rescanBtn = document.createElement('button');
    rescanBtn.className = 'ht-btn-rescan';
    rescanBtn.textContent = '↺ Rescan Room';
    rescanBtn.addEventListener('click', () => {
      this.renderer?.dispose();
      this._mountScanner();
    });
    container.appendChild(rescanBtn);

    this.renderer = new RoomRenderer(container);
    await this.renderer.mount();
  }

  // ------------------------------------------------------------------ //
  //  Surface detection                                                   //
  // ------------------------------------------------------------------ //

  private async _runSurfaceDetection(panoramaDataUrl: string): Promise<void> {
    const container = this.root.querySelector<HTMLElement>('#ht-room-container');
    if (!container) return;

    const detector = new SurfaceDetector(container, async (placement) => {
      console.log('[HomeTwin] GAIA placed:', placement);
      // Position orb canvas at the surface yPercent
      const orbCanvas = container.querySelector<HTMLElement>('.gaian-orb-canvas');
      if (orbCanvas) {
        orbCanvas.style.top  = `${placement.yPercent * 100 - 15}%`;
        orbCanvas.style.left = '50%';
        orbCanvas.style.transform = 'translate(-50%, -50%)';
      }
    });

    const surfaces = await detector.detect(panoramaDataUrl);
    if (surfaces.length > 0) detector.renderOverlay();
  }
}

export function mountHomeTwin(root: HTMLElement): void {
  const twin = new HomeTwin(root);
  void twin.mount();
}
