import { describe, expect, it } from "vitest";

import { createLimiter } from "../limit";

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
});
