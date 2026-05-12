import json
import logging
import os
from datetime import datetime, timedelta

from core.models import EstadoUrgencia, OrdenMantenimiento

logger = logging.getLogger(__name__)

# Severity is now derived purely from days remaining: lower (more negative)
# = more urgent. Priority and production-stop bonus were removed because the
# user no longer relies on priority levels.


def load_pampo_frequencies(path: str = "data/pampo_frequencies.json") -> dict[int, int]:
    """Load PAMPO frequency configuration. Returns {id_pampo: frecuencia_dias}."""
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {int(k): v["frecuencia_dias"] for k, v in data.items()}
    except Exception as e:
        logger.error("Error loading PAMPO frequencies: %s", e)
        return {}


def get_upcoming_threshold(freq: int) -> int:
    """Return how many days before expiration an order should be flagged as Próximo."""
    if freq < 60:
        return 7
    elif freq <= 90:
        return 14
    return 30


def calculate_urgency(
    orden: OrdenMantenimiento,
    frequencies: dict[int, int],
    default_frequency: int = 30,
) -> OrdenMantenimiento:
    """Calculate urgency fields for an order and return the updated order."""
    if orden.finalizado:
        orden.estado = EstadoUrgencia.COMPLETADO
        orden.severidad = -999
        return orden

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    freq = frequencies.get(orden.id_pampo, default_frequency)

    # Deadline is always Fecha + frecuencia; realizar_el_dia is only indicative
    if orden.fecha:
        fecha_limite = orden.fecha + timedelta(days=freq)
    else:
        fecha_limite = today
    orden.fecha_limite = fecha_limite

    # Days remaining (negative = overdue)
    dias_restantes = (fecha_limite - today).days
    orden.dias_restantes = dias_restantes

    upcoming_days = get_upcoming_threshold(freq)

    # Status
    if dias_restantes < 0:
        orden.estado = EstadoUrgencia.VENCIDO
    elif dias_restantes <= upcoming_days:
        orden.estado = EstadoUrgencia.PROXIMO
    else:
        orden.estado = EstadoUrgencia.PROGRAMADO

    # Severity = -days_remaining (overdue orders sort first)
    orden.severidad = -dias_restantes

    return orden


def process_orders(
    orders: list[OrdenMantenimiento],
    frequencies: dict[int, int],
    default_frequency: int = 30,
) -> list[OrdenMantenimiento]:
    """Calculate urgency for all orders and return sorted by severity (most urgent first)."""
    for orden in orders:
        calculate_urgency(orden, frequencies, default_frequency)
    return sorted(orders, key=lambda o: o.severidad, reverse=True)


def filter_latest_per_pampo(orders: list[OrdenMantenimiento]) -> list[OrdenMantenimiento]:
    """Keep only the most recent order (highest n_om) for each unique id_pampo."""
    latest: dict[int, OrdenMantenimiento] = {}
    for o in orders:
        if o.id_pampo and (o.id_pampo not in latest or o.n_om > latest[o.id_pampo].n_om):
            latest[o.id_pampo] = o
    return sorted(latest.values(), key=lambda o: o.severidad, reverse=True)


def get_summary(orders: list[OrdenMantenimiento]) -> dict:
    """Get summary statistics from processed orders."""
    today = datetime.now()
    current_month = today.month
    current_year = today.year

    total_pending = sum(1 for o in orders if not o.finalizado)
    overdue = sum(1 for o in orders if o.estado == EstadoUrgencia.VENCIDO)
    upcoming = sum(1 for o in orders if o.estado == EstadoUrgencia.PROXIMO)
    completed_this_month = sum(
        1 for o in orders
        if o.finalizado and o.fecha_realizacion
        and o.fecha_realizacion.month == current_month
        and o.fecha_realizacion.year == current_year
    )

    return {
        "total_pendientes": total_pending,
        "vencidos": overdue,
        "proximos": upcoming,
        "completados_mes": completed_this_month,
    }
