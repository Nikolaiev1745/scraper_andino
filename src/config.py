"""
Configuración del scraper.

Toda la configuración centralizada en un solo lugar.
Puede cargarse desde archivos externos (JSON/YAML) en el futuro.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Tuple


@dataclass(frozen=True)
class Config:
    """Configuración inmutable del scraper."""

    # ─── Rutas ─────────────────────────────────────────────────────
    ruta_creds: Path = field(
        default_factory=lambda: Path(__file__).parent.parent / "config" / "creds.json"
    )
    nombre_documento: str = "Monitoreo Mineria Argentina"

    # ─── Umbrales ──────────────────────────────────────────────────
    umbral_score_viejas: float = 75.0
    dias_recientes: int = 90
    dias_maximo: int = 365

    # ─── Resiliencia ───────────────────────────────────────────────
    max_retries: int = 3
    backoff_base: float = 2.0          # segundos
    delay_entre_requests: float = 1.5  # segundos entre provincias

    # ─── Semillas positivas (alta relevancia) ──────────────────────
    semillas_positivas: Tuple[str, ...] = (
        "extracción de oro", "proyecto de cobre", "lixiviación con cianuro",
        "mina a cielo abierto", "reservas de mineral", "ley de mineral",
        "concesión minera", "planta de procesamiento", "relave",
        "impacto ambiental", "conflicto socioambiental", "declaración de impacto ambiental",
        "exploración avanzada", "Pascua Lama", "Veladero", "Josemaría", "Los Azules",
        "El Pachón", "Gualcamayo", "Barrick", "Yamana", "McEwen Mining",
        "glaciar", "ley de glaciares", "Mike Mending", "Lundin Mining", "BHP",
        "filo del sol", "José Luis Morea", "Pablo Perea",
        "ley 7722", "ley 5001", "ley XVII 68", "ley 10608", "ley 8229", "ley 7070",
        "ley 5128", "ley 5772", "decreto 5772", "ley 3753", "fideicomiso UNIR",
        "asamblea de vecinos", "no a la mina", "corte de ruta", "recurso de amparo",
        "cuenca hidrica", "estudio hidrogeologico", "Fenix", "Salar de Hombre Muerto",
        "Cauchari-Olaroz", "Tres Quebradas", "Kachi", "Salar de Diablillos",
        "Proyecto MARA", "Agua Rica", "Bajo de la Alumbrera", "Taca Taca", "Altar",
        "San Jorge", "COFEMIN", "CAEM"
    )

    # ─── Términos vagos (baja relevancia) ──────────────────────────
    terminos_vagos: Tuple[str, ...] = (
        "minería", "actividad minera", "desarrollo minero", "crecimiento",
        "producción minera", "sector minero", "provincia de San Juan",
        "potencial minero", "trabajo minero", "inversión", "progreso",
        "industria minera", "la minería es", "motor de la economía",
        "récord", "orgullo sanjuanino", "futuro promisorio", "lidera", "polo minero"
    )

    # ─── Glosario técnico ──────────────────────────────────────────
    glosario_tecnico: Tuple[str, ...] = (
        "cobre", "oro", "plata", "molibdeno", "uranio", "litio", "tierras raras",
        "lixiviación", "relave", "cielo abierto", "subterránea", "ley de mineral",
        "reservas", "recurso", "prefactibilidad", "factibilidad", "producción",
        "extracción", "procesamiento", "fundición", "refinación",
        "línea de 500 kv", "campamento", "planta", "concentradora", "ducto",
        "impacto ambiental", "dia", "declaración de impacto", "glaciar",
        "ley de glaciares", "consulta previa", "licencia social",
        "veladero", "josemaría", "los azules", "pachón", "gualcamayo",
        "hualilán", "calcatreu", "vicuña", "barrick", "glencore", "finning",
        "caterpillar", "patagonia gold", "challenger", "mcewen",
        "regalías", "inversión", "capex", "opex", "onzas",
        "rigi", "proveedor minero", "evaluacion de impacto ambiental", "eia",
        "policia minera", "regalias mineras", "fideicomiso minero", "seguridad juridica",
        "comunidades originarias", "consulta previa", "asamblea legislativa"
    )

    # ─── Términos negativos (descartar) ────────────────────────────
    terminos_negativos: Tuple[str, ...] = (
        "robo de cables", "cables de cobre", "delincuentes", "allanamiento",
        "detenido", "tendido electrico", "clandestino", "mercado negro",
        "robado", "sustraccion de cables", "detenidos", "policial"
    )

    # ─── Medios andinos (bono +15) ─────────────────────────────────
    medios_andinos: Tuple[str, ...] = (
        "diario de cuyo", "el pregon", "el ancasti", "mining press", "pregon minero",
        "jujuy al momento", "el tribuno", "mdz online", "mdz", "diario huarpe", "huarpe",
        "san juan 8", "canal 13 san juan", "tiempo de san juan", "la arena", "el chubut",
        "la opinion austral", "nuevo dia", "el zonda"
    )

    # ─── Provincias a monitorear ───────────────────────────────────
    provincias: Tuple[str, ...] = (
        "San Juan", "Mendoza", "Catamarca", "Salta", "Jujuy",
        "La Rioja", "Santa Cruz", "Chubut", "Neuquen"
    )
