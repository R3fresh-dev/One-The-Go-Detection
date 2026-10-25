import test from "node:test";
import assert from "node:assert/strict";
import { PreparationClock } from "../src/core/preparationClock";

function clocks() {
  let mono = 1000,
    wall = Date.parse("2026-10-11T12:00:00Z");
  const clock = new PreparationClock(
    () => mono,
    () => wall,
  );
  return {
    clock,
    advance(milliseconds: number, drift = 0) {
      mono += milliseconds;
      wall += milliseconds + drift;
    },
    mono(value: number) {
      mono = value;
    },
    wall(value: number) {
      wall = value;
    },
  };
}

test("preparation accepts inclusive ±100ms sampling disagreement while rest remains monotonic", () => {
  for (const drift of [-100, 100]) {
    const h = clocks();
    h.clock.start();
    h.advance(1000, drift);
    assert.equal(h.clock.remaining(30), 29);
    assert.equal(h.clock.active, true);
    h.advance(28999);
    assert.equal(h.clock.remaining(30), 1);
    h.advance(1);
    assert.equal(h.clock.remaining(30), 0);
  }
});

test("forward/backward ±101ms discontinuities reset authority until a new start", () => {
  for (const drift of [-101, 101]) {
    const h = clocks();
    h.clock.start();
    h.advance(1000, drift);
    assert.equal(h.clock.remaining(30), 30);
    assert.equal(h.clock.active, false);
    h.advance(60_000);
    assert.equal(h.clock.remaining(30), 30);
    h.clock.start();
    h.advance(30_000);
    assert.equal(h.clock.remaining(30), 0);
    assert.equal(h.clock.active, true);
  }
});

test("accumulated wall disagreement and opposing per-sample jumps cannot cancel a discontinuity", () => {
  const accumulated = clocks();
  accumulated.clock.start();
  accumulated.advance(1000, 60);
  assert.equal(accumulated.clock.remaining(30), 29);
  accumulated.advance(1000, 41);
  assert.equal(accumulated.clock.remaining(30), 30);
  assert.equal(accumulated.clock.active, false);
  const opposing = clocks();
  opposing.clock.start();
  opposing.advance(1000, 100);
  assert.equal(opposing.clock.remaining(30), 29);
  opposing.advance(1000, -200);
  assert.equal(opposing.clock.remaining(30), 30);
  assert.equal(opposing.clock.active, false);
});

test("zero/max approved durations retain their bounds and wall time never shortens rest", () => {
  const zero = clocks();
  zero.clock.start();
  assert.equal(zero.clock.remaining(0), 0);
  assert.equal(zero.clock.active, true);
  zero.advance(0, 101);
  assert.equal(zero.clock.remaining(0), 0);
  assert.equal(zero.clock.active, false);
  const maximum = clocks();
  maximum.clock.start();
  maximum.advance(3_599_999);
  assert.equal(maximum.clock.remaining(3600), 1);
  maximum.advance(1);
  assert.equal(maximum.clock.remaining(3600), 0);
  const shortcut = clocks();
  shortcut.clock.start();
  shortcut.advance(1, 3_600_000);
  assert.equal(shortcut.clock.remaining(3600), 3600);
  assert.equal(shortcut.clock.active, false);
});

test("invalid wall/monotonic reads, monotonic regression and explicit interruption remain closed", () => {
  for (const invalid of [NaN, Infinity, -Infinity]) {
    const h = clocks();
    h.wall(invalid);
    assert.throws(() => h.clock.start());
    const running = clocks();
    running.clock.start();
    running.wall(invalid);
    assert.equal(running.clock.remaining(30), 30);
    assert.equal(running.clock.active, false);
  }
  const h = clocks();
  h.clock.start();
  h.advance(1000);
  assert.equal(h.clock.remaining(30), 29);
  h.mono(1999);
  assert.equal(h.clock.remaining(30), 30);
  assert.equal(h.clock.active, false);
  h.clock.start();
  h.clock.reset();
  h.advance(30000);
  assert.equal(h.clock.remaining(30), 30);
  assert.equal(h.clock.active, false);
});

test("a wall clock that actually regresses resets even when its disagreement is within sampling tolerance", () => {
  const h = clocks();
  h.clock.start();
  h.advance(1000);
  assert.equal(h.clock.remaining(30), 29);
  h.advance(0, -1);
  assert.equal(h.clock.remaining(30), 30);
  assert.equal(h.clock.active, false);
});
