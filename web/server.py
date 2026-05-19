"""Flask web server for the plant-floor dashboard display."""

import logging
import os
import sys
import time
from datetime import datetime

from flask import Flask, jsonify, render_template, request

# Ensure project root is on sys.path when run as module
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.database import get_all_orders, load_config
from core.urgency import filter_latest_per_pampo, get_summary, load_pampo_frequencies, process_orders

logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder="templates")

_order_cache: dict = {"orders": None, "summary": None, "ts": 0.0}
_CACHE_TTL = 60  # seconds — Access DB is read at most once per minute


def _load_orders(config):
    """Load and process orders from the Access database."""
    db_path = config.get("database", "path", fallback="")
    year_from = config.getint("database", "year_from", fallback=2025)

    if not db_path or not os.path.exists(db_path):
        return [], {}

    orders = get_all_orders(db_path, year_from)
    frequencies = load_pampo_frequencies()
    default_freq = config.getint("alertas", "frecuencia_default_dias", fallback=30)
    orders = process_orders(orders, frequencies, default_freq)
    summary = get_summary(orders)
    return orders, summary


def _load_orders_cached(config):
    now = time.time()
    if _order_cache["orders"] is not None and now - _order_cache["ts"] < _CACHE_TTL:
        return _order_cache["orders"], _order_cache["summary"]
    orders, summary = _load_orders(config)
    _order_cache.update({"orders": orders, "summary": summary, "ts": now})
    return orders, summary


def _serialize_order(o):
    return {
        "n_om": o.n_om,
        "maquina": o.maquina,
        "actividad": o.actividad,
        "tipo": "Preventivo" if o.preventivo else ("Correctivo" if o.correctivo else ""),
        "fecha": o.fecha.strftime("%d/%m/%Y") if o.fecha else "",
        "fecha_limite": o.fecha_limite.strftime("%d/%m/%Y") if o.fecha_limite else "",
        "dias_restantes": o.dias_restantes if not o.finalizado else None,
        "estado": o.estado.value,
        "personal": ", ".join(o.personal) if o.personal else "",
        "finalizado": o.finalizado,
        "con_parada": o.con_parada,
    }


@app.route("/")
def dashboard():
    config = load_config()
    orders, summary = _load_orders_cached(config)
    refresh_seconds = config.getint("web", "refresh_seconds", fallback=60)

    show_all = request.args.get("all", "0") == "1"
    if not show_all:
        pending = [o for o in orders if not o.finalizado]
        display_orders = filter_latest_per_pampo(pending)
    else:
        display_orders = orders

    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    return render_template(
        "dashboard.html",
        orders=display_orders,
        summary=summary,
        refresh_seconds=refresh_seconds,
        timestamp=timestamp,
        show_all=show_all,
    )


@app.route("/api/orders")
def api_orders():
    config = load_config()
    orders, summary = _load_orders_cached(config)

    show_all = request.args.get("all", "0") == "1"
    if not show_all:
        pending = [o for o in orders if not o.finalizado]
        display_orders = filter_latest_per_pampo(pending)
    else:
        display_orders = orders

    return jsonify({
        "summary": summary,
        "orders": [_serialize_order(o) for o in display_orders],
    })


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    config = load_config()
    port = config.getint("web", "port", fallback=5000)
    host = config.get("web", "host", fallback="0.0.0.0")
    logger.info("Starting web dashboard on %s:%d", host, port)
    app.run(host=host, port=port, debug=False)
