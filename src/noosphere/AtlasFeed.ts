/**
 * AtlasFeed.ts — P5 ATLAS
 * Polls the ATLAS backend and applies real Earth data to the GaianOrb.
 *
 * Data flows:
 *   /atlas/clouds      → cloud layer opacity + tile URL on the orb
 *   /atlas/terminator  → day/night shadow band (updates every 60 s)
 *   /atlas/events      → surface ripple animations at event coordinates
 *   /atlas/health      → orb colour temperature, aurora intensity, saturation
 *
 * GAIA narrates her own planetary health when metrics change significantly.
 */

const BACKEND = 'http://localhost:8008';
const TERMINATOR_INTERVAL_MS = 60_000;       // 1 minute — sun moves ~0.25 deg
const HEALTH_INTERVAL_MS     = 3 * 60 * 60 * 1000; // 3 hours
const EVENTS_INTERVAL_MS     = 3 * 60 * 60 * 1000; // 3 hours

export interface AtlasHealth {
  co2_ppm: number;
  co2_index: number;
  temp_anomaly_c: number;
  temp_index: number;
  ocean_health_index: number;
  biodiversity_index: number;
  aurora_intensity: number;
  atmosphere_hue_shift: number;
}

export interface AtlasEvent {
  type: 'earthquake' | 'storm';
  title: string;
  magnitude?: number;
  severity?: string;
  latitude: number;
  longitude: number;
}

export interface AtlasTerminator {
  latitude: number;   // solar declination
  longitude: number;  // sub-solar longitude
  utc: string;
}

export interface AtlasClouds {
  tile_url_template: string;
  opacity: number;
  date: string;
}

// Callback interface — GaianOrb implements this
export interface AtlasConsumer {
  onCloudsUpdate(clouds: AtlasClouds): void;
  onTerminatorUpdate(terminator: AtlasTerminator): void;
  onEventsUpdate(events: AtlasEvent[]): void;
  onHealthUpdate(health: AtlasHealth): void;
  onGaiaHealthNarration(message: string): void;
}

export class AtlasFeed {
  private consumer: AtlasConsumer;
  private timers: ReturnType<typeof setInterval>[] = [];
  private lastHealth: AtlasHealth | null = null;

  constructor(consumer: AtlasConsumer) {
    this.consumer = consumer;
  }

  async start(): Promise<void> {
    // Initial fetch of all layers
    await Promise.allSettled([
      this.fetchClouds(),
      this.fetchTerminator(),
      this.fetchEvents(),
      this.fetchHealth(),
    ]);

    // Terminator updates every minute (sun moves in real time)
    this.timers.push(setInterval(() => this.fetchTerminator(), TERMINATOR_INTERVAL_MS));

    // Health + events update every 3 hours (matches cache TTL)
    this.timers.push(setInterval(() => this.fetchHealth(), HEALTH_INTERVAL_MS));
    this.timers.push(setInterval(() => this.fetchEvents(), EVENTS_INTERVAL_MS));

    // Clouds refresh once per day (daily satellite composite)
    this.timers.push(setInterval(() => this.fetchClouds(), 24 * 60 * 60 * 1000));
  }

  stop(): void {
    this.timers.forEach(clearInterval);
    this.timers = [];
  }

  // ── Fetchers ────────────────────────────────────────────────────────────

  private async fetchClouds(): Promise<void> {
    try {
      const res = await fetch(`${BACKEND}/atlas/clouds`);
      if (!res.ok) return;
      const data: AtlasClouds = await res.json();
      this.consumer.onCloudsUpdate(data);
    } catch { /* offline — silent */ }
  }

  private async fetchTerminator(): Promise<void> {
    try {
      const res = await fetch(`${BACKEND}/atlas/terminator`);
      if (!res.ok) return;
      const data: AtlasTerminator = await res.json();
      this.consumer.onTerminatorUpdate(data);
    } catch { /* offline — silent */ }
  }

  private async fetchEvents(): Promise<void> {
    try {
      const res = await fetch(`${BACKEND}/atlas/events`);
      if (!res.ok) return;
      const { events }: { events: AtlasEvent[] } = await res.json();
      this.consumer.onEventsUpdate(events ?? []);

      // Shift GAIA's mood for major events
      const major = events.filter(
        (e) => e.type === 'earthquake' && (e.magnitude ?? 0) >= 6.5
      );
      if (major.length > 0) {
        this.consumer.onGaiaHealthNarration(
          `I felt a tremor — a magnitude ${major[0].magnitude?.toFixed(1)} earthquake near ${major[0].title.split(' of ')[1] ?? 'the surface'}.`
        );
      }
    } catch { /* offline — silent */ }
  }

  private async fetchHealth(): Promise<void> {
    try {
      const res = await fetch(`${BACKEND}/atlas/health`);
      if (!res.ok) return;
      const data: AtlasHealth = await res.json();

      // Narrate only if CO2 has changed meaningfully since last fetch
      if (this.lastHealth) {
        const delta = Math.abs(data.co2_ppm - this.lastHealth.co2_ppm);
        if (delta >= 1.0) {
          this.consumer.onGaiaHealthNarration(
            `My atmosphere holds ${data.co2_ppm.toFixed(1)} ppm of CO₂ today. ` +
            (data.co2_index > 0.7
              ? 'I can feel the warmth building.'
              : 'I am holding steady.')
          );
        }
      }

      this.lastHealth = data;
      this.consumer.onHealthUpdate(data);
    } catch { /* offline — silent */ }
  }

  // ── Coordinate helpers ───────────────────────────────────────────────────

  /**
   * Convert lat/lon to normalised UV coordinates (0..1) for orb surface mapping.
   * Used by GaianOrb to place event ripples at geographic positions.
   */
  static geoToUV(lat: number, lon: number): { u: number; v: number } {
    const u = (lon + 180) / 360;
    const v = (90 - lat) / 180;
    return { u, v };
  }

  /**
   * Compute terminator shadow intensity for a given lat/lon.
   * Returns 0 (full daylight) to 1 (full night).
   */
  static terminatorShadow(
    lat: number,
    lon: number,
    terminator: AtlasTerminator
  ): number {
    const toRad = (d: number) => (d * Math.PI) / 180;
    const sinLat = Math.sin(toRad(lat));
    const cosLat = Math.cos(toRad(lat));
    const sinDecl = Math.sin(toRad(terminator.latitude));
    const cosDecl = Math.cos(toRad(terminator.latitude));
    const hourAngle = lon - terminator.longitude;
    const cosHour = Math.cos(toRad(hourAngle));

    // Solar elevation angle
    const sinElev = sinLat * sinDecl + cosLat * cosDecl * cosHour;
    // Map elevation to shadow: 0 elevation = terminator line
    // Add soft twilight band of ~6 degrees
    const twilight = 6;
    const elevDeg = Math.asin(sinElev) * (180 / Math.PI);
    return Math.max(0, Math.min(1, (-elevDeg + twilight) / (twilight * 2)));
  }
}
