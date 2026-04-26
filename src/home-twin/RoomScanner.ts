/**
 * RoomScanner.ts
 *
 * Webcam-based room scanning flow.
 * User takes 4 directional photos (front, right, back, left).
 * Photos are stitched into an equirectangular 360° panorama
 * client-side using canvas, then saved via RoomStore.
 *
 * Canon Ref: C20 (Home Twin — Spatial Presence)
 */

import { RoomStore } from './RoomStore';

const DIRECTIONS = ['Front', 'Right', 'Back', 'Left'] as const;
type Direction = typeof DIRECTIONS[number];

interface CapturedFrame {
  direction: Direction;
  dataUrl: string;
  width: number;
  height: number;
}

export class RoomScanner {
  private root: HTMLElement;
  private stream: MediaStream | null = null;
  private frames: Map<Direction, CapturedFrame> = new Map();
  private currentStep = 0;
  private onComplete: (panoramaDataUrl: string) => void;

  constructor(root: HTMLElement, onComplete: (panoramaDataUrl: string) => void) {
    this.root = root;
    this.onComplete = onComplete;
  }

  async mount(): Promise<void> {
    this.root.innerHTML = this._buildHTML();
    await this._startCamera();
    this._bindEvents();
    this._updateStep();
  }

  dispose(): void {
    this._stopCamera();
    this.root.innerHTML = '';
  }

  // ------------------------------------------------------------------ //
  //  Camera                                                              //
  // ------------------------------------------------------------------ //

  private async _startCamera(): Promise<void> {
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 1280 }, height: { ideal: 720 }, facingMode: 'environment' },
      });
      const video = this.root.querySelector<HTMLVideoElement>('#rs-video')!;
      video.srcObject = this.stream;
      await video.play();
    } catch {
      this._showError('Camera access denied. Please allow camera permissions and reload.');
    }
  }

  private _stopCamera(): void {
    this.stream?.getTracks().forEach(t => t.stop());
    this.stream = null;
  }

  // ------------------------------------------------------------------ //
  //  Capture                                                             //
  // ------------------------------------------------------------------ //

  private _capture(): void {
    const video = this.root.querySelector<HTMLVideoElement>('#rs-video')!;
    const canvas = document.createElement('canvas');
    canvas.width  = video.videoWidth  || 1280;
    canvas.height = video.videoHeight || 720;
    const ctx = canvas.getContext('2d')!;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataUrl = canvas.toDataURL('image/jpeg', 0.92);
    const direction = DIRECTIONS[this.currentStep];
    this.frames.set(direction, { direction, dataUrl, width: canvas.width, height: canvas.height });

    // Flash feedback
    const flash = this.root.querySelector<HTMLElement>('#rs-flash')!;
    flash.classList.add('rs-flash--active');
    setTimeout(() => flash.classList.remove('rs-flash--active'), 180);

    this._updateThumbnail(direction, dataUrl);
    this.currentStep++;

    if (this.currentStep >= DIRECTIONS.length) {
      this._stitchAndFinish();
    } else {
      this._updateStep();
    }
  }

  // ------------------------------------------------------------------ //
  //  Stitch                                                              //
  // ------------------------------------------------------------------ //

  private async _stitchAndFinish(): Promise<void> {
    const captureBtn = this.root.querySelector<HTMLButtonElement>('#rs-btn-capture')!;
    captureBtn.disabled = true;
    captureBtn.textContent = 'Stitching…';

    try {
      const panorama = await this._stitch();
      this._stopCamera();

      // Persist via RoomStore
      const store = new RoomStore();
      await store.saveRoom({ panoramaDataUrl: panorama, capturedAt: new Date().toISOString() });

      this.onComplete(panorama);
    } catch (e) {
      this._showError(`Stitch failed: ${e instanceof Error ? e.message : String(e)}`);
    }
  }

  /**
   * Simple equirectangular stitch: place the 4 frames side by side
   * into a 4:1 aspect ratio canvas (each frame = 90° of horizontal FOV).
   * A proper spherical stitch requires OpenCV/WASM — this gives a usable
   * preview panorama for the skybox without external dependencies.
   */
  private _stitch(): Promise<string> {
    return new Promise((resolve, reject) => {
      const order: Direction[] = ['Front', 'Right', 'Back', 'Left'];
      const frames = order.map(d => this.frames.get(d)!).filter(Boolean);
      if (frames.length < 4) { reject(new Error('Not all frames captured')); return; }

      const fw = frames[0].width;
      const fh = frames[0].height;
      const canvas = document.createElement('canvas');
      canvas.width  = fw * 4;
      canvas.height = fh;
      const ctx = canvas.getContext('2d')!;

      let loaded = 0;
      frames.forEach((frame, i) => {
        const img = new Image();
        img.onload = () => {
          ctx.drawImage(img, i * fw, 0, fw, fh);
          loaded++;
          if (loaded === 4) resolve(canvas.toDataURL('image/jpeg', 0.90));
        };
        img.onerror = () => reject(new Error(`Failed to load frame ${i}`));
        img.src = frame.dataUrl;
      });
    });
  }

  // ------------------------------------------------------------------ //
  //  UI                                                                  //
  // ------------------------------------------------------------------ //

  private _updateStep(): void {
    const dir = DIRECTIONS[this.currentStep];
    const label = this.root.querySelector<HTMLElement>('#rs-direction-label')!;
    const hint  = this.root.querySelector<HTMLElement>('#rs-hint')!;
    const progress = this.root.querySelector<HTMLElement>('#rs-progress')!;
    if (label) label.textContent = `Face ${dir}`;
    if (hint)  hint.textContent  = `Turn to face ${dir.toLowerCase()} and hold still.`;
    if (progress) progress.textContent = `${this.currentStep + 1} / ${DIRECTIONS.length}`;
  }

  private _updateThumbnail(direction: Direction, dataUrl: string): void {
    const idx = DIRECTIONS.indexOf(direction);
    const thumb = this.root.querySelector<HTMLImageElement>(`.rs-thumb[data-idx="${idx}"]`);
    if (thumb) { thumb.src = dataUrl; thumb.classList.add('rs-thumb--done'); }
  }

  private _showError(msg: string): void {
    const err = this.root.querySelector<HTMLElement>('#rs-error')!;
    if (err) { err.textContent = msg; err.style.display = 'block'; }
  }

  private _bindEvents(): void {
    this.root.querySelector('#rs-btn-capture')?.addEventListener('click', () => this._capture());
    this.root.querySelector('#rs-btn-cancel')?.addEventListener('click', () => {
      this._stopCamera();
      this.root.dispatchEvent(new CustomEvent('rs:cancel'));
    });
  }

  private _buildHTML(): string {
    const thumbs = DIRECTIONS.map((d, i) => `
      <div class="rs-thumb-slot">
        <img class="rs-thumb" data-idx="${i}" src="" alt="${d}" />
        <span class="rs-thumb-label">${d}</span>
      </div>`).join('');

    return `
<div class="rs-shell">
  <div class="rs-header">
    <span class="rs-title">◉ Room Scan</span>
    <span class="rs-progress-badge" id="rs-progress">1 / 4</span>
  </div>

  <div class="rs-viewport">
    <video id="rs-video" class="rs-video" autoplay muted playsinline></video>
    <div id="rs-flash" class="rs-flash"></div>
    <div class="rs-crosshair"></div>
    <div class="rs-direction-overlay">
      <span id="rs-direction-label" class="rs-direction-label">Face Front</span>
      <span id="rs-hint" class="rs-hint">Turn to face front and hold still.</span>
    </div>
  </div>

  <div class="rs-thumbs">${thumbs}</div>

  <div id="rs-error" class="rs-error" style="display:none"></div>

  <div class="rs-actions">
    <button id="rs-btn-cancel" class="rs-btn rs-btn--ghost">✕ Cancel</button>
    <button id="rs-btn-capture" class="rs-btn rs-btn--capture">● Capture</button>
  </div>
</div>`;
  }
}
