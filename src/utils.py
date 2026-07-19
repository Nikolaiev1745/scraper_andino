"""
Utilidades de procesamiento de texto.
"""

import re


def limpiar_texto(texto: str) -> str:
    """Normaliza texto: minúsculas, sin acentos, sin puntuación.

    Args:
        texto: Texto a normalizar.

    Returns:
        Texto limpio en minúsculas, sin acentos ni caracteres especiales.
    """
    if not texto:
        return ""
    texto = texto.lower()
    texto = re.sub(
        r'[áéíóúü]',
        lambda m: {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ü': 'u'}[m.group(0)],
        texto
    )
    texto = re.sub(r'[^a-z0-9ñ\s]', '', texto)
    return texto
