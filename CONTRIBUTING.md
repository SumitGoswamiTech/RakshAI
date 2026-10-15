# Contributing

Thanks for helping improve Fraud Shield.

## Set up

```bash
python -m venv venv
venv\Scripts\Activate.ps1            # macOS / Linux: source venv/bin/activate
pip install -r requirements-dev.txt
python run.py                        # http://127.0.0.1:8000
```

## Before you open a pull request

```bash
python -m pytest                     # all tests must pass
ruff check .                         # lint must be clean
```

* Add or update tests for any behaviour you change. The suite lives in `tests/`.
* Keep the frontend dependency-free (native ES modules). Build DOM with the helpers in `frontend/js/dom.js`; never
  assign untrusted strings as markup (a test enforces this).
* API changes that break clients belong in a new `/api/v2` router, not in `v1`.
* Schema changes need a migration in `backend/store.py` and a migration test.
* If you retrain the model, commit `model/artifacts/*` and refresh the preview with `python -m backend.export_demo`.
* Update `CHANGELOG.md`.

## Commit style

Short imperative subject lines (`Add CSV export`, `Fix queue paging`), with the reason in the body when it is not obvious.

## Project layout

See the README and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
