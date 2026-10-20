# Data Test Plan

## Per snapshot
- checksum;
- schema;
- count;
- null profile;
- duplicate keys;
- primary identifiers;
- geographic coverage;
- time coverage;
- expected categories.

## Cross-version
- row delta;
- schema delta;
- distribution drift;
- spatial coverage delta.

## Geospatial
- geometry valid;
- CRS;
- bounds;
- random render.

## Reproducibility
Same Bronze + code version → same Silver/Gold checksum where deterministic.
