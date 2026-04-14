"""Main application window with sidebar navigation."""

import tkinter as tk
from tkinter import ttk

from gui.styles import (
    COLOR_BG, COLOR_SIDEBAR, COLOR_SIDEBAR_ACTIVE, COLOR_SIDEBAR_HOVER,
    COLOR_SIDEBAR_TEXT, COLOR_TEXT_SECONDARY, FONT_SIDEBAR, FONT_SIDEBAR_TITLE,
    FONT_SMALL, PADDING, SIDEBAR_WIDTH,
)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Alarmas de Mantenimiento - ATT")
        self.geometry("1200x700")
        self.minsize(900, 500)
        self.configure(bg=COLOR_BG)

        # State
        self._views = {}
        self._nav_buttons = {}
        self._active_view = None
        self._status_var = tk.StringVar(value="Sin conexion a base de datos")
        self._alerts_count_var = tk.StringVar(value="Alertas: 0")

        self._build_ui()

    def _build_ui(self):
        # Sidebar
        self.sidebar = tk.Frame(self, bg=COLOR_SIDEBAR, width=SIDEBAR_WIDTH)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Sidebar title
        title_frame = tk.Frame(self.sidebar, bg=COLOR_SIDEBAR, pady=15)
        title_frame.pack(fill="x")
        tk.Label(
            title_frame, text="ATT", font=FONT_SIDEBAR_TITLE,
            fg=COLOR_SIDEBAR_TEXT, bg=COLOR_SIDEBAR,
        ).pack()
        tk.Label(
            title_frame, text="Mantenimiento", font=FONT_SMALL,
            fg=COLOR_TEXT_SECONDARY, bg=COLOR_SIDEBAR,
        ).pack()

        ttk.Separator(self.sidebar, orient="horizontal").pack(fill="x", padx=10)

        # Navigation buttons container
        self._nav_frame = tk.Frame(self.sidebar, bg=COLOR_SIDEBAR)
        self._nav_frame.pack(fill="x", pady=(10, 0))

        # Content area
        self.content = tk.Frame(self, bg=COLOR_BG)
        self.content.pack(side="left", fill="both", expand=True)

        # Status bar
        status_bar = tk.Frame(self, bg="#ECF0F1", height=25)
        status_bar.pack(side="bottom", fill="x")
        status_bar.pack_propagate(False)

        tk.Label(
            status_bar, textvariable=self._status_var,
            font=FONT_SMALL, fg=COLOR_TEXT_SECONDARY, bg="#ECF0F1",
            anchor="w", padx=10,
        ).pack(side="left")

        tk.Label(
            status_bar, textvariable=self._alerts_count_var,
            font=FONT_SMALL, fg=COLOR_TEXT_SECONDARY, bg="#ECF0F1",
            anchor="e", padx=10,
        ).pack(side="right")

    def add_view(self, name: str, label: str, view_class, **kwargs):
        """Register a view with the sidebar navigation."""
        # Create nav button
        btn = tk.Label(
            self._nav_frame, text=f"  {label}", font=FONT_SIDEBAR,
            fg=COLOR_SIDEBAR_TEXT, bg=COLOR_SIDEBAR,
            anchor="w", padx=15, pady=8, cursor="hand2",
        )
        btn.pack(fill="x")
        btn.bind("<Button-1>", lambda e, n=name: self.show_view(n))
        btn.bind("<Enter>", lambda e, b=btn, n=name: self._on_hover(b, n, True))
        btn.bind("<Leave>", lambda e, b=btn, n=name: self._on_hover(b, n, False))
        self._nav_buttons[name] = btn

        # Create view frame (lazy - not populated yet)
        frame = view_class(self.content, **kwargs)
        self._views[name] = frame

    def show_view(self, name: str):
        """Switch to the specified view."""
        if self._active_view == name:
            return

        # Hide current view
        for view in self._views.values():
            view.pack_forget()

        # Show requested view
        if name in self._views:
            self._views[name].pack(fill="both", expand=True, padx=PADDING, pady=PADDING)
            self._active_view = name

            # Update nav button highlighting
            for btn_name, btn in self._nav_buttons.items():
                if btn_name == name:
                    btn.configure(bg=COLOR_SIDEBAR_ACTIVE)
                else:
                    btn.configure(bg=COLOR_SIDEBAR)

            # Call refresh if the view has one
            view = self._views[name]
            if hasattr(view, "refresh"):
                view.refresh()

    def _on_hover(self, btn: tk.Label, name: str, entering: bool):
        if name == self._active_view:
            return
        btn.configure(bg=COLOR_SIDEBAR_HOVER if entering else COLOR_SIDEBAR)

    def set_status(self, text: str):
        self._status_var.set(text)

    def set_alerts_count(self, count: int):
        self._alerts_count_var.set(f"Alertas activas: {count}")

    def get_view(self, name: str):
        return self._views.get(name)
