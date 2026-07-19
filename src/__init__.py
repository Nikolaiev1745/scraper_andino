"""
scraper_andino - Monitoreo de Minería Argentina

Paquete principal del scraper de noticias sobre minería en Argentina.
"""

__version__ = "2.0.0"
__author__ = "Nikolaiev1745"
__license__ = "MIT"

from .config import Config
from .scoring import ScoringEngine
from .sheets_client import SheetsClient
from .scraper import GoogleNewsScraper
from .utils import limpiar_texto

__all__ = [
    "Config",
    "ScoringEngine",
    "SheetsClient",
    "GoogleNewsScraper",
    "limpiar_texto",
]
