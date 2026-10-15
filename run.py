"""
One-command launcher for Fraud Shield.

    python run.py                       start the console + API on http://127.0.0.1:8000
    python run.py --train               retrain the model first (regenerates data if missing)
    python run.py --port 9000 --no-browser
    python run.py --host 0.0.0.0        listen on all interfaces (containers, LAN)
    python run.py --db path/to/x.db     use a different database file
    python run.py --env production      no demo data, no simulator (see README, "Configuration")

On first run it builds anything that is missing (dataset -> model -> static snapshot), so a
fresh clone works with just `pip install -r requirements.txt`.
"""

import argparse
import os
import sys
import threading
import webbrowser

from model.features import DATA_PATH, METRICS_PATH, MODEL_PATH


def ensure_artifacts(force: bool) -> None:
    if not force and MODEL_PATH.exists() and METRICS_PATH.exists():
        return
    from backend.export_demo import export
    from model.train import train

    print("Training the fraud model (about 15-30 s)..." if DATA_PATH.exists()
          else "Generating the synthetic dataset and training the model (under a minute)...")
    m = train()
    export()
    print(f"Done: {m['recall_fraud_class']:.1%} recall at {m['precision_fraud_class']:.1%} precision "
          f"on the held-out test set.\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--train", action="store_true", help="retrain the model before starting")
    ap.add_argument("--reload", action="store_true", help="auto-reload on code changes (development)")
    ap.add_argument("--no-browser", action="store_true", help="do not open the console automatically")
    ap.add_argument("--db", help="SQLite database file (default data/shield.db)")
    ap.add_argument("--env", choices=["development", "demo", "production"], help="deployment mode")
    a = ap.parse_args(argv)

    if a.db:
        os.environ["FRAUD_SHIELD_DB"] = a.db
    if a.env:
        os.environ["FRAUD_SHIELD_ENV"] = a.env
    ensure_artifacts(a.train)

    import uvicorn

    shown = "127.0.0.1" if a.host in ("0.0.0.0", "::") else a.host
    url = f"http://{shown}:{a.port}"
    print(f"Fraud Shield running at {url}   (API docs: {url}/docs)   Ctrl+C to stop")
    if not a.no_browser:
        threading.Timer(1.5, webbrowser.open, args=(url,)).start()
    uvicorn.run("backend.main:app", host=a.host, port=a.port, reload=a.reload, log_level="info")
    return 0


if __name__ == "__main__":
    sys.exit(main())
