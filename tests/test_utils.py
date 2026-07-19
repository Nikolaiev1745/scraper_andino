"""
Tests para utilidades de procesamiento de texto.
"""

from src.utils import limpiar_texto


class TestLimpiarTexto:
    """Tests para la función de limpieza de texto."""

    def test_texto_vacio(self):
        assert limpiar_texto("") == ""
        assert limpiar_texto(None) == ""

    def test_normalizacion_acentos(self):
        assert limpiar_texto("Máquina de Lixiviación") == "maquina de lixiviacion"

    def test_eliminacion_puntuacion(self):
        assert limpiar_texto("Cobre, oro y plata!") == "cobre oro y plata"

    def test_minusculas(self):
        assert limpiar_texto("MINA A CIELO ABIERTO") == "mina a cielo abierto"

    def test_espacios_multiples(self):
        """La función no normaliza espacios múltiples (comportamiento documentado)."""
        resultado = limpiar_texto("cobre    oro")
        assert "cobre" in resultado
        assert "oro" in resultado

    def test_emojis_eliminados(self):
        """Los emojis deben ser eliminados."""
        resultado = limpiar_texto("Mina 🏔️💎⛏️")
        assert "🏔️" not in resultado
        assert "💎" not in resultado
