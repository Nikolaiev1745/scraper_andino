"""
Motor de scoring semántico basado en TF-IDF + reglas de dominio.
"""

import logging
import re
from typing import Optional, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .config import Config
from .utils import limpiar_texto

logger = logging.getLogger("scraper_andino.scoring")


class ScoringEngine:
    """Motor de scoring semántico basado en TF-IDF + reglas de dominio."""

    def __init__(self, config: Config):
        self.config = config
        self._vectorizer: Optional[TfidfVectorizer] = None
        self._vec_positivas = None
        self._vec_vagas = None
        self._fit()

    def _fit(self) -> None:
        """Entrena el vectorizador TF-IDF con el corpus de entrenamiento."""
        corpus = [limpiar_texto(t) for t in self.config.semillas_positivas + self.config.terminos_vagos]
        self._vectorizer = TfidfVectorizer().fit(corpus)
        self._vec_positivas = self._vectorizer.transform(
            [limpiar_texto(t) for t in self.config.semillas_positivas]
        )
        self._vec_vagas = self._vectorizer.transform(
            [limpiar_texto(t) for t in self.config.terminos_vagos]
        )
        logger.info("ScoringEngine inicializado con %d términos de entrenamiento", len(corpus))

    def calcular_score(self, texto: str, medio: str) -> float:
        """Calcula el score final de una noticia.

        Args:
            texto: Texto completo de la noticia (título + resumen).
            medio: Nombre del medio de comunicación.

        Returns:
            Score entre 1.0 y 100.0. 0.0 si debe descartarse.
        """
        txt_limpio = limpiar_texto(texto)
        if not txt_limpio.strip():
            return 0.0

        # Filtro de términos negativos
        for t_neg in self.config.terminos_negativos:
            if re.search(r'\b' + re.escape(limpiar_texto(t_neg)) + r'\b', txt_limpio):
                logger.debug("Noticia descartada por término negativo: %s", t_neg)
                return 0.0

        # Score semántico base
        score_sem = self._score_semantico(txt_limpio)

        # Densidad técnica y de términos vagos
        densidad_tecnica = self._calcular_densidad(txt_limpio, self.config.glosario_tecnico)
        densidad_vaga = self._calcular_densidad(txt_limpio, self.config.terminos_vagos)

        # Bono por densidad técnica (con límite para evitar keyword stuffing)
        bono_densidad = min(densidad_tecnica * 0.05, 0.15)  # cap de 0.15
        score_final = score_sem + bono_densidad

        # Penalización por exceso de términos vagos
        if densidad_vaga > (densidad_tecnica * 2) and densidad_vaga > 2:
            score_final *= 0.6

        score_pct = score_final * 100

        # Bono por medio andino
        medio_limpio = medio.lower().strip()
        if any(m in medio_limpio for m in self.config.medios_andinos):
            score_pct += 15.0
            logger.debug("Bono de medio andino aplicado a: %s", medio)

        return round(max(1.0, min(100.0, score_pct)), 2)

    def _score_semantico(self, txt_limpio: str) -> float:
        """Calcula similitud coseno contra semillas positivas y vagas."""
        try:
            vec_texto = self._vectorizer.transform([txt_limpio])
            sim_pos = float(np.max(cosine_similarity(vec_texto, self._vec_positivas)))
            sim_vaga = float(np.max(cosine_similarity(vec_texto, self._vec_vagas)))
            score_base = sim_pos - (sim_vaga * 0.3)
            return max(0.0, min(1.0, score_base))
        except Exception as e:
            logger.warning("Error en score semántico: %s", e)
            return 0.0

    @staticmethod
    def _calcular_densidad(texto: str, glosario: Tuple[str, ...]) -> int:
        """Cuenta ocurrencias de términos del glosario en el texto."""
        coincidencias = 0
        for termino in glosario:
            pattern = r'\b' + re.escape(limpiar_texto(termino)) + r'\b'
            coincidencias += len(re.findall(pattern, texto))
        return coincidencias
