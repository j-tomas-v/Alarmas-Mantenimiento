import configparser
import logging
import os
from datetime import datetime
from typing import Optional

import pyodbc

from core.models import OrdenMantenimiento, PampoEntry, Prioridad

logger = logging.getLogger(__name__)

PLACEHOLDER_DATE = datetime(1999, 12, 30)

DRIVER_NAME = "Microsoft Access Driver (*.mdb, *.accdb)"


def _clean_date(value: Optional[datetime]) -> Optional[datetime]:
    """Return None for placeholder dates (1999-12-30) or actual None."""
    if value is None:
        return None
    if isinstance(value, datetime) and value.year == 1999:
        return None
    return value


def _parse_priority(alta: bool, media: bool, baja: bool) -> Prioridad:
    if alta:
        return Prioridad.ALTA
    if media:
        return Prioridad.MEDIA
    if baja:
        return Prioridad.BAJA
    return Prioridad.NINGUNA


def check_driver_installed() -> bool:
    """Check if the Microsoft Access ODBC driver is available."""
    try:
        drivers = pyodbc.drivers()
        return DRIVER_NAME in drivers
    except Exception:
        return False


def get_connection_string(db_path: str) -> str:
    return (
        f"DRIVER={{{DRIVER_NAME}}};"
        f"DBQ={db_path};"
        f"ReadOnly=1;"
    )


def get_all_pampo(db_path: str) -> list[PampoEntry]:
    """Get all PAMPO entries."""
    conn_str = get_connection_string(db_path)
    entries = []
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT [ID_PAMPO], [Máquina], [Actividad] FROM [PAMPO]"
        )
        for row in cursor.fetchall():
            entries.append(PampoEntry(
                id_pampo=int(row[0]),
                maquina=row[1] or "",
                actividad=row[2] or "",
            ))
        conn.close()
    except Exception as e:
        logger.error("Error reading PAMPO table: %s", e)
    return entries


def get_pending_orders(db_path: str, year_from: int = 2025) -> list[OrdenMantenimiento]:
    """Get all non-completed orders from year_from onwards, joined with PAMPO."""
    conn_str = get_connection_string(db_path)
    orders = []
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        query = (
            "SELECT "
            "  o.[N°OM], o.[Fecha], o.[Preventivo], o.[Correctivo], "
            "  o.[Alta], o.[Media], o.[Baja], o.[Solicita], "
            "  o.[Realizar el día], o.[¿Con parada de producción?], "
            "  o.[ID PAMPO], o.[¿Finalizado?], o.[Fecha realización], "
            "  o.[PM1], o.[PM2], o.[PM3], "
            "  o.[Cusa falla/Observaciones], "
            "  p.[Máquina], p.[Actividad] "
            "FROM [Base Orden Mantenimiento] AS o "
            "LEFT JOIN [PAMPO] AS p ON o.[ID PAMPO] = p.[ID_PAMPO] "
            "WHERE o.[Fecha] >= ? "
            "ORDER BY o.[Fecha] DESC"
        )
        start_date = datetime(year_from, 1, 1)
        cursor.execute(query, start_date)

        for row in cursor.fetchall():
            personal = [p for p in [row[13], row[14], row[15]] if p]
            orden = OrdenMantenimiento(
                n_om=row[0],
                fecha=_clean_date(row[1]),
                preventivo=bool(row[2]),
                correctivo=bool(row[3]),
                prioridad=_parse_priority(bool(row[4]), bool(row[5]), bool(row[6])),
                solicita=row[7] or "",
                realizar_el_dia=_clean_date(row[8]),
                con_parada=bool(row[9]),
                id_pampo=int(row[10]) if row[10] else 0,
                finalizado=bool(row[11]),
                fecha_realizacion=_clean_date(row[12]),
                personal=personal,
                observaciones=row[16] or "",
                maquina=row[17] or f"PAMPO #{row[10]}",
                actividad=row[18] or "",
            )
            orders.append(orden)
        conn.close()
    except Exception as e:
        logger.error("Error reading orders: %s", e)
    return orders


def get_all_orders(db_path: str, year_from: int = 2025) -> list[OrdenMantenimiento]:
    """Get ALL orders (completed and pending) from year_from onwards."""
    conn_str = get_connection_string(db_path)
    orders = []
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        query = (
            "SELECT "
            "  o.[N°OM], o.[Fecha], o.[Preventivo], o.[Correctivo], "
            "  o.[Alta], o.[Media], o.[Baja], o.[Solicita], "
            "  o.[Realizar el día], o.[¿Con parada de producción?], "
            "  o.[ID PAMPO], o.[¿Finalizado?], o.[Fecha realización], "
            "  o.[PM1], o.[PM2], o.[PM3], "
            "  o.[Cusa falla/Observaciones], "
            "  p.[Máquina], p.[Actividad] "
            "FROM [Base Orden Mantenimiento] AS o "
            "LEFT JOIN [PAMPO] AS p ON o.[ID PAMPO] = p.[ID_PAMPO] "
            "WHERE o.[Fecha] >= ? "
            "ORDER BY o.[Fecha] DESC"
        )
        start_date = datetime(year_from, 1, 1)
        cursor.execute(query, start_date)

        for row in cursor.fetchall():
            personal = [p for p in [row[13], row[14], row[15]] if p]
            orden = OrdenMantenimiento(
                n_om=row[0],
                fecha=_clean_date(row[1]),
                preventivo=bool(row[2]),
                correctivo=bool(row[3]),
                prioridad=_parse_priority(bool(row[4]), bool(row[5]), bool(row[6])),
                solicita=row[7] or "",
                realizar_el_dia=_clean_date(row[8]),
                con_parada=bool(row[9]),
                id_pampo=int(row[10]) if row[10] else 0,
                finalizado=bool(row[11]),
                fecha_realizacion=_clean_date(row[12]),
                personal=personal,
                observaciones=row[16] or "",
                maquina=row[17] or f"PAMPO #{row[10]}",
                actividad=row[18] or "",
            )
            orders.append(orden)
        conn.close()
    except Exception as e:
        logger.error("Error reading orders: %s", e)
    return orders


def load_config(config_path: str = "config.ini") -> configparser.ConfigParser:
    """Load application configuration."""
    config = configparser.ConfigParser()
    if os.path.exists(config_path):
        config.read(config_path, encoding="utf-8")
    return config
