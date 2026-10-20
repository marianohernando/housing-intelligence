# DATAMAD Demo Snapshot Policy

## Purpose
Demo must not depend on a third-party endpoint working live.

## Before demo
Freeze validated snapshots for:
- core CM datasets;
- Catastro subset;
- transport;
- POIs/services;
- model artifacts;
- docs/RAG corpus.

## Requirements
- checksum manifest;
- generated_at;
- data_version;
- source attribution;
- reproducible seed.

## Mode
Application can run in `DEMO_SNAPSHOT_MODE`.

Live refresh can exist but is not required for demo reliability.
