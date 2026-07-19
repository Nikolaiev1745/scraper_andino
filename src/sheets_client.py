"""
Cliente de Google Sheets con autenticación moderna y manejo de errores.
"""

import logging
from typing import List, Dict, Optional, Set

import gspread
from gspread_formatting import (
    ConditionalFormatRule,
    GradientRule,
    InterpolationPoint,
    Color,
    GridRange,
    get_conditional_format_rules,
)
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from google.auth.transport.requests import Request

from .config import Config

logger = logging.getLogger("scraper_andino.sheets")


class SheetsClient:
    """Cliente de Google Sheets con autenticación moderna y manejo de errores."""

    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    def __init__(self, config: Config):
        self.config = config
        self._gc: Optional[gspread.Client] = None
        self._sh: Optional[gspread.Spreadsheet] = None
        self._connect()

    def _connect(self) -> None:
        """Establece conexión con Google Sheets usando google-auth."""
        if not self.config.ruta_creds.exists():
            raise FileNotFoundError(
                f"No se encontró credenciales en: {self.config.ruta_creds}"
            )

        try:
            creds = ServiceAccountCredentials.from_service_account_file(
                str(self.config.ruta_creds),
                scopes=self.SCOPES,
            )
            # Refrescar token si es necesario
            if creds.expired:
                creds.refresh(Request())

            self._gc = gspread.authorize(creds)
            logger.info("Conexión a Google Sheets establecida correctamente")
        except Exception as e:
            logger.error("Fallo al conectar con Google Sheets: %s", e)
            raise

    def obtener_o_crear_hoja(self) -> gspread.Worksheet:
        """Obtiene la hoja existente o crea una nueva."""
        try:
            self._sh = self._gc.open(self.config.nombre_documento)
            ws = self._sh.get_worksheet(0)
            logger.info("Hoja existente abierta: %s", self._sh.url)
            return ws
        except gspread.exceptions.SpreadsheetNotFound:
            self._sh = self._gc.create(self.config.nombre_documento)
            ws = self._sh.get_worksheet(0)
            logger.info("Nueva hoja creada: %s", self._sh.url)
            return ws
        except Exception as e:
            logger.error("Error al obtener/crear hoja: %s", e)
            raise

    def obtener_urls_existentes(self, ws: gspread.Worksheet) -> Set[str]:
        """Obtiene URLs ya registradas para deduplicación persistente.

        Args:
            ws: Worksheet de Google Sheets.

        Returns:
            Set de URLs ya existentes en la columna de fuentes.
        """
        try:
            urls = ws.col_values(6)  # Columna F (url)
            return set(urls[1:])  # Saltar header
        except Exception as e:
            logger.warning("No se pudieron leer URLs existentes: %s", e)
            return set()

    def guardar_noticias(self, noticias: List[Dict]) -> None:
        """Guarda noticias en Sheets con formato condicional.

        Args:
            noticias: Lista de diccionarios con datos de noticias.
        """
        if not noticias:
            logger.info("No hay noticias para guardar")
            return

        ws = self.obtener_o_crear_hoja()
        urls_existentes = self.obtener_urls_existentes(ws)

        # Filtrar duplicados persistentes
        noticias_nuevas = [n for n in noticias if n["url"] not in urls_existentes]
        if not noticias_nuevas:
            logger.info("Todas las noticias ya existen en la hoja")
            return

        # Ordenar por score descendente
        noticias_nuevas.sort(key=lambda x: x["score"], reverse=True)

        # Si es la primera vez, escribir headers
        if not urls_existentes:
            ws.clear()
            headers = [
                "titulo", "fecha", "medio", "autor",
                "descripcion", "url (fuente)", "score de precision"
            ]
            ws.append_row(headers)
            logger.info("Headers escritos en la hoja")

        filas = [
            [
                n["titulo"],
                n["fecha"],
                n["medio"],
                n["autor"],
                n["descripcion"],
                n["url"],
                n["score"],
            ]
            for n in noticias_nuevas
        ]
        ws.append_rows(filas)
        logger.info("%d noticias nuevas guardadas", len(noticias_nuevas))

        # Aplicar formato condicional
        self._aplicar_formato_condicional(ws)

    def _aplicar_formato_condicional(self, ws: gspread.Worksheet) -> None:
        """Aplica gradiente de color a la columna de score."""
        try:
            total_filas = len(ws.get_all_values())
            if total_filas <= 1:
                return

            rango_score = f"G2:G{total_filas}"
            regla = ConditionalFormatRule(
                ranges=[GridRange.from_a1_range(rango_score, ws)],
                gradientRule=GradientRule(
                    minpoint=InterpolationPoint(
                        color=Color(1, 1, 1), type="NUMBER", value="1"
                    ),
                    midpoint=InterpolationPoint(
                        color=Color(0.78, 0.93, 0.80), type="NUMBER", value="50"
                    ),
                    maxpoint=InterpolationPoint(
                        color=Color(0.10, 0.36, 0.12), type="NUMBER", value="100"
                    ),
                ),
            )
            rules = get_conditional_format_rules(ws)
            rules.clear()
            rules.append(regla)
            rules.save()
            logger.info("Formato condicional aplicado a %s", rango_score)
        except Exception as e:
            logger.warning("Error aplicando formato condicional: %s", e)
