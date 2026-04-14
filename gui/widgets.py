"""Reusable tkinter widgets."""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Union

from gui.styles import (
    COLOR_CARD_BG, COLOR_TEXT, COLOR_TEXT_SECONDARY,
    FONT_CARD_LABEL, FONT_CARD_NUMBER, PADDING,
)


class StatusCard(tk.Frame):
    """A summary card showing a number and label with a colored accent."""

    def __init__(self, parent, label: str, value: Union[int, str], color: str, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(bg=COLOR_CARD_BG, relief="solid", bd=1, padx=PADDING, pady=PADDING)

        # Color accent bar on left
        accent = tk.Frame(self, bg=color, width=4)
        accent.pack(side="left", fill="y", padx=(0, 8))

        content = tk.Frame(self, bg=COLOR_CARD_BG)
        content.pack(side="left", fill="both", expand=True)

        self.value_label = tk.Label(
            content, text=str(value), font=FONT_CARD_NUMBER,
            fg=color, bg=COLOR_CARD_BG, anchor="w",
        )
        self.value_label.pack(anchor="w")

        self.text_label = tk.Label(
            content, text=label, font=FONT_CARD_LABEL,
            fg=COLOR_TEXT_SECONDARY, bg=COLOR_CARD_BG, anchor="w",
        )
        self.text_label.pack(anchor="w")

    def update_value(self, value: Union[int, str], color: Optional[str] = None):
        self.value_label.config(text=str(value))
        if color:
            self.value_label.config(fg=color)


class ScrollableTreeview(tk.Frame):
    """A Treeview with vertical and horizontal scrollbars."""

    def __init__(self, parent, columns: list[tuple[str, str, int]], **kwargs):
        super().__init__(parent, **kwargs)

        # Scrollbars
        vsb = ttk.Scrollbar(self, orient="vertical")
        hsb = ttk.Scrollbar(self, orient="horizontal")

        col_ids = [c[0] for c in columns]
        self.tree = ttk.Treeview(
            self, columns=col_ids, show="headings",
            yscrollcommand=vsb.set, xscrollcommand=hsb.set,
        )
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)

        # Configure columns
        for col_id, heading, width in columns:
            self.tree.heading(col_id, text=heading, anchor="w")
            self.tree.column(col_id, width=width, minwidth=50, anchor="w")

        # Configure row tags for urgency colors
        self.tree.tag_configure("vencido", background="#FADBD8")
        self.tree.tag_configure("proximo", background="#FEF5E7")
        self.tree.tag_configure("programado", background="#E8F8F5")
        self.tree.tag_configure("completado", background="#F2F3F4")

        # Layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def clear(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def insert_row(self, values: tuple, tag: str = ""):
        self.tree.insert("", "end", values=values, tags=(tag,))
