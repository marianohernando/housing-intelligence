# Geospatial QA

## Tests
- CRS explicit;
- valid geometry;
- no accidental lat/lon swap;
- within expected Madrid bounds;
- polygon self-intersections;
- duplicate geometries;
- H3 mapping;
- boundary overlap;
- area/length sanity;
- centroid containment where applicable.

## Golden points
Maintain known addresses/POIs across Madrid and verify:
- district;
- neighborhood;
- H3;
- municipality;
- nearest transit.

## Visual QA
Render random samples and edge/boundary cases.

## Gate
No geospatial dataset reaches Silver if critical geometry tests fail.
