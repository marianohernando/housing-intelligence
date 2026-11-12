/**
 * One request per key for the whole visit, shared by every screen that asks for it, also after
 * leaving a page and coming back. A failed request is forgotten, so retrying asks again.
 */
export function once<T>(cache: Map<string, Promise<T>>, key: string, load: () => Promise<T>): Promise<T> {
  const cached = cache.get(key);
  if (cached) return cached;
  const request = load();
  cache.set(key, request);
  request.catch(() => {
    if (cache.get(key) === request) cache.delete(key);
  });
  return request;
}
