"""Filter panel widget for the dashboard."""

import tkinter as tk
from tkinter import ttk

from gui.styles import COLOR_BG, COLOR_CARD_BG, FONT_BODY, FONT_SMALL, PADDING


class FilterPanel(tk.Frame):
    """Horizontal filter bar with dropdowns for machine, priority, type, and status."""

    def __init__(self, parent, on_filter_change=None, **kwargs):
        super().__init__(parent, bg=COLOR_CARD_BG, relief="solid", bd=1, **kwargs)
        self._on_filter_change = on_filter_change

        # Machine filter
        tk.Label(self, text="Maquina:", font=FONT_SMALL, bg=COLOR_CARD_BG).pack(
            side="left", padx=(PADDING, 2))
        self.machine_var = tk.StringVar(value="Todas")
        self.machine_combo = ttk.Combobox(
            self, textvariable=self.machine_var, state="readonly", width=25)
        self.machine_combo.pack(side="left", padx=(0, PADDING))
        self.machine_combo.bind("<<ComboboxSelected>>", self._filter_changed)

        # Priority filter
        tk.Label(self, text="Prioridad:", font=FONT_SMALL, bg=COLOR_CARD_BG).pack(
            side="left", padx=(PADDING, 2))
        self.priority_var = tk.StringVar(value="Todas")
        self.priority_combo = ttk.Combobox(
            self, textvariable=self.priority_var, state="readonly", width=12,
            values=["Todas", "Alta", "Media", "Baja", "Sin prioridad"])
        self.priority_combo.pack(side="left", padx=(0, PADDING))
        self.priority_combo.bind("<<ComboboxSelected>>", self._filter_changed)

        # Type filter
        tk.Label(self, text="Tipo:", font=FONT_SMALL, bg=COLOR_CARD_BG).pack(
            side="left", padx=(PADDING, 2))
        self.type_var = tk.StringVar(value="Todos")
        self.type_combo = ttk.Combobox(
            self, textvariable=self.type_var, state="readonly", width=12,
            values=["Todos", "Preventivo", "Correctivo"])
        self.type_combo.pack(side="left", padx=(0, PADDING))
        self.type_combo.bind("<<ComboboxSelected>>", self._filter_changed)

        # Status filter
        tk.Label(self, text="Estado:", font=FONT_SMALL, bg=COLOR_CARD_BG).pack(
            side="left", padx=(PADDING, 2))
        self.status_var = tk.StringVar(value="Pendientes")
        self.status_combo = ttk.Combobox(
            self, textvariable=self.status_var, state="readonly", width=12,
            values=["Todos", "Pendientes", "Vencido", "Proximo", "Programado", "Completado"])
        self.status_combo.pack(side="left", padx=(0, PADDING))
        self.status_combo.bind("<<ComboboxSelected>>", self._filter_changed)

        # Refresh button
        refresh_btn = ttk.Button(self, text="Actualizar", command=self._filter_changed)
        refresh_btn.pack(side="right", padx=PADDING)

    def set_machines(self, machines: list[str]):
        """Update the machine dropdown values."""
        values = ["Todas"] + sorted(set(machines))
        self.machine_combo.config(values=values)

    def get_filters(self) -> dict:
        return {
            "maquina": self.machine_var.get(),
            "prioridad": self.priority_var.get(),
            "tipo": self.type_var.get(),
            "estado": self.status_var.get(),
        }

    def _filter_changed(self, event=None):
        if self._on_filter_change:
            self._on_filter_change(self.get_filters())
