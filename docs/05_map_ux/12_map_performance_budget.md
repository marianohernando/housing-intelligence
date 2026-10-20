# Map Performance Budget

## Budgets
- cap active heavy layers;
- progressive detail by zoom;
- tile/payload size monitored;
- no citywide raw building GeoJSON in client.

## Tests
- cold load;
- warm load;
- rapid zoom/pan;
- layer toggles;
- low-memory browser;
- mobile representative viewport.

## Failure
If a heavy layer exceeds budget:
- aggregate;
- tile;
- sample;
- disable 3D detail at lower zoom.
