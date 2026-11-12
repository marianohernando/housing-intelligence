/**
 * At most `max` tasks running at once; the rest wait their turn, in the order they were asked.
 * The web sends its API requests through one of these (see `createApi`).
 */
export function createLimiter(max: number) {
  let running = 0;
  const waiting: (() => void)[] = [];
  return function run<T>(task: () => Promise<T>): Promise<T> {
    return new Promise<T>((resolve, reject) => {
      const start = () => {
        running += 1;
        task()
          .then(resolve, reject)
          .finally(() => {
            running -= 1;
            waiting.shift()?.();
          });
      };
      if (running < max) start();
      else waiting.push(start);
    });
  };
}
