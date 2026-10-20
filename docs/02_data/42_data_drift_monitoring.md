# Data Drift Monitoring

## Source drift
- schema change;
- field disappearance;
- category change;
- encoding;
- coordinate format.

## Distribution drift
- sudden null spike;
- row count jump/drop;
- impossible distribution;
- geographic coverage loss.

## Actions
- quarantine new snapshot;
- keep last valid;
- alert;
- compare source documentation;
- approve migration.

## Rule
A successful HTTP 200 is not a successful ingestion.
