"""
Punto de entrada principal del Scraper Andino.

Uso:
    python main.py

Variables de entorno:
    SCRAPER_LOG_LEVEL: Nivel de logging (DEBUG, INFO, WARNING, ERROR). Default: INFO
"""

import logging
import os
import sys

# Agregar src/ al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.config import Config
from src.scoring import ScoringEngine
from src.scraper import GoogleNewsScraper
from src.sheets_client import SheetsClient


def setup_logging() -> None:
    """Configura el logging estructurado."""
    nivel = os.environ.get("SCRAPER_LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, nivel, logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main() -> None:
    """Orquesta el pipeline completo: scrape → score → save."""
    setup_logging()
    logger = logging.getLogger("scraper_andino.main")

    logger.info("═" * 50)
    logger.info("Iniciando Scraper Andino v2.0.0")
    logger.info("═" * 50)

    config = Config()
    scoring = ScoringEngine(config)
    scraper = GoogleNewsScraper(config, scoring)

    try:
        noticias = scraper.scrapear()
        sheets = SheetsClient(config)
        sheets.guardar_noticias(noticias)
        logger.info("✓ Proceso completado exitosamente")
    except Exception as e:
        logger.critical("Error fatal en el pipeline: %s", e, exc_info=True)
        raise


if __name__ == "__main__":
    main()
