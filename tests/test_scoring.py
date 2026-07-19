"""
Tests para el motor de scoring.
"""

import pytest
from src.config import Config
from src.scoring import ScoringEngine


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
def scoring(config_minima):
    return ScoringEngine(config_minima)


class TestScoringEngine:
    """Tests para el motor de scoring."""

    def test_score_cero_texto_vacio(self, scoring):
        assert scoring.calcular_score("", "Diario") == 0.0

    def test_score_descarta_terminos_negativos(self, scoring):
        """Una noticia con 'robo de cables' debe tener score 0."""
        texto = "Detenidos por robo de cables de cobre en la mina"
        assert scoring.calcular_score(texto, "Diario") == 0.0

    def test_score_bono_medio_andino(self, scoring):
        """Noticias de medios andinos reciben bono de +15."""
        texto = "Proyecto de cobre en San Juan avanza"
        score_andino = scoring.calcular_score(texto, "diario de cuyo")
        score_normal = scoring.calcular_score(texto, "clarin")
        assert score_andino >= score_normal
        if score_normal < 85:
            assert score_andino - score_normal >= 14.0

    def test_score_rango_valido(self, scoring):
        """El score siempre debe estar entre 1.0 y 100.0."""
        texto = "Proyecto de cobre y oro con lixiviación en mina a cielo abierto"
        score = scoring.calcular_score(texto, "Diario")
        assert 1.0 <= score <= 100.0

    def test_score_aumenta_con_densidad_tecnica(self, scoring):
        """Más términos técnicos = mayor score (hasta el cap)."""
        texto_basico = "minería en San Juan"
        texto_tecnico = "cobre oro litio lixiviación en mina a cielo abierto"
        score_basico = scoring.calcular_score(texto_basico, "Diario")
        score_tecnico = scoring.calcular_score(texto_tecnico, "Diario")
        assert score_tecnico >= score_basico

    def test_penalizacion_terminos_vagos(self, scoring):
        """Exceso de términos vagos reduce el score."""
        texto_vago = "minería crecimiento minería crecimiento minería crecimiento"
        texto_mixto = "minería proyecto de cobre crecimiento"
        score_vago = scoring.calcular_score(texto_vago, "Diario")
        score_mixto = scoring.calcular_score(texto_mixto, "Diario")
        assert score_vago < score_mixto or score_vago < 50

    def test_score_semantico_similaridad(self, scoring):
        """Textos similares a semillas positivas deben tener score alto."""
        texto_positivo = "proyecto de cobre en mina a cielo abierto"
        score = scoring.calcular_score(texto_positivo, "Diario")
        assert score > 50.0

    def test_score_no_excede_100(self, scoring):
        """El score nunca debe superar 100.0."""
        texto_max = "cobre oro litio cobre oro litio cobre oro litio proyecto de cobre mina a cielo abierto"
        score = scoring.calcular_score(texto_max, "diario de cuyo")
        assert score <= 100.0

    def test_score_texto_muy_largo(self, scoring):
        """Textos muy largos no deben romper el scoring."""
        texto = "cobre " * 1000 + "proyecto de cobre"
        score = scoring.calcular_score(texto, "Diario")
        assert 1.0 <= score <= 100.0

    def test_score_caracteres_especiales(self, scoring):
        """Caracteres especiales no deben romper el scoring."""
        texto = "Proyecto de cobre @#$%&*() en San Juan!!!"
        score = scoring.calcular_score(texto, "Diario")
        assert 1.0 <= score <= 100.0

    def test_score_unicode(self, scoring):
        """Unicode no debe romper el scoring."""
        texto = "Proyecto de cobre en San Juan 🏔️"
        score = scoring.calcular_score(texto, "Diario")
        assert 1.0 <= score <= 100.0

    def test_score_medio_vacio(self, scoring):
        """Medio vacío no debe romper el scoring."""
        score = scoring.calcular_score("proyecto de cobre", "")
        assert 1.0 <= score <= 100.0
