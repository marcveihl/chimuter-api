# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Chi-Muter API (`chimuter-api`) is a FastAPI backend that aggregates Chicago transit data from CTA and Metra APIs, computes connection health for saved commutes, and serves pre-computed results to a static HTML frontend hosted on GitHub Pages.

## Commands

- **Run server:** `uvicorn app.main:app --reload --port 8000`
- **Run tests:** `python -m pytest tests/ -v`
- **Docker build:** `docker build -t chimuter-api .`
- **Docker run:** `docker run --env-file .env -p 8000:8000 chimuter-api`

## Architecture

Stateless on-demand API proxy + computation engine. No database. The only persistent state is the in-memory parsed Metra GTFS schedule (refreshed when Metra publishes a new one).

### Endpoints

- `GET /api/health` — liveness check
- `GET /api/commutes` — returns the commute catalog from `commutes.json`
- `GET /api/refresh?commuteId=X&direction=morning|evening&rideOverrides=9:5,X9:3` — (being built) returns pre-computed train cards with nested connections, hero countdown data, alerts, and null placeholders for social/briefing

### Modules

- `app/main.py` — FastAPI app, CORS, rate limiting (3/min per IP), startup lifecycle
- `app/config.py` — env var loading, missing key warnings
- `app/logging_config.py` — structured JSON logging to stdout
- `app/commutes.py` — loads commute catalog from `commutes.json`
- `app/cta.py` — (to build) async CTA Bus Tracker + Train Tracker API clients
- `app/metra.py` — (to build) GTFS static parser + GTFS-RT protobuf decoder
- `app/engine.py` — (to build) connection math, card builder, best-pick algorithm

### Five Upstream Data Sources

| Source | Auth | Purpose |
|---|---|---|
| CTA Bus Tracker v3 | `CTA_BUS_API_KEY` env var | Live bus predictions |
| CTA Train Tracker | `CTA_TRAIN_API_KEY` env var | Live rail predictions |
| CTA Route Status + Alerts | None (public) | Service disruptions |
| Metra GTFS Static | None (public zip) | Schedule parsed at startup |
| Metra GTFS-RT tripupdates | `METRA_API_TOKEN` env var (Bearer) | Real-time delay overlay (protobuf) |

## Domain Language

Defined in the frontend repo's `CONTEXT.md`. Key terms:

- **Commute** — a saved, named route configuration (e.g., "Cortland / Ashland ↔ UP-NW")
- **Feeder** — a CTA bus or train leg that brings the commuter to a Metra station
- **Train** — a specific Metra departure the commuter is trying to catch
- **Connection** — one Feeder matched to one Train, with Buffer computed
- **Buffer** — minutes between Feeder arrival and Train departure
- **Health** — green/yellow/red viability based on Buffer vs threshold
- **Confidence** — data source quality: `live`, `live_delayed`, `schedule_fallback`, etc.

Health and Confidence are independent axes.

## Issue Tracker

All issues are on GitHub at `marcveihl/Token-Jockey-com` (not this repo). Use `--repo marcveihl/Token-Jockey-com` with all `gh` commands.

## Key Decisions (ADRs)

Recorded in the frontend repo's `docs/adr/`:

- **ADR-0001:** Two-repo split — GitHub Pages frontend + this Python backend
- **ADR-0002:** Backend owns all computation — frontend is a pure renderer
- **ADR-0003:** Curated commute catalog in JSON — no user configuration

## API Documentation

CTA Bus Tracker and Train Tracker API docs are in the frontend repo:
- `cta_Bus_Tracker_API_Developer_Guide_and_Documentation_2025-04-21.md`
- `cta_Train_Tracker_API_Developer_Guide_and_Documentation.md`

Metra GTFS docs: https://metra.com/metra-gtfs-api
