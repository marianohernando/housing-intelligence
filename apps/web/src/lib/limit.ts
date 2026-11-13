/**
 * At most `max` tasks running at once; the rest wait their turn, in the order they were asked.
 * A waiting task whose `signal` aborts leaves the queue and fails with the signal's reason. The
 * web sends its API requests through one of these (see `createApi`).
 */
export function createLimiter(max: number) {
  let running = 0;
  const waiting: (() => void)[] = [];
  return function run<T>(task: () => Promise<T>, { signal }: { signal?: AbortSignal } = {}): Promise<T> {
    return new Promise<T>((resolve, reject) => {
      const giveUp = () => {
        const index = waiting.indexOf(start);
        if (index < 0) return;
        waiting.splice(index, 1);
        reject(signal?.reason);
      };
      function start() {
        signal?.removeEventListener("abort", giveUp);
        running += 1;
        task()
          .then(resolve, reject)
          .finally(() => {
            running -= 1;
            waiting.shift()?.();
          });
      }
      if (running < max) return start();
      if (signal?.aborted) return reject(signal.reason);
      waiting.push(start);
      signal?.addEventListener("abort", giveUp, { once: true });
    });
  };
}

/** AbortSignal.any, with the same behaviour where the browser lacks it (Safari before 17.4). */
export function anySignal(signals: readonly AbortSignal[]): AbortSignal {
  if ("any" in AbortSignal && typeof AbortSignal.any === "function") return AbortSignal.any([...signals]);
  const controller = new AbortController();
  for (const signal of signals) {
    if (signal.aborted) {
      controller.abort(signal.reason);
      break;
    }
    signal.addEventListener("abort", () => controller.abort(signal.reason), { once: true });
  }
  return controller.signal;
}
