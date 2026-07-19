"""
Tests para el scraper de Google News.
"""

from datetime import datetime, timezone, timedelta
from unittest.mock import Mock

import pytest

from src.config import Config
from src.scoring import ScoringEngine
from src.scraper import GoogleNewsScraper


@pytest.fixture
def config_minima():
    return Config(
        semillas_positivas=("proyecto de cobre", "mina a cielo abierto"),
        terminos_vagos=("minería", "crecimiento"),
        glosario_tecnico=("cobre", "oro", "litio"),
        terminos_negativos=("robo de cables", "delincuentes"),
        medios_andinos=("diario de cuyo", "el tribuno"),
        provincias=("San Juan",),
    )


@pytest.fixture
def scraper(config_minima):
    scoring = ScoringEngine(config_minima)
    return GoogleNewsScraper(config_minima, scoring)


class TestGoogleNewsScraper:
    """Tests para el scraper."""

    def test_procesar_entry_fecha_vieja(self, scraper):
        """Entradas con fecha > 1 año deben ser descartadas."""
        ahora = datetime.now(timezone.utc)
        limite_3m = ahora - timedelta(days=90)
        limite_1y = ahora - timedelta(days=365)

        entry = Mock()
        entry.published = "Mon, 01 Jan 2020 00:00:00 GMT"
        entry.title = "Titulo - Medio"
        entry.link = "http://example.com/1"
        entry.summary = "Resumen"
        entry.author = ""
        entry.authors = []

        resultado = scraper._procesar_entry(entry, ahora, limite_3m, limite_1y, set())
        assert resultado is None

    def test_procesar_entry_url_duplicada(self, scraper):
        """URLs ya vistas deben ser descartadas."""
        ahora = datetime.now(timezone.utc)
        limite_3m = ahora - timedelta(days=90)
        limite_1y = ahora - timedelta(days=365)

        entry = Mock()
        entry.published = ahora.strftime("%a, %d %b %Y %H:%M:%S GMT")
        entry.title = "Titulo - Medio"
        entry.link = "http://example.com/1"
        entry.summary = "Resumen"
        entry.author = ""
        entry.authors = []

        urls_vistas = {"http://example.com/1"}
        resultado = scraper._procesar_entry(entry, ahora, limite_3m, limite_1y, urls_vistas)
        assert resultado is None

    def test_procesar_entry_score_cero(self, scraper):
        """Noticias con score 0 deben ser descartadas."""
        ahora = datetime.now(timezone.utc)
        limite_3m = ahora - timedelta(days=90)
        limite_1y = ahora - timedelta(days=365)

        entry = Mock()
        entry.published = ahora.strftime("%a, %d %b %Y %H:%M:%S GMT")
        entry.title = "robo de cables - Medio"
        entry.link = "http://example.com/1"
        entry.summary = "detenidos por robo"
        entry.author = ""
        entry.authors = []
        entry.get = Mock(return_value="detenidos por robo")

        resultado = scraper._procesar_entry(entry, ahora, limite_3m, limite_1y, set())
        assert resultado is None

    def test_procesar_entry_noticia_valida(self, scraper):
        """Una noticia válida debe retornar un dict con todos los campos."""
        ahora = datetime.now(timezone.utc)
        limite_3m = ahora - timedelta(days=90)
        limite_1y = ahora - timedelta(days=365)

        entry = Mock()
        entry.published = ahora.strftime("%a, %d %b %Y %H:%M:%S GMT")
        entry.title = "Proyecto de cobre en San Juan - Diario de Cuyo"
        entry.link = "http://example.com/nueva"
        entry.summary = "Avanza el proyecto de extracción"
        entry.author = "Juan Pérez"
        entry.authors = [{"name": "Juan Pérez"}]
        entry.get = Mock(return_value="Avanza el proyecto de extracción")

        resultado = scraper._procesar_entry(entry, ahora, limite_3m, limite_1y, set())
        assert resultado is not None
        assert resultado["titulo"] == "Proyecto de cobre en San Juan"
        assert resultado["medio"] == "Diario de Cuyo"
        assert resultado["autor"] == "Juan Pérez"
        assert resultado["url"] == "http://example.com/nueva"
        assert "score" in resultado
        assert 1.0 <= resultado["score"] <= 100.0

    def test_procesar_entry_autor_fallback(self, scraper):
        """Si no hay autor, debe usar el fallback."""
        ahora = datetime.now(timezone.utc)
        limite_3m = ahora - timedelta(days=90)
        limite_1y = ahora - timedelta(days=365)

        entry = Mock()
        entry.published = ahora.strftime("%a, %d %b %Y %H:%M:%S GMT")
        entry.title = "Proyecto de cobre - El Tribuno"
        entry.link = "http://example.com/2"
        entry.summary = "Resumen"
        entry.author = ""
        entry.authors = []
        entry.get = Mock(return_value="Resumen")

        resultado = scraper._procesar_entry(entry, ahora, limite_3m, limite_1y, set())
        assert resultado["autor"] == "Redacción de El Tribuno"
