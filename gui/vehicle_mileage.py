"""Vehicle mileage input form and history view."""

import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from core.models import MileageRecord
from gui.styles import COLOR_BG, COLOR_CARD_BG, COLOR_TEXT, FONT_BODY, FONT_SUBTITLE, FONT_TITLE, PADDING
from gui.widgets import ScrollableTreeview

MILEAGE_PATH = "data/vehicle_mileage.json"

VEHICLES = [
    "Renault Master",
    "Camion Iveco",
    "Toyota Hiace",
]

HISTORY_COLUMNS = [
    ("vehiculo", "Vehiculo", 160),
    ("km", "Kilometraje", 100),
    ("fecha", "Fecha", 100),
    ("registrado", "Registrado por", 140),
    ("notas", "Notas", 200),
]


def _load_mileage() -> list[dict]:
    if not os.path.exists(MILEAGE_PATH):
        return []
    try:
        with open(MILEAGE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save_mileage(records: list[dict]):
    os.makedirs(os.path.dirname(MILEAGE_PATH), exist_ok=True)
    with open(MILEAGE_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)


def _get_last_km(records: list[dict], vehicle: str) -> int:
    """Get the last recorded km for a vehicle."""
    vehicle_records = [r for r in records if r.get("vehiculo") == vehicle]
    if not vehicle_records:
        return 0
    return max(r.get("km", 0) for r in vehicle_records)


class VehicleMileageView(tk.Frame):
    """Vehicle mileage tracking form and history."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLOR_BG, **kwargs)
        self._build_ui()

    def _build_ui(self):
        # Title
        tk.Label(
            self, text="Kilometraje de Vehiculos", font=FONT_TITLE,
            fg=COLOR_TEXT, bg=COLOR_BG, anchor="w",
        ).pack(fill="x", pady=(0, PADDING))

        # Form frame
        form_frame = tk.LabelFrame(self, text="Nuevo registro", font=FONT_SUBTITLE,
                                   bg=COLOR_CARD_BG, padx=15, pady=10)
        form_frame.pack(fill="x", pady=(0, PADDING))

        # Vehicle
        row0 = tk.Frame(form_frame, bg=COLOR_CARD_BG)
        row0.pack(fill="x", pady=3)
        tk.Label(row0, text="Vehiculo:", font=FONT_BODY, bg=COLOR_CARD_BG, width=15,
                 anchor="w").pack(side="left")
        self._vehicle_var = tk.StringVar(value=VEHICLES[0])
        ttk.Combobox(row0, textvariable=self._vehicle_var, state="readonly",
                     values=VEHICLES, width=30).pack(side="left")

        # Km
        row1 = tk.Frame(form_frame, bg=COLOR_CARD_BG)
        row1.pack(fill="x", pady=3)
        tk.Label(row1, text="Kilometraje:", font=FONT_BODY, bg=COLOR_CARD_BG, width=15,
                 anchor="w").pack(side="left")
        self._km_var = tk.StringVar()
        tk.Entry(row1, textvariable=self._km_var, width=15, font=FONT_BODY).pack(side="left")
        self._last_km_label = tk.Label(row1, text="", font=("Segoe UI", 9),
                                       fg="#7F8C8D", bg=COLOR_CARD_BG)
        self._last_km_label.pack(side="left", padx=(10, 0))

        # Update last km display when vehicle changes
        self._vehicle_var.trace_add("write", self._update_last_km_display)

        # Date
        row2 = tk.Frame(form_frame, bg=COLOR_CARD_BG)
        row2.pack(fill="x", pady=3)
        tk.Label(row2, text="Fecha:", font=FONT_BODY, bg=COLOR_CARD_BG, width=15,
                 anchor="w").pack(side="left")
        self._date_var = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        tk.Entry(row2, textvariable=self._date_var, width=15, font=FONT_BODY).pack(side="left")
        tk.Label(row2, text="(DD/MM/AAAA)", font=("Segoe UI", 8),
                 fg="#7F8C8D", bg=COLOR_CARD_BG).pack(side="left", padx=5)

        # Recorded by
        row3 = tk.Frame(form_frame, bg=COLOR_CARD_BG)
        row3.pack(fill="x", pady=3)
        tk.Label(row3, text="Registrado por:", font=FONT_BODY, bg=COLOR_CARD_BG, width=15,
                 anchor="w").pack(side="left")
        self._recorded_by_var = tk.StringVar()
        tk.Entry(row3, textvariable=self._recorded_by_var, width=25, font=FONT_BODY).pack(side="left")

        # Notes
        row4 = tk.Frame(form_frame, bg=COLOR_CARD_BG)
        row4.pack(fill="x", pady=3)
        tk.Label(row4, text="Notas:", font=FONT_BODY, bg=COLOR_CARD_BG, width=15,
                 anchor="w").pack(side="left")
        self._notes_var = tk.StringVar()
        tk.Entry(row4, textvariable=self._notes_var, width=40, font=FONT_BODY).pack(side="left")

        # Submit button
        btn_frame = tk.Frame(form_frame, bg=COLOR_CARD_BG)
        btn_frame.pack(fill="x", pady=(10, 0))
        ttk.Button(btn_frame, text="Guardar registro", command=self._save_record).pack(side="left")

        # History section
        tk.Label(
            self, text="Historial de registros", font=FONT_SUBTITLE,
            fg=COLOR_TEXT, bg=COLOR_BG, anchor="w",
        ).pack(fill="x", pady=(PADDING, 5))

        # Vehicle filter for history
        hist_filter = tk.Frame(self, bg=COLOR_BG)
        hist_filter.pack(fill="x", pady=(0, 5))
        tk.Label(hist_filter, text="Vehiculo:", font=FONT_BODY, bg=COLOR_BG).pack(side="left", padx=(0, 5))
        self._hist_vehicle_var = tk.StringVar(value="Todos")
        combo = ttk.Combobox(hist_filter, textvariable=self._hist_vehicle_var, state="readonly",
                     values=["Todos"] + VEHICLES, width=25)
        combo.pack(side="left")
        combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_history())

        self._history_table = ScrollableTreeview(self, columns=HISTORY_COLUMNS)
        self._history_table.pack(fill="both", expand=True)

    def _update_last_km_display(self, *args):
        records = _load_mileage()
        vehicle = self._vehicle_var.get()
        last_km = _get_last_km(records, vehicle)
        if last_km > 0:
            self._last_km_label.config(text=f"(Ultimo: {last_km:,} km)")
        else:
            self._last_km_label.config(text="(Sin registros previos)")

    def _save_record(self):
        vehicle = self._vehicle_var.get()
        km_str = self._km_var.get().strip()
        date_str = self._date_var.get().strip()
        recorded_by = self._recorded_by_var.get().strip()

        # Validate
        if not km_str:
            messagebox.showwarning("Campo requerido", "Ingrese el kilometraje.")
            return
        try:
            km = int(km_str.replace(".", "").replace(",", ""))
        except ValueError:
            messagebox.showerror("Error", "El kilometraje debe ser un numero entero.")
            return

        if not recorded_by:
            messagebox.showwarning("Campo requerido", "Ingrese quien registra el dato.")
            return

        try:
            date_obj = datetime.strptime(date_str, "%d/%m/%Y")
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha invalido. Use DD/MM/AAAA.")
            return

        # Validate km >= last
        records = _load_mileage()
        last_km = _get_last_km(records, vehicle)
        if km < last_km:
            messagebox.showerror(
                "Error",
                f"El kilometraje ({km:,}) no puede ser menor al ultimo registro ({last_km:,}).")
            return

        # Save
        record = {
            "vehiculo": vehicle,
            "km": km,
            "fecha": date_obj.strftime("%Y-%m-%d"),
            "registrado_por": recorded_by,
            "notas": self._notes_var.get().strip(),
        }
        records.append(record)
        _save_mileage(records)

        # Clear form
        self._km_var.set("")
        self._notes_var.set("")
        self._update_last_km_display()

        messagebox.showinfo("Guardado", f"Registro guardado: {vehicle} - {km:,} km")
        self._refresh_history()

    def _refresh_history(self):
        self._history_table.clear()
        records = _load_mileage()
        vehicle_filter = self._hist_vehicle_var.get()

        # Sort by date descending
        records.sort(key=lambda r: r.get("fecha", ""), reverse=True)

        for r in records:
            if vehicle_filter != "Todos" and r.get("vehiculo") != vehicle_filter:
                continue
            try:
                date_display = datetime.strptime(r["fecha"], "%Y-%m-%d").strftime("%d/%m/%Y")
            except (KeyError, ValueError):
                date_display = r.get("fecha", "")

            self._history_table.insert_row((
                r.get("vehiculo", ""),
                f"{r.get('km', 0):,}",
                date_display,
                r.get("registrado_por", ""),
                r.get("notas", ""),
            ))

    def refresh(self):
        self._update_last_km_display()
        self._refresh_history()
