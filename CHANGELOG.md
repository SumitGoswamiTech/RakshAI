# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/) and the project uses [Semantic Versioning](https://semver.org/).

## [1.0.1] - 2026-10-03

### Fixed
- Restarting a populated instance no longer re-injects 240 back-dated demo decisions once retention pruning has
  removed the original seed rows (seeding now requires a genuinely empty database).
- Escalated alerts stay in the open review queue and the "Open alerts" KPI until released or confirmed, as the
  documented analyst workflow specifies; previously escalation silently closed them.
- `FRAUD_SHIELD_RETENTION` is enforced while running (every 500 inserts), not only at startup.
- Review queue shows "—" instead of "Open" for auto-allowed payments in the "All" view.

### Performance
- Schema v3: covering indexes for dashboard aggregates; `/stats` at 10k decisions drops from ~118 ms to ~20-35 ms
  (and it no longer holds the database lock that long).
- Console: removed the blurred translucent sticky header (re-blurred on every scroll frame); cached `Intl`
  formatters; the simulator never overlaps requests; Overview and queue refreshes are serialised and skip
  re-rendering unchanged data; removed duplicate `/stats` polling for the nav badge.

## [1.0.0] - 2026-09-21

### Added
- Analyst console: overview KPIs and timeline, review queue (search, filters, sorting, paging, keyboard shortcuts),
  decision drawer with SHAP signal bars and complaint draft, audit log, model card with drift monitor.
- Versioned JSON API under `/api/v1`: screening (single, batch, CSV), decisions, overrides, audit, statistics,
  model card, traffic simulator, CSV export.
- Idempotent screening by client `reference`.
- SQLite decision store with append-only override history and forward-only schema migrations.
- PSI drift monitoring against the training score distribution.
- Environment-based configuration, optional API key for writes, per-IP write rate limiting, request IDs,
  `/healthz` and `/readyz`, strict CSP.
- Read-only static preview mode for GitHub Pages, Docker image and compose file, CI on Linux and Windows.
- `python -m model.train --data` accepts a user's own labelled CSV.

### Model
- XGBoost classifier with a 60/20/20 train/validation/test split; thresholds tuned on validation only.
- Exact TreeSHAP attributions via XGBoost's native `pred_contribs`.
- Model stored as portable JSON with metrics, thresholds and a drift baseline.
