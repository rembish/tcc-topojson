"""Tests for validate.py — output validation functions."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import validate


def _make_feature(idx: int, name: str = "Test", missing_prop: str | None = None) -> dict:
    """Helper to build a valid GeoJSON feature."""
    props = {
        "tcc_index": idx,
        "name": name,
        "region": "Test Region",
        "sovereign": "Testland",
        "type": "country",
    }
    if missing_prop:
        del props[missing_prop]
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [0, 0]},
        "properties": props,
    }


def _write_geojson(path: Path, features: list) -> None:
    path.write_text(json.dumps({"type": "FeatureCollection", "features": features}))


def _write_topojson(path: Path, n_geoms: int = 330, size_kb: int = 100) -> None:
    geoms = [{"type": "Point"} for _ in range(n_geoms)]
    data = {"type": "Topology", "objects": {"tcc": {"geometries": geoms}}}
    path.write_text(json.dumps(data))


class TestValidateGeoJSON:
    def test_valid_330_features(self, tmp_path):
        features = [_make_feature(i) for i in range(1, 331)]
        p = tmp_path / "merged.geojson"
        _write_geojson(p, features)
        assert validate.validate_geojson(p) is True

    def test_wrong_count(self, tmp_path, capsys):
        features = [_make_feature(i) for i in range(1, 11)]
        p = tmp_path / "merged.geojson"
        _write_geojson(p, features)
        result = validate.validate_geojson(p)
        assert result is False

    def test_duplicate_index(self, tmp_path, capsys):
        features = [_make_feature(i) for i in range(1, 330)]
        features.append(_make_feature(1))  # duplicate index 1
        p = tmp_path / "merged.geojson"
        _write_geojson(p, features)
        result = validate.validate_geojson(p)
        assert result is False

    def test_missing_required_property(self, tmp_path):
        features = [_make_feature(i) for i in range(1, 330)]
        features.append(_make_feature(330, missing_prop="sovereign"))
        p = tmp_path / "merged.geojson"
        _write_geojson(p, features)
        result = validate.validate_geojson(p)
        assert result is False

    def test_missing_geometry(self, tmp_path):
        features = [_make_feature(i) for i in range(1, 330)]
        bad = _make_feature(330)
        bad["geometry"] = None
        features.append(bad)
        p = tmp_path / "merged.geojson"
        _write_geojson(p, features)
        result = validate.validate_geojson(p)
        assert result is False

    def test_missing_tcc_index(self, tmp_path):
        features = [_make_feature(i) for i in range(1, 330)]
        no_idx = {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [0, 0]},
            "properties": {"name": "NoIndex"},
        }
        features.append(no_idx)
        p = tmp_path / "merged.geojson"
        _write_geojson(p, features)
        result = validate.validate_geojson(p)
        assert result is False


class TestValidateTopoJSON:
    def test_valid_330_geometries(self, tmp_path):
        p = tmp_path / "tcc-330.json"
        _write_topojson(p, n_geoms=330)
        assert validate.validate_topojson(p) is True

    def test_wrong_count(self, tmp_path):
        p = tmp_path / "tcc-330.json"
        _write_topojson(p, n_geoms=100)
        assert validate.validate_topojson(p) is False


class TestMain:
    def test_exits_1_when_geojson_missing(self, tmp_path, mocker):
        mocker.patch.object(validate, "OUTPUT_DIR", tmp_path)
        with pytest.raises(SystemExit) as exc_info:
            validate.main()
        assert exc_info.value.code == 1

    def test_exits_0_when_both_valid(self, tmp_path, mocker):
        mocker.patch.object(validate, "OUTPUT_DIR", tmp_path)
        features = [_make_feature(i) for i in range(1, 331)]
        _write_geojson(tmp_path / "merged.geojson", features)
        _write_topojson(tmp_path / "tcc-330.json", n_geoms=330)
        # Should not raise
        validate.main()
