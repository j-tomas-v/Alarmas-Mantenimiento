"""Settings view for SMTP config, PAMPO frequencies, and alert thresholds."""

import configparser
import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from core.email_service import test_smtp_connection
from gui.styles import COLOR_BG, COLOR_CARD_BG, COLOR_TEXT, FONT_BODY, FONT_SUBTITLE, FONT_TITLE, PADDING

PAMPO_FREQ_PATH = "data/pampo_frequencies.json"
CONFIG_PATH = "config.ini"


class SettingsView(tk.Frame):
    """Configuration panel for SMTP, database, frequencies, and alert settings."""

    def __init__(self, parent, app_controller=None, **kwargs):
        super().__init__(parent, bg=COLOR_BG, **kwargs)
        self._controller = app_controller
        self._build_ui()

    def _build_ui(self):
        # Scrollable container
        canvas = tk.Canvas(self, bg=COLOR_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self._scroll_frame = tk.Frame(canvas, bg=COLOR_BG)

        self._scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self._scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        parent = self._scroll_frame

        # Title
        tk.Label(parent, text="Configuracion", font=FONT_TITLE,
                 fg=COLOR_TEXT, bg=COLOR_BG, anchor="w").pack(fill="x", pady=(0, PADDING))

        # === Database Section ===
        db_frame = tk.LabelFrame(parent, text="Base de Datos", font=FONT_SUBTITLE,
                                 bg=COLOR_CARD_BG, padx=15, pady=10)
        db_frame.pack(fill="x", pady=(0, PADDING))

        row = tk.Frame(db_frame, bg=COLOR_CARD_BG)
        row.pack(fill="x", pady=3)
        tk.Label(row, text="Ruta archivo .accdb:", font=FONT_BODY, bg=COLOR_CARD_BG,
                 width=20, anchor="w").pack(side="left")
        self._db_path_var = tk.StringVar()
        tk.Entry(row, textvariable=self._db_path_var, width=50, font=FONT_BODY).pack(side="left")
        ttk.Button(row, text="Buscar...", command=self._browse_db).pack(side="left", padx=5)

        row2 = tk.Frame(db_frame, bg=COLOR_CARD_BG)
        row2.pack(fill="x", pady=3)
        tk.Label(row2, text="Filtrar desde ano:", font=FONT_BODY, bg=COLOR_CARD_BG,
                 width=20, anchor="w").pack(side="left")
        self._year_var = tk.StringVar(value="2025")
        tk.Entry(row2, textvariable=self._year_var, width=8, font=FONT_BODY).pack(side="left")

        # === SMTP Section ===
        smtp_frame = tk.LabelFrame(parent, text="Servidor SMTP", font=FONT_SUBTITLE,
                                   bg=COLOR_CARD_BG, padx=15, pady=10)
        smtp_frame.pack(fill="x", pady=(0, PADDING))

        self._smtp_vars = {}
        smtp_fields = [
            ("server", "Servidor:", 30),
            ("port", "Puerto:", 8),
            ("username", "Usuario:", 30),
            ("password", "Contrasena:", 30),
            ("from_name", "Nombre remitente:", 30),
        ]
        for key, label, width in smtp_fields:
            row = tk.Frame(smtp_frame, bg=COLOR_CARD_BG)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=label, font=FONT_BODY, bg=COLOR_CARD_BG,
                     width=20, anchor="w").pack(side="left")
            var = tk.StringVar()
            show = "*" if key == "password" else None
            tk.Entry(row, textvariable=var, width=width, font=FONT_BODY,
                     show=show).pack(side="left")
            self._smtp_vars[key] = var

        tls_row = tk.Frame(smtp_frame, bg=COLOR_CARD_BG)
        tls_row.pack(fill="x", pady=2)
        tk.Label(tls_row, text="Usar TLS:", font=FONT_BODY, bg=COLOR_CARD_BG,
                 width=20, anchor="w").pack(side="left")
        self._tls_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(tls_row, variable=self._tls_var).pack(side="left")

        smtp_btn_frame = tk.Frame(smtp_frame, bg=COLOR_CARD_BG)
        smtp_btn_frame.pack(fill="x", pady=(8, 0))
        ttk.Button(smtp_btn_frame, text="Probar conexion", command=self._test_smtp).pack(side="left")

        # === Recipients Section ===
        recip_frame = tk.LabelFrame(parent, text="Destinatarios de Email", font=FONT_SUBTITLE,
                                    bg=COLOR_CARD_BG, padx=15, pady=10)
        recip_frame.pack(fill="x", pady=(0, PADDING))

        self._recip_vars = {}
        recip_fields = [
            ("mantenimiento", "Equipo mantenimiento:"),
            ("gerencia", "Gerencia:"),
            ("conductores", "Conductores:"),
        ]
        for key, label in recip_fields:
            row = tk.Frame(recip_frame, bg=COLOR_CARD_BG)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=label, font=FONT_BODY, bg=COLOR_CARD_BG,
                     width=20, anchor="w").pack(side="left")
            var = tk.StringVar()
            tk.Entry(row, textvariable=var, width=50, font=FONT_BODY).pack(side="left")
            self._recip_vars[key] = var

        tk.Label(recip_frame, text="(Separar multiples emails con coma)",
                 font=("Segoe UI", 8), fg="#7F8C8D", bg=COLOR_CARD_BG).pack(anchor="w")

        # === Alert Settings ===
        alert_frame = tk.LabelFrame(parent, text="Parametros de Alertas", font=FONT_SUBTITLE,
                                    bg=COLOR_CARD_BG, padx=15, pady=10)
        alert_frame.pack(fill="x", pady=(0, PADDING))

        self._alert_vars = {}
        alert_fields = [
            ("intervalo_check_horas", "Intervalo verificacion (hs):", "4"),
            ("cooldown_dias", "Cooldown reenvio (dias):", "7"),
            ("dias_aviso_proximo", "Dias aviso proximo:", "7"),
            ("frecuencia_default_dias", "Frecuencia default (dias):", "30"),
        ]
        for key, label, default in alert_fields:
            row = tk.Frame(alert_frame, bg=COLOR_CARD_BG)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=label, font=FONT_BODY, bg=COLOR_CARD_BG,
                     width=28, anchor="w").pack(side="left")
            var = tk.StringVar(value=default)
            tk.Entry(row, textvariable=var, width=8, font=FONT_BODY).pack(side="left")
            self._alert_vars[key] = var

        # === PAMPO Frequencies ===
        freq_frame = tk.LabelFrame(parent, text="Frecuencias PAMPO (dias entre mantenimientos)",
                                   font=FONT_SUBTITLE, bg=COLOR_CARD_BG, padx=15, pady=10)
        freq_frame.pack(fill="x", pady=(0, PADDING))

        freq_btn_row = tk.Frame(freq_frame, bg=COLOR_CARD_BG)
        freq_btn_row.pack(fill="x", pady=(0, 5))
        ttk.Button(freq_btn_row, text="Cargar frecuencias", command=self._load_frequencies).pack(side="left", padx=3)
        ttk.Button(freq_btn_row, text="Guardar frecuencias", command=self._save_frequencies).pack(side="left", padx=3)

        # Frequencies table
        freq_cols = [
            ("id", "ID PAMPO", 70),
            ("desc", "Descripcion", 380),
            ("freq", "Frecuencia (dias)", 120),
        ]
        tree_frame = tk.Frame(freq_frame, bg=COLOR_CARD_BG)
        tree_frame.pack(fill="x")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        self._freq_tree = ttk.Treeview(
            tree_frame, columns=[c[0] for c in freq_cols], show="headings",
            height=10, yscrollcommand=vsb.set)
        vsb.config(command=self._freq_tree.yview)

        for col_id, heading, width in freq_cols:
            self._freq_tree.heading(col_id, text=heading)
            self._freq_tree.column(col_id, width=width)

        self._freq_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        tree_frame.grid_columnconfigure(0, weight=1)

        # Edit frequency inline
        edit_row = tk.Frame(freq_frame, bg=COLOR_CARD_BG)
        edit_row.pack(fill="x", pady=(5, 0))
        tk.Label(edit_row, text="ID PAMPO:", font=FONT_BODY, bg=COLOR_CARD_BG).pack(side="left", padx=(0, 3))
        self._edit_id_var = tk.StringVar()
        tk.Entry(edit_row, textvariable=self._edit_id_var, width=6, font=FONT_BODY).pack(side="left", padx=(0, 10))
        tk.Label(edit_row, text="Nueva frecuencia (dias):", font=FONT_BODY, bg=COLOR_CARD_BG).pack(side="left", padx=(0, 3))
        self._edit_freq_var = tk.StringVar()
        tk.Entry(edit_row, textvariable=self._edit_freq_var, width=6, font=FONT_BODY).pack(side="left", padx=(0, 10))
        ttk.Button(edit_row, text="Actualizar", command=self._update_frequency).pack(side="left")

        # Bind selection to fill edit fields
        self._freq_tree.bind("<<TreeviewSelect>>", self._on_freq_select)

        # === Save All Button ===
        ttk.Button(parent, text="Guardar toda la configuracion",
                   command=self._save_all).pack(pady=PADDING)

    def _browse_db(self):
        path = filedialog.askopenfilename(
            title="Seleccionar base de datos Access",
            filetypes=[("Access Database", "*.accdb *.mdb"), ("All files", "*.*")])
        if path:
            self._db_path_var.set(path)

    def _test_smtp(self):
        config = {
            "server": self._smtp_vars["server"].get(),
            "port": self._smtp_vars["port"].get(),
            "use_tls": "true" if self._tls_var.get() else "false",
            "username": self._smtp_vars["username"].get(),
            "password": self._smtp_vars["password"].get(),
        }
        success, message = test_smtp_connection(config)
        if success:
            messagebox.showinfo("Exito", message)
        else:
            messagebox.showerror("Error", message)

    def _load_frequencies(self):
        self._freq_tree.delete(*self._freq_tree.get_children())
        if not os.path.exists(PAMPO_FREQ_PATH):
            return
        try:
            with open(PAMPO_FREQ_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            for id_str, info in sorted(data.items(), key=lambda x: int(x[0])):
                self._freq_tree.insert("", "end", values=(
                    id_str, info.get("descripcion", ""), info.get("frecuencia_dias", 30)))
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando frecuencias: {e}")

    def _save_frequencies(self):
        data = {}
        for item in self._freq_tree.get_children():
            vals = self._freq_tree.item(item, "values")
            data[str(vals[0])] = {
                "descripcion": vals[1],
                "frecuencia_dias": int(vals[2]),
            }
        try:
            with open(PAMPO_FREQ_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Guardado", "Frecuencias PAMPO guardadas correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"Error guardando frecuencias: {e}")

    def _on_freq_select(self, event):
        selection = self._freq_tree.selection()
        if selection:
            vals = self._freq_tree.item(selection[0], "values")
            self._edit_id_var.set(vals[0])
            self._edit_freq_var.set(vals[2])

    def _update_frequency(self):
        target_id = self._edit_id_var.get().strip()
        new_freq = self._edit_freq_var.get().strip()
        if not target_id or not new_freq:
            return
        try:
            int(new_freq)
        except ValueError:
            messagebox.showerror("Error", "La frecuencia debe ser un numero.")
            return

        for item in self._freq_tree.get_children():
            vals = self._freq_tree.item(item, "values")
            if str(vals[0]) == target_id:
                self._freq_tree.item(item, values=(vals[0], vals[1], new_freq))
                break

    def _save_all(self):
        config = configparser.ConfigParser()

        config["database"] = {
            "path": self._db_path_var.get(),
            "year_from": self._year_var.get(),
        }

        config["smtp"] = {
            "server": self._smtp_vars["server"].get(),
            "port": self._smtp_vars["port"].get(),
            "use_tls": "true" if self._tls_var.get() else "false",
            "username": self._smtp_vars["username"].get(),
            "password": self._smtp_vars["password"].get(),
            "from_name": self._smtp_vars["from_name"].get(),
        }

        config["recipients"] = {k: v.get() for k, v in self._recip_vars.items()}
        config["alertas"] = {k: v.get() for k, v in self._alert_vars.items()}

        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                config.write(f)
            self._save_frequencies()
            messagebox.showinfo("Guardado", "Configuracion guardada correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"Error guardando configuracion: {e}")

    def load_from_config(self, config: configparser.ConfigParser):
        """Populate fields from a ConfigParser object."""
        if config.has_section("database"):
            self._db_path_var.set(config.get("database", "path", fallback=""))
            self._year_var.set(config.get("database", "year_from", fallback="2025"))

        if config.has_section("smtp"):
            for key, var in self._smtp_vars.items():
                var.set(config.get("smtp", key, fallback=""))
            self._tls_var.set(config.get("smtp", "use_tls", fallback="true").lower() == "true")

        if config.has_section("recipients"):
            for key, var in self._recip_vars.items():
                var.set(config.get("recipients", key, fallback=""))

        if config.has_section("alertas"):
            for key, var in self._alert_vars.items():
                var.set(config.get("alertas", key, fallback=""))

        self._load_frequencies()

    def refresh(self):
        pass
