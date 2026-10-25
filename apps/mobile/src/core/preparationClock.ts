import { IntegrityError } from "./integrity";

/** Sequential wall/monotonic sampling allowance, inclusive. This engineering
 * consistency bound is not clock accuracy or a scientific/rest-duration limit. */
export const PREPARATION_CLOCK_TOLERANCE_MS = 100;

/** Foreground preparation wait. Only monotonic elapsed time counts toward rest;
 * inconsistent wall chronology invalidates authority rather than shortening it. */
export class PreparationClock {
  private started: number | null = null;
  private previous: number | null = null;
  private startedWall: number | null = null;
  private previousWall: number | null = null;
  constructor(
    private readonly monotonic: () => number = () => performance.now(),
    private readonly wall: () => number = () => Date.now(),
  ) {}
  start(): void {
    this.reset();
    const value = this.monotonic(),
      wall = this.wall();
    if (!Number.isFinite(value) || value < 0 || !Number.isFinite(wall))
      throw new IntegrityError(
        "PREPARATION_CLOCK_UNAVAILABLE",
        "Valid monotonic and wall preparation clocks are required.",
      );
    this.started = value;
    this.previous = value;
    this.startedWall = wall;
    this.previousWall = wall;
  }
  get active(): boolean {
    return this.started !== null;
  }
  reset(): void {
    this.started = null;
    this.previous = null;
    this.startedWall = null;
    this.previousWall = null;
  }
  remaining(seconds: number): number {
    const value = this.monotonic(),
      wall = this.wall();
    if (
      this.started === null ||
      this.startedWall === null ||
      !Number.isFinite(value) ||
      !Number.isFinite(wall) ||
      value < this.started ||
      wall < this.startedWall ||
      (this.previous !== null && value < this.previous) ||
      (this.previousWall !== null && wall < this.previousWall) ||
      Math.abs(wall - this.startedWall - (value - this.started)) >
        PREPARATION_CLOCK_TOLERANCE_MS ||
      (this.previous !== null &&
        this.previousWall !== null &&
        Math.abs(wall - this.previousWall - (value - this.previous)) >
          PREPARATION_CLOCK_TOLERANCE_MS)
    ) {
      this.reset();
      return seconds;
    }
    this.previous = value;
    this.previousWall = wall;
    return Math.max(0, Math.ceil(seconds - (value - this.started) / 1000));
  }
}
