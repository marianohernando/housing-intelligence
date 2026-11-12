import { describe, expect, it } from "vitest";

import { anySignal, createLimiter } from "../limit";

function deferred() {
  let resolve: () => void = () => undefined;
  let reject: (e: Error) => void = () => undefined;
  const promise = new Promise<void>((res, rej) => {
    resolve = res;
    reject = rej;
  });
  return { promise, resolve, reject };
}

const tick = () => new Promise((resolve) => setTimeout(resolve, 0));

describe("createLimiter", () => {
  it("runs at most `max` tasks at once, the rest in the order they were asked", async () => {
    const run = createLimiter(2);
    const tasks = [deferred(), deferred(), deferred(), deferred()];
    const started: number[] = [];
    const done = tasks.map((t, i) =>
      run(() => {
        started.push(i);
        return t.promise;
      }),
    );
    const settled = Promise.allSettled(done);
    await tick();
    expect(started).toEqual([0, 1]);
    tasks[1]?.resolve();
    await tick();
    expect(started).toEqual([0, 1, 2]);
    tasks[0]?.reject(new Error("down"));
    await tick();
    expect(started).toEqual([0, 1, 2, 3]);
    tasks[2]?.resolve();
    tasks[3]?.resolve();
    // A failure is the caller's, and frees its turn like a success
    const results = await settled;
    expect(results.map((r) => r.status)).toEqual(["rejected", "fulfilled", "fulfilled", "fulfilled"]);
  });

  it("gives each caller its own answer", async () => {
    const run = createLimiter(1);
    await expect(Promise.all([run(async () => "a"), run(async () => "b")])).resolves.toEqual(["a", "b"]);
  });

  it("a waiting task whose signal aborts leaves the queue with its reason; the others keep their turn", async () => {
    const run = createLimiter(1);
    const first = deferred();
    const started: string[] = [];
    const done = [
      run(() => {
        started.push("a");
        return first.promise;
      }),
      run(
        () => {
          started.push("b");
          return Promise.resolve();
        },
        { signal: AbortSignal.timeout(10) },
      ),
      run(() => {
        started.push("c");
        return Promise.resolve();
      }),
    ];
    const settled = Promise.allSettled(done);
    await new Promise((resolve) => setTimeout(resolve, 30));
    first.resolve();
    const results = await settled;
    expect(started).toEqual(["a", "c"]);
    expect(results.map((r) => r.status)).toEqual(["fulfilled", "rejected", "fulfilled"]);
    expect((results[1] as PromiseRejectedResult).reason).toMatchObject({ name: "TimeoutError" });
  });
});

describe("anySignal", () => {
  it("aborts with the first signal's reason, also where AbortSignal.any does not exist", () => {
    const native = Object.getOwnPropertyDescriptor(AbortSignal, "any");
    try {
      for (const withNative of [true, false]) {
        if (!withNative) Reflect.deleteProperty(AbortSignal, "any");
        const a = new AbortController();
        const b = new AbortController();
        const signal = anySignal([a.signal, b.signal]);
        expect(signal.aborted).toBe(false);
        b.abort(new Error("second"));
        expect(signal.aborted).toBe(true);
        expect((signal.reason as Error).message).toBe("second");
        const already = new AbortController();
        already.abort(new Error("before"));
        expect((anySignal([already.signal]).reason as Error).message).toBe("before");
      }
    } finally {
      if (native) Object.defineProperty(AbortSignal, "any", native);
    }
  });
});
