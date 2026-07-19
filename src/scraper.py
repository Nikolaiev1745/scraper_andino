"""
Scraper de Google News RSS con backoff y logging.
"""

import logging
import re
import time
import urllib.parse
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Set

import email.utils
import feedparser

from .config import Config
from .scoring import ScoringEngine

logger = logging.getLogger("scraper_andino.scraper")


class GoogleNewsScraper:
    """Scraper de Google News RSS con backoff y logging."""

    def __init__(self, config: Config, scoring: ScoringEngine):
        self.config = config
        self.scoring = scoring

    def _fetch_feed(self, url: str, intento: int = 0) -> Optional[feedparser.FeedParserDict]:
        """Obtiene un feed con backoff exponencial ante errores.

        Args:
            url: URL del feed RSS.
            intento: Número de intento actual.

        Returns:
            Feed parseado o None si falla definitivamente.
        """
        try:
            feed = feedparser.parse(url)
            if feed.bozo and hasattr(feed, "bozo_exception"):
                logger.warning("Feed malformado: %s", feed.bozo_exception)
            return feed
        except Exception as e:
            if intento < self.config.max_retries:
                wait = self.config.backoff_base ** intento
                logger.warning(
                    "Error fetching %s, reintentando en %.1fs... (%d/%d)",
                    url, wait, intento + 1, self.config.max_retries
                )
                time.sleep(wait)
                return self._fetch_feed(url, intento + 1)
            logger.error("Fallo definitivo al obtener feed: %s — %s", url, e)
            return None

    def scrapear(self) -> List[Dict]:
        """Ejecuta el scraping completo por provincias.

        Returns:
            Lista de noticias captadas y filtradas.
        """
        ahora = datetime.now(timezone.utc)
        limite_3m = ahora - timedelta(days=self.config.dias_recientes)
        limite_1y = ahora - timedelta(days=self.config.dias_maximo)
        noticias: List[Dict] = []
        urls_vistas: Set[str] = set()

        for prov in self.config.provincias:
            query = f"mineria {prov} o cobre o litio"
            query_encoded = urllib.parse.quote(query)
            url_rss = (
                f"https://news.google.com/rss/search?q={query_encoded}"
                f"&hl=es-AR&gl=AR&ceid=AR:es"
            )

            logger.info("Escaneando %s...", prov)
            feed = self._fetch_feed(url_rss)
            if not feed or not hasattr(feed, "entries"):
                continue

            logger.info("Procesando %d entradas de %s", len(feed.entries), prov)

            for entry in feed.entries:
                noticia = self._procesar_entry(
                    entry, ahora, limite_3m, limite_1y, urls_vistas
                )
                if noticia:
                    noticias.append(noticia)
                    urls_vistas.add(noticia["url"])

            # Rate limiting amigable
            time.sleep(self.config.delay_entre_requests)

        logger.info("Scraping completado: %d noticias captadas", len(noticias))
        return noticias

    def _procesar_entry(
        self,
        entry: feedparser.FeedParserDict,
        ahora: datetime,
        limite_3m: datetime,
        limite_1y: datetime,
        urls_vistas: Set[str],
    ) -> Optional[Dict]:
        """Procesa una entrada individual del feed.

        Args:
            entry: Entrada del feed RSS.
            ahora: Fecha/hora actual.
            limite_3m: Límite de 3 meses para noticias recientes.
            limite_1y: Límite de 1 año para noticias antiguas.
            urls_vistas: Set de URLs ya procesadas.

        Returns:
            Diccionario con datos de la noticia o None si debe descartarse.
        """
        # Parsear fecha
        try:
            fecha_pub = email.utils.parsedate_to_datetime(entry.published)
        except Exception:
            fecha_pub = ahora

        if fecha_pub < limite_1y:
            return None

        # Extraer título y medio
        titulo = entry.title
        medio = "Desconocido"
        if " - " in titulo:
            partes = titulo.rsplit(" - ", 1)
            medio = partes[-1].strip()
            titulo = partes[0].strip()

        url = entry.link
        if url in urls_vistas:
            return None

        # Extraer resumen
        resumen = entry.get("summary", "")
        resumen_limpio = re.sub(r"<[^<]+?>", "", resumen).strip()
        texto_completo = f"{titulo} {resumen_limpio}"

        # Autor
        autor = ""
        if hasattr(entry, "author") and entry.author.strip():
            autor = entry.author.strip()
        elif hasattr(entry, "authors") and entry.authors:
            autor = ", ".join(
                a.get("name", "") for a in entry.authors if "name" in a
            )
        if not autor:
            autor = f"Redacción de {medio}"

        # Calcular score
        score = self.scoring.calcular_score(texto_completo, medio)
        if score == 0.0:
            return None

        # Umbral para noticias viejas
        if fecha_pub < limite_3m and score < self.config.umbral_score_viejas:
            return None

        return {
            "titulo": titulo,
            "fecha": fecha_pub.strftime("%d/%m/%Y"),
            "medio": medio,
            "autor": autor,
            "descripcion": resumen_limpio,
            "url": url,
            "score": score,
        }
