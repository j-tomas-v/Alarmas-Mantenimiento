"""Dashboard view with summary cards and color-coded order table."""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Optional

from core.models import EstadoUrgencia, OrdenMantenimiento, Prioridad
from core.urgency import get_summary
from gui.filters import FilterPanel
from gui.styles import (
    COLOR_BG, COLOR_COMPLETADO, COLOR_PROGRAMADO, COLOR_PROXIMO,
    COLOR_TEXT, COLOR_VENCIDO, FONT_SUBTITLE, FONT_TITLE, PADDING,
)
from gui.widgets import ScrollableTreeview, StatusCard


COLUMNS = [
    ("n_om", "N° OM", 70),
    ("maquina", "Maquina", 200),
    ("actividad", "Actividad", 250),
    ("prioridad", "Prioridad", 80),
    ("tipo", "Tipo", 90),
    ("fecha", "Fecha creacion", 100),
    ("fecha_limite", "Fecha limite", 100),
    ("dias", "Dias rest.", 75),
    ("estado", "Estado", 90),
    ("personal", "Personal", 120),
]


def _estado_tag(estado: EstadoUrgencia) -> str:
    return {
        EstadoUrgencia.VENCIDO: "vencido",
        EstadoUrgencia.PROXIMO: "proximo",
        EstadoUrgencia.PROGRAMADO: "programado",
        EstadoUrgencia.COMPLETADO: "completado",
    }.get(estado, "")


def _format_date(dt: Optional[datetime]) -> str:
    if dt is None:
        return ""
    return dt.strftime("%d/%m/%Y")


class DashboardView(tk.Frame):
    """Main dashboard with summary cards, filters, and order table."""

    def __init__(self, parent, app_controller=None, **kwargs):
        super().__init__(parent, bg=COLOR_BG, **kwargs)
        self._controller = app_controller
        self._all_orders: list[OrdenMantenimiento] = []

        self._build_ui()

    def _build_ui(self):
        # Title
        tk.Label(
            self, text="Dashboard", font=FONT_TITLE,
            fg=COLOR_TEXT, bg=COLOR_BG, anchor="w",
        ).pack(fill="x", pady=(0, PADDING))

        # Summary cards row
        self._cards_frame = tk.Frame(self, bg=COLOR_BG)
        self._cards_frame.pack(fill="x", pady=(0, PADDING))

        self._card_pending = StatusCard(
            self._cards_frame, "Pendientes", 0, COLOR_VENCIDO)
        self._card_pending.pack(side="left", padx=(0, PADDING), fill="x", expand=True)

        self._card_overdue = StatusCard(
            self._cards_frame, "Vencidos", 0, COLOR_VENCIDO)
        self._card_overdue.pack(side="left", padx=(0, PADDING), fill="x", expand=True)

        self._card_upcoming = StatusCard(
            self._cards_frame, "Proximos", 0, COLOR_PROXIMO)
        self._card_upcoming.pack(side="left", padx=(0, PADDING), fill="x", expand=True)

        self._card_completed = StatusCard(
            self._cards_frame, "Completados (mes)", 0, COLOR_PROGRAMADO)
        self._card_completed.pack(side="left", fill="x", expand=True)

        # Filter panel
        self._filter_panel = FilterPanel(
            self, on_filter_change=self._apply_filters)
        self._filter_panel.pack(fill="x", pady=(0, PADDING), ipady=5)

        # Orders table
        self._table = ScrollableTreeview(self, columns=COLUMNS)
        self._table.pack(fill="both", expand=True)

        # Bind double-click for detail
        self._table.tree.bind("<Double-1>", self._on_row_double_click)

    def set_orders(self, orders: list[OrdenMantenimiento]):
        """Set the full list of orders and refresh display."""
        self._all_orders = orders

        # Update machine filter values
        machines = sorted(set(o.maquina for o in orders if o.maquina))
        self._filter_panel.set_machines(machines)

        # Update cards
        summary = get_summary(orders)
        self._card_pending.update_value(summary["total_pendientes"], COLOR_VENCIDO)
        self._card_overdue.update_value(summary["vencidos"], COLOR_VENCIDO)
        self._card_upcoming.update_value(summary["proximos"], COLOR_PROXIMO)
        self._card_completed.update_value(summary["completados_mes"], COLOR_PROGRAMADO)

        # Apply current filters
        self._apply_filters(self._filter_panel.get_filters())

    def _apply_filters(self, filters: dict):
        """Filter and display orders based on current filter settings."""
        filtered = self._all_orders

        # Machine filter
        if filters.get("maquina") and filters["maquina"] != "Todas":
            filtered = [o for o in filtered if o.maquina == filters["maquina"]]

        # Priority filter
        if filters.get("prioridad") and filters["prioridad"] != "Todas":
            filtered = [o for o in filtered
                        if o.prioridad.value == filters["prioridad"]]

        # Type filter
        if filters.get("tipo") and filters["tipo"] != "Todos":
            if filters["tipo"] == "Preventivo":
                filtered = [o for o in filtered if o.preventivo]
            elif filters["tipo"] == "Correctivo":
                filtered = [o for o in filtered if o.correctivo]

        # Status filter
        if filters.get("estado") and filters["estado"] != "Todos":
            if filters["estado"] == "Pendientes":
                filtered = [o for o in filtered if not o.finalizado]
            else:
                filtered = [o for o in filtered
                            if o.estado.value == filters["estado"]]

        self._populate_table(filtered)

    def _populate_table(self, orders: list[OrdenMantenimiento]):
        self._table.clear()
        for orden in orders:
            tipo = "Preventivo" if orden.preventivo else ("Correctivo" if orden.correctivo else "")
            values = (
                orden.n_om,
                orden.maquina,
                orden.actividad,
                orden.prioridad.value,
                tipo,
                _format_date(orden.fecha),
                _format_date(orden.fecha_limite),
                orden.dias_restantes if not orden.finalizado else "",
                orden.estado.value,
                ", ".join(orden.personal) if orden.personal else "",
            )
            tag = _estado_tag(orden.estado)
            self._table.insert_row(values, tag)

    def _on_row_double_click(self, event):
        selection = self._table.tree.selection()
        if not selection:
            return
        item = self._table.tree.item(selection[0])
        n_om = item["values"][0]

        # Find the order
        orden = next((o for o in self._all_orders if o.n_om == n_om), None)
        if not orden:
            return

        self._show_detail_popup(orden)

    def _show_detail_popup(self, orden: OrdenMantenimiento):
        popup = tk.Toplevel(self)
        popup.title(f"Detalle OM #{orden.n_om}")
        popup.geometry("500x450")
        popup.resizable(False, False)

        frame = tk.Frame(popup, padx=20, pady=15)
        frame.pack(fill="both", expand=True)

        fields = [
            ("N° OM", orden.n_om),
            ("Maquina", orden.maquina),
            ("Actividad", orden.actividad),
            ("Prioridad", orden.prioridad.value),
            ("Tipo", "Preventivo" if orden.preventivo else "Correctivo"),
            ("Fecha creacion", _format_date(orden.fecha)),
            ("Realizar el dia", _format_date(orden.realizar_el_dia)),
            ("Fecha limite", _format_date(orden.fecha_limite)),
            ("Estado", orden.estado.value),
            ("Dias restantes", orden.dias_restantes if not orden.finalizado else "N/A"),
            ("Severidad", f"{orden.severidad:.1f}"),
            ("Parada produccion", "Si" if orden.con_parada else "No"),
            ("Personal", ", ".join(orden.personal) if orden.personal else "Sin asignar"),
            ("Solicitado por", orden.solicita),
            ("Finalizado", "Si" if orden.finalizado else "No"),
            ("Fecha realizacion", _format_date(orden.fecha_realizacion)),
            ("ID PAMPO", orden.id_pampo),
        ]

        for i, (label, value) in enumerate(fields):
            tk.Label(frame, text=f"{label}:", font=("Segoe UI", 9, "bold"),
                     anchor="w").grid(row=i, column=0, sticky="w", pady=1)
            tk.Label(frame, text=str(value), font=("Segoe UI", 9),
                     anchor="w").grid(row=i, column=1, sticky="w", padx=(10, 0), pady=1)

        if orden.observaciones:
            row = len(fields)
            tk.Label(frame, text="Observaciones:", font=("Segoe UI", 9, "bold"),
                     anchor="w").grid(row=row, column=0, sticky="nw", pady=(5, 0))
            obs_text = tk.Text(frame, height=3, width=40, font=("Segoe UI", 9), wrap="word")
            obs_text.grid(row=row, column=1, sticky="w", padx=(10, 0), pady=(5, 0))
            obs_text.insert("1.0", orden.observaciones)
            obs_text.config(state="disabled")

        ttk.Button(popup, text="Cerrar", command=popup.destroy).pack(pady=10)

    def refresh(self):
        """Called when the view becomes visible."""
        if self._controller and hasattr(self._controller, "refresh_data"):
            self._controller.refresh_data()
