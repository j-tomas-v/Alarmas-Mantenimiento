"""Dashboard view with summary cards and color-coded order table."""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Optional

from core.models import EstadoUrgencia, OrdenMantenimiento
from core.urgency import filter_latest_per_pampo, get_summary
from gui.filters import FilterPanel
from gui.styles import (
    COLOR_BG, COLOR_COMPLETADO, COLOR_PROGRAMADO, COLOR_PROXIMO,
    COLOR_TEXT, COLOR_VENCIDO, FONT_SUBTITLE, FONT_TITLE, PADDING,
)
from gui.widgets import ScrollableTreeview, StatusCard


# "Dias rest." is placed second (right after N° OM) so the most operationally
# relevant information — how many days remain — is the first thing the user
# sees when scanning the table.
COLUMNS = [
    ("n_om", "N° OM", 70),
    ("dias", "Dias rest.", 90),
    ("maquina", "Maquina", 200),
    ("actividad", "Actividad", 270),
    ("tipo", "Tipo", 90),
    ("fecha", "Fecha creacion", 110),
    ("fecha_limite", "Fecha limite", 110),
    ("estado", "Estado", 100),
    ("personal", "Personal", 140),
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
        # Title row with web-dashboard button on the right
        title_row = tk.Frame(self, bg=COLOR_BG)
        title_row.pack(fill="x", pady=(0, PADDING))
        tk.Label(
            title_row, text="Dashboard", font=FONT_TITLE,
            fg=COLOR_TEXT, bg=COLOR_BG, anchor="w",
        ).pack(side="left")
        web_btn = tk.Button(
            title_row, text="🌐  Abrir Dashboard Web",
            bg="#3498DB", fg="white", font=("Segoe UI", 10, "bold"),
            activebackground="#2980B9", activeforeground="white",
            relief="flat", padx=12, pady=4, cursor="hand2",
            command=self._open_web_dashboard,
        )
        web_btn.pack(side="right")

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

        if filters.get("latest_per_pampo"):
            filtered = filter_latest_per_pampo(filtered)

        self._populate_table(filtered)

    def _populate_table(self, orders: list[OrdenMantenimiento]):
        self._table.clear()
        for orden in orders:
            tipo = "Preventivo" if orden.preventivo else ("Correctivo" if orden.correctivo else "")
            # Format days remaining as readable text: "VENCIDA hace X" or "X dias"
            if orden.finalizado:
                dias_text = "—"
            elif orden.dias_restantes is None:
                dias_text = ""
            elif orden.dias_restantes < 0:
                dias_text = f"VENCIDA ({orden.dias_restantes})"
            elif orden.dias_restantes == 0:
                dias_text = "HOY"
            else:
                dias_text = f"{orden.dias_restantes} dias"
            values = (
                orden.n_om,
                dias_text,
                orden.maquina,
                orden.actividad,
                tipo,
                _format_date(orden.fecha),
                _format_date(orden.fecha_limite),
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
            ("Tipo", "Preventivo" if orden.preventivo else "Correctivo"),
            ("Fecha creacion", _format_date(orden.fecha)),
            ("Realizar el dia", _format_date(orden.realizar_el_dia)),
            ("Fecha limite", _format_date(orden.fecha_limite)),
            ("Estado", orden.estado.value),
            ("Dias restantes", orden.dias_restantes if not orden.finalizado else "N/A"),
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

        btn_frame = tk.Frame(popup)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Cerrar", command=popup.destroy).pack(side="left", padx=5)

        if not orden.finalizado and self._controller:
            finalizar_btn = tk.Button(
                btn_frame, text="Finalizar Orden",
                bg="#27AE60", fg="white", font=("Segoe UI", 10, "bold"),
                activebackground="#219A52", activeforeground="white",
                command=lambda: self._confirm_close_order(orden, popup),
            )
            finalizar_btn.pack(side="left", padx=5)

    def _confirm_close_order(self, orden: OrdenMantenimiento, popup):
        if not messagebox.askyesno(
            "Confirmar",
            f"¿Marcar OM #{orden.n_om} como finalizada?\n"
            f"Maquina: {orden.maquina}\n"
            f"Actividad: {orden.actividad}\n\n"
            "Se registrará con la fecha de hoy.",
            parent=popup,
        ):
            return
        success = self._controller.close_order(orden.n_om)
        if success:
            messagebox.showinfo("Orden finalizada", f"OM #{orden.n_om} marcada como completada.", parent=popup)
            popup.destroy()
        else:
            messagebox.showerror("Error", "No se pudo cerrar la orden. Revise el log.", parent=popup)

    def _open_web_dashboard(self):
        """Start the web server (if needed) and open it in the browser."""
        if not self._controller or not hasattr(self._controller, "open_web_dashboard"):
            messagebox.showerror("Error", "Funcion no disponible.")
            return
        if not self._controller.open_web_dashboard():
            messagebox.showerror(
                "Error",
                "No se pudo iniciar el servidor web.\n"
                "Verifique que Flask este instalado: pip install flask",
            )

    def prompt_personal_for_new_order(
        self, new_n_om: int, maquina: str, actividad: str,
        previous_personal: list[str],
    ):
        """Show a dialog asking the user to confirm/edit personnel for the
        auto-created order. Pre-fills with the personnel from the closed order.
        Only invoked by AppController when previous_personal is non-empty."""
        personal_list = []
        if self._controller and hasattr(self._controller, "get_personnel_list"):
            personal_list = self._controller.get_personnel_list()

        popup = tk.Toplevel(self)
        popup.title(f"Personal para nueva OM #{new_n_om}")
        popup.geometry("440x280")
        popup.resizable(False, False)
        popup.grab_set()

        frame = tk.Frame(popup, padx=20, pady=15)
        frame.pack(fill="both", expand=True)

        tk.Label(
            frame, text=f"Nueva OM generada para:", font=("Segoe UI", 9),
        ).pack(anchor="w")
        tk.Label(
            frame, text=f"{maquina} — {actividad}",
            font=("Segoe UI", 10, "bold"), wraplength=400, justify="left",
        ).pack(anchor="w", pady=(0, 10))
        tk.Label(
            frame,
            text="Personal de la OM anterior precargado. Confirme o modifique:",
            font=("Segoe UI", 9), fg="#555",
        ).pack(anchor="w", pady=(0, 8))

        pm_vars = []
        current = list(previous_personal) + ["", "", ""]
        for i, label in enumerate(("PM1", "PM2", "PM3")):
            row = tk.Frame(frame)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=f"{label}:", width=5, anchor="w").pack(side="left")
            var = tk.StringVar(value=current[i])
            combo = ttk.Combobox(
                row, textvariable=var, values=[""] + personal_list, width=32)
            combo.pack(side="left", padx=(5, 0))
            pm_vars.append(var)

        def _save():
            pm1, pm2, pm3 = (v.get().strip() for v in pm_vars)
            if self._controller and hasattr(self._controller, "assign_personal"):
                ok = self._controller.assign_personal(new_n_om, pm1, pm2, pm3)
                if ok:
                    popup.destroy()
                else:
                    messagebox.showerror(
                        "Error", "No se pudo guardar el personal.", parent=popup)

        btn_row = tk.Frame(frame)
        btn_row.pack(pady=(15, 0))
        ttk.Button(btn_row, text="Guardar", command=_save).pack(side="left", padx=5)
        ttk.Button(btn_row, text="Omitir", command=popup.destroy).pack(side="left", padx=5)

    def refresh(self):
        """Called when the view becomes visible."""
        if self._controller and hasattr(self._controller, "refresh_data"):
            self._controller.refresh_data()
