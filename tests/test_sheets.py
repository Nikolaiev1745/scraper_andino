"""
Tests para el cliente de Google Sheets.
"""

from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

from src.config import Config
from src.sheets_client import SheetsClient


class TestSheetsClient:
    """Tests para el cliente de Sheets con mocks."""

    @patch("src.sheets_client.ServiceAccountCredentials")
    @patch("src.sheets_client.gspread.authorize")
    def test_conexion_exitosa(self, mock_authorize, mock_creds, tmp_path):
        """La conexión debe establecerse correctamente."""
        fake_creds = tmp_path / "creds.json"
        fake_creds.write_text("{}")
        config = Config(ruta_creds=fake_creds)

        mock_gc = MagicMock()
        mock_authorize.return_value = mock_gc
        mock_creds.from_service_account_file.return_value = Mock(expired=False)

        client = SheetsClient(config)
        assert client._gc is not None
        mock_creds.from_service_account_file.assert_called_once()

    def test_conexion_falla_sin_creds(self):
        """Debe lanzar FileNotFoundError si no hay credenciales."""
        config = Config(ruta_creds=Path("/no/existe/creds.json"))
        with pytest.raises(FileNotFoundError):
            SheetsClient(config)

    @patch("src.sheets_client.ServiceAccountCredentials")
    @patch("src.sheets_client.gspread.authorize")
    def test_obtener_urls_existentes(self, mock_authorize, mock_creds, tmp_path):
        """Debe retornar un set de URLs existentes."""
        fake_creds = tmp_path / "creds.json"
        fake_creds.write_text("{}")
        config = Config(ruta_creds=fake_creds)

        mock_gc = MagicMock()
        mock_ws = MagicMock()
        mock_ws.col_values.return_value = ["url (fuente)", "http://a.com", "http://b.com"]
        mock_sh = MagicMock()
        mock_sh.get_worksheet.return_value = mock_ws
        mock_gc.open.return_value = mock_sh
        mock_authorize.return_value = mock_gc
        mock_creds.from_service_account_file.return_value = Mock(expired=False)

        client = SheetsClient(config)
        client._sh = mock_sh
        urls = client.obtener_urls_existentes(mock_ws)
        assert urls == {"http://a.com", "http://b.com"}
