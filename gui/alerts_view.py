"""Alerts view - shows active alerts with actions to send emails or dismiss."""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Optional

from core.alerts import AlertRegistry, is_alert_in_cooldown, log_alert_sent
from core.email_service import send_alert_email
from core.models import Alert
from gui.styles import (
    COLOR_BG, COLOR_BTN_DANGER, COLOR_BTN_PRIMARY, COLOR_BTN_SUCCESS,
    COLOR_TEXT, COLOR_VENCIDO, COLOR_PROXIMO, FONT_BODY, FONT_SUBTITLE,
    FONT_TITLE, PADDING,
)
from gui.widgets import ScrollableTreeview


ALERT_COLUMNS = [
    ("tipo", "Tipo", 180),
    ("mensaje", "Descripcion", 450),
    ("severidad", "Severidad", 80),
    ("timestamp", "Fecha", 130),
]


class AlertsView(tk.Frame):
    """View for managing and sending alert notifications."""

    def __init__(self, parent, app_controller=None, **kwargs):
        super().__init__(parent, bg=COLOR_BG, **kwargs)
        self._controller = app_controller
        self._alerts: list[Alert] = []
        self._registry: Optional[AlertRegistry] = None
        self._smtp_config: dict = {}

        self._build_ui()

    def _build_ui(self):
        # Title
        tk.Label(
            self, text="Alertas", font=FONT_TITLE,
            fg=COLOR_TEXT, bg=COLOR_BG, anchor="w",
        ).pack(fill="x", pady=(0, PADDING))

        # Filter bar
        filter_frame = tk.Frame(self, bg=COLOR_BG)
        filter_frame.pack(fill="x", pady=(0, PADDING))

        tk.Label(filter_frame, text="Filtrar por tipo:", font=FONT_BODY,
                 bg=COLOR_BG).pack(side="left", padx=(0, 5))
        self._type_var = tk.StringVar(value="Todos")
        self._type_combo = ttk.Combobox(
            filter_frame, textvariable=self._type_var, state="readonly", width=25,
            values=["Todos"])
        self._type_combo.pack(side="left", padx=(0, PADDING))
        self._type_combo.bind("<<ComboboxSelected>>", self._apply_filter)

        # Action buttons
        btn_frame = tk.Frame(filter_frame, bg=COLOR_BG)
        btn_frame.pack(side="right")

        ttk.Button(btn_frame, text="Evaluar alertas",
                   command=self._evaluate_alerts).pack(side="left", padx=3)
        ttk.Button(btn_frame, text="Enviar seleccionada",
                   command=self._send_selected).pack(side="left", padx=3)
        ttk.Button(btn_frame, text="Enviar todas pendientes",
                   command=self._send_all).pack(side="left", padx=3)

        # Alerts table
        self._table = ScrollableTreeview(self, columns=ALERT_COLUMNS)
        self._table.pack(fill="both", expand=True)

        # Info label
        self._info_var = tk.StringVar(value="Presione 'Evaluar alertas' para verificar el estado actual.")
        tk.Label(
            self, textvariable=self._info_var, font=FONT_BODY,
            fg=COLOR_TEXT, bg=COLOR_BG, anchor="w",
        ).pack(fill="x", pady=(PADDING, 0))

    def set_alerts(self, alerts: list[Alert]):
        """Update the alerts list."""
        self._alerts = alerts
        # Update type filter values
        types = sorted(set(a.display_name for a in alerts))
        self._type_combo.config(values=["Todos"] + types)
        self._apply_filter()
        self._info_var.set(f"{len(alerts)} alertas encontradas.")

    def set_registry(self, registry: AlertRegistry):
        self._registry = registry

    def set_smtp_config(self, config: dict):
        self._smtp_config = config

    def _apply_filter(self, event=None):
        self._table.clear()
        tipo_filter = self._type_var.get()
        for alert in self._alerts:
            if tipo_filter != "Todos" and alert.display_name != tipo_filter:
                continue

            tag = "vencido" if "vencido" in alert.tipo.lower() else (
                "proximo" if "proximo" in alert.tipo.lower() or "upcoming" in alert.tipo.lower() else "")

            self._table.insert_row((
                alert.display_name,
                alert.mensaje,
                f"{alert.severidad:.0f}",
                alert.timestamp.strftime("%d/%m/%Y %H:%M"),
            ), tag)

    def _evaluate_alerts(self):
        if self._controller and hasattr(self._controller, "evaluate_alerts"):
            self._controller.evaluate_alerts()

    def _send_selected(self):
        selection = self._table.tree.selection()
        if not selection:
            messagebox.showwarning("Sin seleccion", "Seleccione una alerta para enviar.")
            return

        item = self._table.tree.item(selection[0])
        # Find matching alert
        msg = item["values"][1]
        alert = next((a for a in self._alerts if a.mensaje == msg), None)
        if not alert:
            return

        self._send_single_alert(alert)

    def _send_single_alert(self, alert: Alert):
        if not self._smtp_config.get("server"):
            messagebox.showerror("Error", "Configure el servidor SMTP en Configuracion.")
            return

        cooldown = int(self._smtp_config.get("cooldown_dias", 7) if isinstance(self._smtp_config, dict)
                       else 7)
        if is_alert_in_cooldown(alert, cooldown):
            messagebox.showinfo("Info", "Esta alerta ya fue enviada recientemente (periodo de cooldown).")
            return

        evaluator = self._registry.get_evaluator(alert.tipo) if self._registry else None
        template = evaluator.get_email_template() if evaluator else "overdue_alert.html"
        recipients = (evaluator.get_recipients(alert, {"recipients": self._smtp_config})
                      if evaluator else [])

        if not recipients:
            messagebox.showwarning("Sin destinatarios",
                                   "No hay destinatarios configurados para este tipo de alerta.")
            return

        success = send_alert_email(alert, self._smtp_config, recipients, template)
        if success:
            log_alert_sent(alert)
            messagebox.showinfo("Enviado", f"Email enviado a: {', '.join(recipients)}")
        else:
            messagebox.showerror("Error", "No se pudo enviar el email. Verifique la configuracion SMTP.")

    def _send_all(self):
        if not self._smtp_config.get("server"):
            messagebox.showerror("Error", "Configure el servidor SMTP en Configuracion.")
            return

        sent = 0
        skipped = 0
        failed = 0
        cooldown = 7

        for alert in self._alerts:
            if is_alert_in_cooldown(alert, cooldown):
                skipped += 1
                continue

            evaluator = self._registry.get_evaluator(alert.tipo) if self._registry else None
            template = evaluator.get_email_template() if evaluator else "overdue_alert.html"
            recipients = (evaluator.get_recipients(alert, {"recipients": self._smtp_config})
                          if evaluator else [])

            if not recipients:
                skipped += 1
                continue

            success = send_alert_email(alert, self._smtp_config, recipients, template)
            if success:
                log_alert_sent(alert)
                sent += 1
            else:
                failed += 1

        messagebox.showinfo(
            "Resultado",
            f"Enviados: {sent}\nOmitidos (cooldown): {skipped}\nFallidos: {failed}")

    def refresh(self):
        if self._controller and hasattr(self._controller, "evaluate_alerts"):
            self._controller.evaluate_alerts()
