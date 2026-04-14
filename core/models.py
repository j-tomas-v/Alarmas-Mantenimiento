from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class EstadoUrgencia(Enum):
    VENCIDO = "Vencido"
    PROXIMO = "Proximo"
    PROGRAMADO = "Programado"
    COMPLETADO = "Completado"


class Prioridad(Enum):
    ALTA = "Alta"
    MEDIA = "Media"
    BAJA = "Baja"
    NINGUNA = "Sin prioridad"


@dataclass
class PampoEntry:
    id_pampo: int
    maquina: str
    actividad: str


@dataclass
class OrdenMantenimiento:
    n_om: int
    fecha: Optional[datetime]
    preventivo: bool
    correctivo: bool
    prioridad: Prioridad
    solicita: str
    realizar_el_dia: Optional[datetime]
    con_parada: bool
    id_pampo: int
    finalizado: bool
    fecha_realizacion: Optional[datetime]
    personal: list[str] = field(default_factory=list)
    observaciones: str = ""
    # Campos desde PAMPO (join)
    maquina: str = ""
    actividad: str = ""
    # Campos calculados por urgency engine
    estado: EstadoUrgencia = EstadoUrgencia.PROGRAMADO
    fecha_limite: Optional[datetime] = None
    dias_restantes: int = 0
    severidad: float = 0.0


@dataclass
class Alert:
    tipo: str
    display_name: str
    orden: Optional[OrdenMantenimiento]
    mensaje: str
    severidad: float
    destinatarios: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MileageRecord:
    vehiculo: str
    km: int
    fecha: str  # ISO format string for JSON serialization
    registrado_por: str
    notas: str = ""
