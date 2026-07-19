"""
Tests para la configuración.
"""

import pytest
from src.config import Config


class TestConfig:
    """Tests para la configuración."""

    def test_config_inmutable(self):
        """Las dataclasses frozen deben ser inmutables."""
        config = Config()
        with pytest.raises(AttributeError):
            config.umbral_score_viejas = 50.0

    def test_valores_por_defecto(self):
        config = Config()
        assert config.umbral_score_viejas == 75.0
        assert config.dias_recientes == 90
        assert config.dias_maximo == 365
        assert config.max_retries == 3
        assert config.backoff_base == 2.0

    def test_provincias_no_vacias(self):
        config = Config()
        assert len(config.provincias) > 0
        assert all(isinstance(p, str) for p in config.provincias)

    def test_glosario_no_vacio(self):
        config = Config()
        assert len(config.glosario_tecnico) > 0
        assert len(config.terminos_negativos) > 0
