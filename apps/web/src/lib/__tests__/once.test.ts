import { describe, expect, it, vi } from "vitest";

import { once } from "../once";

describe("once", () => {
  it("shares one request per key between callers", async () => {
    const cache = new Map<string, Promise<number>>();
    const load = vi.fn(() => Promise.resolve(1));
    const [a, b] = await Promise.all([once(cache, "k", load), once(cache, "k", load)]);
    expect([a, b]).toEqual([1, 1]);
    expect(load).toHaveBeenCalledTimes(1);
    await once(cache, "other", load);
    expect(load).toHaveBeenCalledTimes(2);
  });

  it("forgets a failed request, so retrying asks again", async () => {
    const cache = new Map<string, Promise<number>>();
    await expect(once(cache, "k", () => Promise.reject(new Error("down")))).rejects.toThrow("down");
    await Promise.resolve();
    expect(cache.has("k")).toBe(false);
    await expect(once(cache, "k", () => Promise.resolve(2))).resolves.toBe(2);
  });

  it("a late failure never removes the request that replaced it", async () => {
    const cache = new Map<string, Promise<number>>();
    let fail: (e: Error) => void = () => undefined;
    const first = once(cache, "k", () => new Promise<number>((_, reject) => (fail = reject)));
    const replacement = Promise.resolve(3);
    cache.set("k", replacement);
    fail(new Error("late"));
    await expect(first).rejects.toThrow("late");
    expect(cache.get("k")).toBe(replacement);
  });
});
