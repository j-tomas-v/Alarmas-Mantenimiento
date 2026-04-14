import json
import logging
import os
from datetime import datetime, timedelta

from core.models import EstadoUrgencia, OrdenMantenimiento, Prioridad

logger = logging.getLogger(__name__)

PRIORITY_MULTIPLIER = {
    Prioridad.ALTA: 3,
    Prioridad.MEDIA: 2,
    Prioridad.BAJA: 1,
    Prioridad.NINGUNA: 1,
}

PRODUCTION_STOP_BONUS = 50


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


def calculate_urgency(
    orden: OrdenMantenimiento,
    frequencies: dict[int, int],
    default_frequency: int = 30,
    upcoming_days: int = 7,
) -> OrdenMantenimiento:
    """Calculate urgency fields for an order and return the updated order."""
    if orden.finalizado:
        orden.estado = EstadoUrgencia.COMPLETADO
        orden.severidad = -999
        return orden

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    freq = frequencies.get(orden.id_pampo, default_frequency)

    # Determine deadline
    if orden.realizar_el_dia:
        fecha_limite = orden.realizar_el_dia
    elif orden.fecha:
        fecha_limite = orden.fecha + timedelta(days=freq)
    else:
        fecha_limite = today
    orden.fecha_limite = fecha_limite

    # Days remaining (negative = overdue)
    dias_restantes = (fecha_limite - today).days
    orden.dias_restantes = dias_restantes

    # Status
    if dias_restantes < 0:
        orden.estado = EstadoUrgencia.VENCIDO
    elif dias_restantes <= upcoming_days:
        orden.estado = EstadoUrgencia.PROXIMO
    else:
        orden.estado = EstadoUrgencia.PROGRAMADO

    # Severity score (higher = more urgent)
    base = -dias_restantes
    mult = PRIORITY_MULTIPLIER[orden.prioridad]
    bonus = PRODUCTION_STOP_BONUS if orden.con_parada else 0
    orden.severidad = base * mult + bonus

    return orden


def process_orders(
    orders: list[OrdenMantenimiento],
    frequencies: dict[int, int],
    default_frequency: int = 30,
    upcoming_days: int = 7,
) -> list[OrdenMantenimiento]:
    """Calculate urgency for all orders and return sorted by severity (most urgent first)."""
    for orden in orders:
        calculate_urgency(orden, frequencies, default_frequency, upcoming_days)
    return sorted(orders, key=lambda o: o.severidad, reverse=True)


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
