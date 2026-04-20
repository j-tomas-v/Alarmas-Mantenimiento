"""Extensible alert system using Strategy + Registry pattern."""

import json
import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional

from core.models import Alert, EstadoUrgencia, MileageRecord, OrdenMantenimiento, Prioridad
from core.personal_directory import get_emails_for

logger = logging.getLogger(__name__)

ALERT_LOG_PATH = "data/alert_log.json"
MILEAGE_PATH = "data/vehicle_mileage.json"

# Vehicle PAMPO IDs (42-45)
VEHICLE_PAMPO_IDS = {42, 43, 44, 45}


class AlertEvaluator(ABC):
    """Base class for alert evaluators. Implement this to add new alert types."""

    alert_type: str = ""
    display_name: str = ""

    @abstractmethod
    def evaluate(self, orders: list[OrdenMantenimiento], config: dict) -> list[Alert]:
        """Evaluate orders and return alerts that should fire."""

    @abstractmethod
    def get_email_template(self) -> str:
        """Return the filename of the HTML email template."""

    def get_recipients(self, alert: Alert, config: dict) -> list[str]:
        """Return email recipients for this alert. Override for custom routing."""
        recipients_str = config.get("recipients", {}).get("mantenimiento", "")
        base = [r.strip() for r in recipients_str.split(",") if r.strip()]
        # Add emails of assigned personnel if available
        if alert.orden and alert.orden.personal:
            personal_emails = get_emails_for(alert.orden.personal)
            for email in personal_emails:
                if email not in base:
                    base.append(email)
        return base


class OverdueMaintenanceEvaluator(AlertEvaluator):
    alert_type = "overdue_maintenance"
    display_name = "Mantenimiento vencido"

    def evaluate(self, orders, config):
        alerts = []
        for o in orders:
            if o.estado == EstadoUrgencia.VENCIDO:
                alerts.append(Alert(
                    tipo=self.alert_type,
                    display_name=self.display_name,
                    orden=o,
                    mensaje=(
                        f"OM #{o.n_om} - {o.maquina}: {o.actividad} "
                        f"vencido hace {abs(o.dias_restantes)} dias "
                        f"(Prioridad: {o.prioridad.value})"
                    ),
                    severidad=o.severidad,
                ))
        return alerts

    def get_email_template(self):
        return "overdue_alert.html"


class UpcomingMaintenanceEvaluator(AlertEvaluator):
    alert_type = "upcoming_maintenance"
    display_name = "Mantenimiento proximo"

    def evaluate(self, orders, config):
        alerts = []
        for o in orders:
            if o.estado == EstadoUrgencia.PROXIMO:
                alerts.append(Alert(
                    tipo=self.alert_type,
                    display_name=self.display_name,
                    orden=o,
                    mensaje=(
                        f"OM #{o.n_om} - {o.maquina}: {o.actividad} "
                        f"vence en {o.dias_restantes} dias "
                        f"(Prioridad: {o.prioridad.value})"
                    ),
                    severidad=o.severidad,
                ))
        return alerts

    def get_email_template(self):
        return "upcoming_alert.html"


class VehicleMileageRequestEvaluator(AlertEvaluator):
    alert_type = "vehicle_mileage_request"
    display_name = "Solicitud de kilometraje"

    def evaluate(self, orders, config):
        alerts = []
        days_threshold = int(config.get("alertas", {}).get("cooldown_dias", 14))

        # Load mileage records
        records = self._load_mileage()
        if not records:
            # No mileage ever recorded - alert for all vehicles
            alerts.append(Alert(
                tipo=self.alert_type,
                display_name=self.display_name,
                orden=None,
                mensaje="No hay registros de kilometraje. Solicitar datos a conductores.",
                severidad=100,
            ))
            return alerts

        # Check last record date per vehicle
        last_by_vehicle: dict[str, datetime] = {}
        for r in records:
            try:
                dt = datetime.fromisoformat(r["fecha"])
                vehicle = r["vehiculo"]
                if vehicle not in last_by_vehicle or dt > last_by_vehicle[vehicle]:
                    last_by_vehicle[vehicle] = dt
            except (KeyError, ValueError):
                continue

        today = datetime.now()
        for vehicle, last_date in last_by_vehicle.items():
            days_since = (today - last_date).days
            if days_since > days_threshold:
                alerts.append(Alert(
                    tipo=self.alert_type,
                    display_name=self.display_name,
                    orden=None,
                    mensaje=(
                        f"Vehiculo '{vehicle}': ultimo registro de km hace "
                        f"{days_since} dias. Solicitar actualizacion."
                    ),
                    severidad=float(days_since),
                ))

        return alerts

    def get_email_template(self):
        return "vehicle_request.html"

    def get_recipients(self, alert, config):
        recipients_str = config.get("recipients", {}).get("conductores", "")
        return [r.strip() for r in recipients_str.split(",") if r.strip()]

    def _load_mileage(self) -> list[dict]:
        if not os.path.exists(MILEAGE_PATH):
            return []
        try:
            with open(MILEAGE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []


class HighPriorityUnassignedEvaluator(AlertEvaluator):
    alert_type = "high_priority_unassigned"
    display_name = "Alta prioridad sin asignar"

    def evaluate(self, orders, config):
        alerts = []
        for o in orders:
            if (o.prioridad == Prioridad.ALTA
                    and not o.finalizado
                    and not o.personal):
                alerts.append(Alert(
                    tipo=self.alert_type,
                    display_name=self.display_name,
                    orden=o,
                    mensaje=(
                        f"OM #{o.n_om} - {o.maquina}: {o.actividad} "
                        f"es de ALTA prioridad y no tiene personal asignado"
                    ),
                    severidad=o.severidad + 25,
                ))
        return alerts

    def get_email_template(self):
        return "overdue_alert.html"


class AlertRegistry:
    """Central registry for alert evaluators."""

    def __init__(self):
        self._evaluators: dict[str, AlertEvaluator] = {}

    def register(self, evaluator: AlertEvaluator):
        self._evaluators[evaluator.alert_type] = evaluator

    def unregister(self, alert_type: str):
        self._evaluators.pop(alert_type, None)

    def evaluate_all(self, orders: list[OrdenMantenimiento], config: dict) -> list[Alert]:
        all_alerts = []
        for evaluator in self._evaluators.values():
            try:
                alerts = evaluator.evaluate(orders, config)
                all_alerts.extend(alerts)
            except Exception as e:
                logger.error("Error in evaluator %s: %s", evaluator.alert_type, e)
        return sorted(all_alerts, key=lambda a: a.severidad, reverse=True)

    def get_evaluator(self, alert_type: str) -> Optional[AlertEvaluator]:
        return self._evaluators.get(alert_type)

    def list_evaluators(self) -> list[AlertEvaluator]:
        return list(self._evaluators.values())


def create_default_registry() -> AlertRegistry:
    """Create a registry with all built-in evaluators."""
    registry = AlertRegistry()
    registry.register(OverdueMaintenanceEvaluator())
    registry.register(UpcomingMaintenanceEvaluator())
    registry.register(VehicleMileageRequestEvaluator())
    registry.register(HighPriorityUnassignedEvaluator())
    return registry


# Alert log management

def load_alert_log() -> list[dict]:
    if not os.path.exists(ALERT_LOG_PATH):
        return []
    try:
        with open(ALERT_LOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_alert_log(log: list[dict]):
    os.makedirs(os.path.dirname(ALERT_LOG_PATH), exist_ok=True)
    with open(ALERT_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False, default=str)


def is_alert_in_cooldown(alert: Alert, cooldown_days: int = 7) -> bool:
    """Check if this alert was already sent within the cooldown period."""
    log = load_alert_log()
    cutoff = datetime.now() - timedelta(days=cooldown_days)
    n_om = alert.orden.n_om if alert.orden else 0

    for entry in log:
        if (entry.get("tipo") == alert.tipo
                and entry.get("n_om") == n_om):
            try:
                sent_at = datetime.fromisoformat(entry["timestamp"])
                if sent_at > cutoff:
                    return True
            except (KeyError, ValueError):
                continue
    return False


def log_alert_sent(alert: Alert):
    """Record that an alert was sent."""
    log = load_alert_log()
    log.append({
        "tipo": alert.tipo,
        "n_om": alert.orden.n_om if alert.orden else 0,
        "mensaje": alert.mensaje,
        "timestamp": datetime.now().isoformat(),
    })
    save_alert_log(log)
