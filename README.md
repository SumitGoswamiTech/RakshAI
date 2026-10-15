# Fraud Shield

**A real-time payment risk console: screen every transaction, explain every decision, and keep a human in the loop.**

[![CI](../../actions/workflows/ci.yml/badge.svg)](../../actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Fraud Shield scores UPI-style digital payments with a gradient-boosted model, explains each score in plain
language with exact SHAP attributions, and applies a transparent three-tier policy: **allow**, **challenge with
step-up verification**, or **hold and draft a complaint**. Analysts work the resulting alerts in a review console;
every override is written to an append-only audit trail.

```
payment ─► model score ─► SHAP reasons ─► agent policy ─┬─► allow
 (API / CSV)                                            ├─► step-up verify ─┐
                                                        └─► hold + complaint ┴─► analyst review ─► audit log
```

## What you get

| Area | Capability |
| --- | --- |
| **Console** | Overview KPIs and live timeline · review queue with search, filters, sorting, paging and keyboard shortcuts · decision drawer with per-signal SHAP bars, auto-drafted complaint and one-click override · audit log · model card with drift monitor |
| **Screening** | Single transaction, batch JSON, or **CSV upload** (500 rows) · idempotent by client `reference` · every decision persisted |
| **Human in the loop** | Release / Confirm fraud / Escalate with analyst name and note · append-only history · analyst-confirmed precision on the dashboard |
| **Model** | XGBoost, validated on a held-out split, thresholds tuned on a separate validation split · exact TreeSHAP · PSI drift monitor against the training score distribution |
| **Operations** | Versioned API (`/api/v1`) · env-based config · optional API key and rate limiting · `/healthz` + `/readyz` · request IDs · schema migrations · security headers + strict CSP · Docker |
| **Quality** | 90 automated tests · CI on Linux and Windows · lint clean · zero-build frontend (native ES modules) |

## Quick start

Requires **Python 3.11+**. No database server, no GPU, no build step, no external services.

```bash
python -m venv venv
# Windows (PowerShell):  venv\Scripts\Activate.ps1        macOS / Linux:  source venv/bin/activate
pip install -r requirements.txt
python run.py
```

`python run.py` opens the console at <http://127.0.0.1:8000> (API docs at `/docs`). The trained model ships
with the repository, and a fresh database is filled with simulated history so every page has content on first
launch. Use **Overview → Start simulation** to stream live traffic through the pipeline.

| Command | What it does |
| --- | --- |
| `python run.py` | start the console + API |
| `python run.py --train` | retrain the model first (regenerates data if missing) |
| `python run.py --port 9000 --no-browser` | different port, don't open a browser |
| `python run.py --db path/to/file.db` | use another database file |
| `python run.py --env production` | no demo data, no simulator |
| `python run.py --host 0.0.0.0` | listen on all interfaces (containers, LAN) |
| `pip install -r requirements-dev.txt && python -m pytest` | run the tests |

## Screening from your own systems

```bash
curl -X POST http://127.0.0.1:8000/api/v1/screen -H "Content-Type: application/json" -d '{
  "reference": "UPI-2026-000123",
  "hour_of_day": 2, "amount": 4500, "amount_ratio_to_avg": 6.2,
  "merchant_category": "unknown_merchant", "is_new_payee": 1, "device_recognized": 0,
  "lat_bucket_delta": 22, "lon_bucket_delta": 18, "txn_velocity_10min": 6,
  "failed_attempts_last_hour": 2, "account_age_days": 40, "is_international": 1}'
```

The response carries the risk score, the ranked reasons, per-signal contributions, the agent's decision and (for
held payments) a structured complaint draft. Sending the same `reference` again returns the original decision
instead of creating a duplicate (`Idempotent-Replay: true`). For files, download the template from
`GET /api/v1/screen/csv/template` (or the **Screen** page) and `POST` the CSV to `/api/v1/screen/csv`.

| Endpoint | Purpose |
| --- | --- |
| `GET /api/v1/meta` · `/model` · `/stats` | version and config · model card · KPIs, timeline, drift |
| `POST /api/v1/screen` · `/screen/batch` · `/screen/csv` | score + explain + decide (one / up to 500 / CSV file) |
| `GET /api/v1/decisions` | filter by `status`, `action`, `q`; `sort`, `limit`, `offset` · `GET .../export.csv` for a spreadsheet |
| `GET /api/v1/decisions/{id}` · `POST .../{id}/overrides` | one decision · analyst release / confirm fraud / escalate |
| `GET /api/v1/audit` | the override history |
| `POST /api/v1/simulate` · `/simulate/reset` | demo traffic (disabled in production) |
| `GET /healthz` · `GET /readyz` | liveness · readiness (model loaded) |

Interactive documentation with request and response schemas is served at `/docs`.

## How the agent decides

| Risk score | Action |
| --- | --- |
| `< review_at` | **Allow**: proceeds normally |
| `review_at` … `hold_at` | **Step-up verify**: OTP / biometric before the payment completes |
| `≥ hold_at` | **Hold + complaint draft**: funds held, a structured cybercrime-portal-style draft is prepared for a **human** to review (it never files anything itself) |

Both thresholds come from the trained model's validation-set operating points (`hold_at` is F1-optimal;
`review_at` is the highest threshold that still keeps ≥ 98 % recall), so retraining re-tunes the agent
automatically. Every decision carries a one-line reason built from the SHAP attributions.

## Model results

Trained on 90,000 synthetic UPI transactions (1.8 % fraud; four attack patterns plus stealth variants). A 60 / 20 / 20
train / validation / test split is used: **early stopping and both thresholds are chosen on the validation split
only**, and the numbers below come from the untouched 18,000-transaction test split (318 fraud).

| Metric (test set) | Value |
| --- | --- |
| ROC-AUC | **0.998** (5-fold CV 0.9983 ± 0.0005) |
| PR-AUC | **0.930** (5-fold CV 0.935 ± 0.010) |
| Hold tier: precision / recall / F1 | 90.0 % / 79.6 % / 84.5 % |
| Accuracy | 99.48 % (an "always allow" model scores 98.23 %) |

| Tier | Payments | Of which fraud |
| --- | --- | --- |
| Allow (< 0.076) | 17,427 | 7 |
| Step-up verify (0.076 – 0.95) | 292 | 58 |
| Hold (≥ 0.95) | 281 | 253 |

The policy **stops or challenges 97.8 % of fraud** while adding friction to only **1.5 % of legitimate payments**.
Retraining on a different library version can shift these by about a point.

> **Synthetic data.** Real payment logs are not public, so the demo model is trained on generated data. The figures
> show a correctly validated pipeline, not accuracy on production traffic. Re-train on your own labelled history
> (see [docs/DESIGN_DECISIONS.md](docs/DESIGN_DECISIONS.md#training-on-your-own-data)) before relying on it.

## Configuration

All settings are environment variables (see [.env.example](.env.example)).

| Variable | Default | Purpose |
| --- | --- | --- |
| `FRAUD_SHIELD_ENV` | `development` | `development` · `demo` · `production` (no seed data, no simulator) |
| `FRAUD_SHIELD_DB` | `data/shield.db` | SQLite file |
| `FRAUD_SHIELD_API_KEY` | *(unset)* | if set, all write endpoints require an `X-API-Key` header |
| `FRAUD_SHIELD_RATE_LIMIT` | `0` (off) | max write requests per minute per client IP |
| `FRAUD_SHIELD_CORS` | `*` | comma-separated allowed origins |
| `FRAUD_SHIELD_MAX_BATCH` | `500` | max transactions per batch / CSV request |
| `FRAUD_SHIELD_RETENTION` | `10000` | max decisions kept |
| `FRAUD_SHIELD_LOG_LEVEL` | `INFO` | logging level |

## Project layout

```
run.py                      one-command launcher
backend/
  main.py                   app factory, lifespan, static console
  api/v1.py                 versioned HTTP routes
  config.py  state.py       settings from env · shared app state
  agent.py                  policy: score -> action -> complaint draft
  store.py                  SQLite decisions + audit trail, statistics, schema migrations
  screening.py  csvio.py    score/explain/decide/persist pipeline · CSV import and export
  monitoring.py  modelcard.py  drift (PSI) · model card
  middleware.py             request IDs, rate limit, security headers, error shape
  demo.py  seed.py          traffic simulator · first-run demo history
model/
  features.py               single source of truth for the feature schema
  train.py  explain.py      training and validation · scoring with exact SHAP
  artifacts/                fraud_model.json + metrics.json
data/generate_dataset.py    synthetic transaction generator
frontend/                   console (native ES modules, no build step) + static snapshot
tests/                      90 tests
docs/                       architecture and design decisions
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for diagrams and data flow.

## Docker

```bash
docker compose up --build        # http://localhost:8000, data persisted in a volume
```

## Static preview (GitHub Pages)

The same `frontend/` folder runs without a backend, in **read-only preview** mode, from a bundled snapshot
(`frontend/snapshot/`, regenerated by `python -m backend.export_demo`). The included *Deploy static preview*
workflow publishes it: enable **Settings → Pages → Source: GitHub Actions**, then run the workflow.

## Limitations and roadmap

* Synthetic training data; single-node SQLite; no user accounts (the analyst name is self-reported and an optional API key protects writes). Put it behind your identity provider or gateway for real use.
* Next: feed analyst overrides back into training, streaming ingestion (Kafka / webhooks), PostgreSQL storage, per-analyst assignment and SLAs.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Security issues: [SECURITY.md](SECURITY.md). Released under the [MIT License](LICENSE).
