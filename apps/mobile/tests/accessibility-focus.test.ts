import test from "node:test";
import assert from "node:assert/strict";
import "./support/runtime.cjs";
const native = require("react-native");
const { scheduleAccessibilityFocus } =
  require("../src/ui/accessibility") as typeof import("../src/ui/accessibility");

// These tests exercise our handoff/cancellation at the native API boundary.
// They do not execute TalkBack, VoiceOver or a native renderer.
function scheduler(context: any) {
  let interaction: (() => void) | undefined;
  const frames: FrameRequestCallback[] = [];
  const cancelled: number[] = [];
  context.mock.method(
    native.InteractionManager,
    "runAfterInteractions",
    (callback: () => void) => {
      interaction = callback;
      return {
        cancel() {
          cancelled.push(-1);
        },
      };
    },
  );
  const priorRequest = globalThis.requestAnimationFrame;
  const priorCancel = globalThis.cancelAnimationFrame;
  globalThis.requestAnimationFrame = (callback) => {
    frames.push(callback);
    return frames.length;
  };
  globalThis.cancelAnimationFrame = (frame) => {
    if (typeof frame === "number") cancelled.push(frame);
  };
  context.after(() => {
    globalThis.requestAnimationFrame = priorRequest;
    globalThis.cancelAnimationFrame = priorCancel;
  });
  return {
    start: () => interaction!(),
    flush: () => frames.forEach((callback) => callback(1)),
    cancelled,
  };
}
test("web heading focus prevents scrolling and ignores a detached destination", (context) => {
  const queue = scheduler(context);
  const calls: unknown[] = [];
  const node = {
    isConnected: true,
    focus: (options: unknown) => calls.push(options),
  };
  scheduleAccessibilityFocus(() => node);
  queue.start();
  queue.flush();
  assert.deepEqual(calls, [{ preventScroll: true }]);
  calls.length = 0;
  node.isConnected = false;
  scheduleAccessibilityFocus(() => node);
  queue.start();
  queue.flush();
  assert.deepEqual(calls, []);
});
test("native heading focus resolves the current native tag and calls accessibility focus", (context) => {
  const queue = scheduler(context);
  const previous = native.Platform.OS;
  native.Platform.OS = "android";
  context.after(() => {
    native.Platform.OS = previous;
  });
  const node = {};
  context.mock.method(native, "findNodeHandle", (target: unknown) => {
    assert.equal(target, node);
    return 42;
  });
  const focus = context.mock.method(
    native.AccessibilityInfo,
    "setAccessibilityFocus",
    () => {},
  );
  scheduleAccessibilityFocus(() => node);
  queue.start();
  queue.flush();
  assert.deepEqual(
    focus.mock.calls.map((call: any) => call.arguments),
    [[42]],
  );
});
test("cancelled and stale navigation cannot focus an old route after deferred work", (context) => {
  const queue = scheduler(context);
  let calls = 0,
    current = true;
  const node = {
    focus: () => {
      calls++;
    },
  };
  const cancel = scheduleAccessibilityFocus(
    () => node,
    () => current,
  );
  queue.start();
  cancel();
  queue.flush();
  assert.equal(calls, 0);
  assert.ok(queue.cancelled.includes(1));
  scheduleAccessibilityFocus(
    () => node,
    () => current,
  );
  queue.start();
  current = false;
  queue.flush();
  assert.equal(calls, 0);
});
test("cleanup before interaction completion prevents scheduling a layout frame", (context) => {
  const queue = scheduler(context);
  let reads = 0;
  const cancel = scheduleAccessibilityFocus(() => {
    reads++;
    return null;
  });
  cancel();
  queue.start();
  queue.flush();
  assert.equal(reads, 0);
  assert.deepEqual(queue.cancelled, [-1]);
});

test("deferred destination focus preserves a newer explicit user focus", (context) => {
  const queue = scheduler(context);
  const previous = (globalThis as any).document;
  const oldFocus = {},
    newFocus = {},
    body = {};
  (globalThis as any).document = { activeElement: oldFocus, body };
  context.after(() => {
    (globalThis as any).document = previous;
  });
  let calls = 0;
  scheduleAccessibilityFocus(() => ({
    focus: () => {
      calls++;
    },
  }));
  queue.start();
  (globalThis as any).document.activeElement = newFocus;
  queue.flush();
  assert.equal(calls, 0);
});
