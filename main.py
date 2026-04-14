"""ATT Maintenance Alarm System - Entry point."""

import logging
import os
import sys
import threading
import time
from datetime import datetime

import schedule

from core.alerts import create_default_registry, is_alert_in_cooldown, log_alert_sent
from core.database import check_driver_installed, get_all_orders, get_all_pampo, load_config
from core.email_service import send_alert_email
from core.models import Alert
from core.urgency import load_pampo_frequencies, process_orders
from gui.alerts_view import AlertsView
from gui.app import App
from gui.dashboard import DashboardView
from gui.settings_view import SettingsView
from gui.vehicle_mileage import VehicleMileageView

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("att_mantenimiento.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class AppController:
    """Central controller that ties together database, urgency engine, alerts, and GUI."""

    def __init__(self):
        self.config = load_config()
        self.app = App()
        self.registry = create_default_registry()
        self.orders = []
        self.alerts = []
        self._scheduler_running = False

        self._setup_views()
        self._load_initial_data()
        self._start_scheduler()

    def _setup_views(self):
        # Register views with the app
        self.app.add_view("dashboard", "Dashboard", DashboardView, app_controller=self)
        self.app.add_view("alertas", "Alertas", AlertsView, app_controller=self)
        self.app.add_view("vehiculos", "Vehiculos", VehicleMileageView)
        self.app.add_view("config", "Configuracion", SettingsView, app_controller=self)

        # Load config into settings view
        settings_view: SettingsView = self.app.get_view("config")
        settings_view.load_from_config(self.config)

        # Set alert registry and SMTP config
        alerts_view: AlertsView = self.app.get_view("alertas")
        alerts_view.set_registry(self.registry)
        self._update_smtp_config()

        # Show dashboard by default
        self.app.show_view("dashboard")

    def _load_initial_data(self):
        """Load data from the database."""
        db_path = self.config.get("database", "path", fallback="")
        if not db_path or not os.path.exists(db_path):
            self.app.set_status("Base de datos no encontrada. Configure la ruta en Configuracion.")
            logger.warning("Database path not found: %s", db_path)
            return

        if not check_driver_installed():
            self.app.set_status(
                "Driver ODBC de Access no instalado. "
                "Descargue 'Microsoft Access Database Engine Redistributable'.")
            logger.error("Microsoft Access ODBC driver not found")
            return

        self.refresh_data()

    def refresh_data(self):
        """Refresh orders from the database and update the dashboard."""
        db_path = self.config.get("database", "path", fallback="")
        year_from = self.config.getint("database", "year_from", fallback=2025)

        if not db_path or not os.path.exists(db_path):
            return

        try:
            self.orders = get_all_orders(db_path, year_from)
            frequencies = load_pampo_frequencies()
            default_freq = self.config.getint("alertas", "frecuencia_default_dias", fallback=30)
            upcoming_days = self.config.getint("alertas", "dias_aviso_proximo", fallback=7)

            self.orders = process_orders(self.orders, frequencies, default_freq, upcoming_days)

            # Update dashboard
            dashboard: DashboardView = self.app.get_view("dashboard")
            dashboard.set_orders(self.orders)

            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            self.app.set_status(f"Ultima actualizacion: {timestamp} | {len(self.orders)} ordenes cargadas")
            logger.info("Data refreshed: %d orders loaded", len(self.orders))
        except Exception as e:
            self.app.set_status(f"Error al cargar datos: {e}")
            logger.error("Error refreshing data: %s", e)

    def evaluate_alerts(self):
        """Run all alert evaluators and update the alerts view."""
        config_dict = {
            "alertas": dict(self.config.items("alertas")) if self.config.has_section("alertas") else {},
            "recipients": dict(self.config.items("recipients")) if self.config.has_section("recipients") else {},
        }

        self.alerts = self.registry.evaluate_all(self.orders, config_dict)

        # Update alerts view
        alerts_view: AlertsView = self.app.get_view("alertas")
        smtp_config = dict(self.config.items("smtp")) if self.config.has_section("smtp") else {}
        smtp_config.update(config_dict.get("recipients", {}))
        alerts_view.set_smtp_config(smtp_config)
        alerts_view.set_alerts(self.alerts)

        self.app.set_alerts_count(len(self.alerts))
        logger.info("Alerts evaluated: %d alerts found", len(self.alerts))

    def _update_smtp_config(self):
        alerts_view: AlertsView = self.app.get_view("alertas")
        if self.config.has_section("smtp"):
            smtp_config = dict(self.config.items("smtp"))
            if self.config.has_section("recipients"):
                smtp_config.update(dict(self.config.items("recipients")))
            alerts_view.set_smtp_config(smtp_config)

    def _start_scheduler(self):
        """Start background scheduler for periodic alert checking."""
        interval_hours = self.config.getint("alertas", "intervalo_check_horas", fallback=4)

        def scheduled_check():
            now = datetime.now()
            start_hour = 7
            end_hour = 18
            try:
                start_str = self.config.get("alertas", "horario_inicio", fallback="07:00")
                end_str = self.config.get("alertas", "horario_fin", fallback="18:00")
                start_hour = int(start_str.split(":")[0])
                end_hour = int(end_str.split(":")[0])
            except (ValueError, IndexError):
                pass

            if start_hour <= now.hour < end_hour:
                logger.info("Running scheduled alert check")
                # Use after() to run on the main thread
                self.app.after(0, self._scheduled_refresh_and_alert)

        schedule.every(interval_hours).hours.do(scheduled_check)

        def scheduler_loop():
            self._scheduler_running = True
            while self._scheduler_running:
                schedule.run_pending()
                time.sleep(60)

        thread = threading.Thread(target=scheduler_loop, daemon=True)
        thread.start()
        logger.info("Background scheduler started (every %d hours)", interval_hours)

    def _scheduled_refresh_and_alert(self):
        """Called by scheduler on the main thread."""
        self.refresh_data()
        self.evaluate_alerts()

        # Auto-send alerts that aren't in cooldown
        if not self.config.has_section("smtp") or not self.config.get("smtp", "server", fallback=""):
            return

        smtp_config = dict(self.config.items("smtp"))
        cooldown = self.config.getint("alertas", "cooldown_dias", fallback=7)
        config_dict = {
            "recipients": dict(self.config.items("recipients")) if self.config.has_section("recipients") else {},
        }

        sent = 0
        for alert in self.alerts:
            if is_alert_in_cooldown(alert, cooldown):
                continue
            evaluator = self.registry.get_evaluator(alert.tipo)
            if not evaluator:
                continue
            template = evaluator.get_email_template()
            recipients = evaluator.get_recipients(alert, config_dict)
            if not recipients:
                continue
            if send_alert_email(alert, smtp_config, recipients, template):
                log_alert_sent(alert)
                sent += 1

        if sent > 0:
            logger.info("Auto-sent %d alert emails", sent)

    def run(self):
        """Start the application main loop."""
        logger.info("Application starting")
        self.app.mainloop()
        self._scheduler_running = False
        logger.info("Application closed")


def main():
    controller = AppController()
    controller.run()


if __name__ == "__main__":
    main()
