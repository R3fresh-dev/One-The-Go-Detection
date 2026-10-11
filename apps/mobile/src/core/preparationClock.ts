import { IntegrityError } from "./integrity";

/** Foreground preparation wait. Wall-clock timestamps describe events, never shorten this wait. */
export class PreparationClock {
  private started: number | null = null;
  private previous: number | null = null;
  constructor(
    private readonly monotonic: () => number = () => performance.now(),
  ) {}
  start(): void {
    const value = this.monotonic();
    if (!Number.isFinite(value) || value < 0)
      throw new IntegrityError(
        "PREPARATION_CLOCK_UNAVAILABLE",
        "A monotonic preparation clock is required.",
      );
    this.started = value;
    this.previous = value;
  }
  get active(): boolean {
    return this.started !== null;
  }
  reset(): void {
    this.started = null;
    this.previous = null;
  }
  remaining(seconds: number): number {
    const value = this.monotonic();
    if (
      this.started === null ||
      !Number.isFinite(value) ||
      value < this.started ||
      (this.previous !== null && value < this.previous)
    ) {
      this.reset();
      return seconds;
    }
    this.previous = value;
    return Math.max(0, Math.ceil(seconds - (value - this.started) / 1000));
  }
}
