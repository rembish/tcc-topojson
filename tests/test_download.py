"""Tests for src/download.py — download functions with mocked HTTP."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pytest


class TestDownloadNeDataset:
    def test_skips_if_shp_exists(self, tmp_path, mocker):
        from src import download as dl

        mocker.patch.object(dl, "DATA_DIR", tmp_path)
        shp_file = tmp_path / "ne_10m_test.shp"
        shp_file.touch()

        mock_get = mocker.patch("requests.get")
        dl.download_ne_dataset("ne_10m_test")
        mock_get.assert_not_called()

    def test_downloads_and_extracts_zip(self, tmp_path, mocker):
        from src import download as dl

        mocker.patch.object(dl, "DATA_DIR", tmp_path)

        # Build a minimal in-memory zip
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("ne_10m_test.shp", b"fake shp data")
            zf.writestr("ne_10m_test.dbf", b"fake dbf data")
        buf.seek(0)

        mock_resp = mocker.MagicMock()
        mock_resp.content = buf.read()
        mock_resp.raise_for_status = mocker.MagicMock()
        mocker.patch("requests.get", return_value=mock_resp)

        dl.download_ne_dataset("ne_10m_test")

        assert (tmp_path / "ne_10m_test.shp").exists()
        assert (tmp_path / "ne_10m_test.dbf").exists()

    def test_raises_on_http_error(self, tmp_path, mocker):
        from src import download as dl

        mocker.patch.object(dl, "DATA_DIR", tmp_path)

        import requests

        mock_resp = mocker.MagicMock()
        mock_resp.raise_for_status.side_effect = requests.HTTPError("404")
        mocker.patch("requests.get", return_value=mock_resp)

        with pytest.raises(requests.HTTPError):
            dl.download_ne_dataset("ne_10m_missing")


class TestDownloadBoundary:
    def test_skips_if_exists(self, tmp_path, mocker):
        from src import download as dl

        mocker.patch.object(dl, "DATA_DIR", tmp_path)
        (tmp_path / "europe_asia_boundary.geojson").write_text("{}")

        mock_get = mocker.patch("requests.get")
        dl.download_boundary()
        mock_get.assert_not_called()

    def test_downloads_and_writes_text(self, tmp_path, mocker):
        from src import download as dl

        mocker.patch.object(dl, "DATA_DIR", tmp_path)

        mock_resp = mocker.MagicMock()
        mock_resp.text = '{"type":"FeatureCollection","features":[]}'
        mock_resp.raise_for_status = mocker.MagicMock()
        mocker.patch("requests.get", return_value=mock_resp)

        dl.download_boundary()

        out = tmp_path / "europe_asia_boundary.geojson"
        assert out.exists()
        assert out.read_text() == mock_resp.text


class TestMain:
    def test_main_calls_all_downloads(self, tmp_path, mocker):
        from src import download as dl

        mocker.patch.object(dl, "DATA_DIR", tmp_path)
        mock_ne = mocker.patch.object(dl, "download_ne_dataset")
        mock_bnd = mocker.patch.object(dl, "download_boundary")

        dl.main()

        assert mock_ne.call_count == len(dl.NE_DATASETS)
        mock_bnd.assert_called_once()
