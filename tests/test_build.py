"""Tests for src/build.py — build orchestration."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import geopandas as gpd
from shapely.geometry import box, mapping


def _make_feature(idx: int) -> dict:
    return {
        "type": "Feature",
        "geometry": mapping(box(0, 0, 1, 1)),
        "properties": {"tcc_index": idx, "name": f"Dest {idx}"},
    }


class TestWriteGeojson:
    def test_writes_sorted_feature_collection(self, tmp_path):
        from src.build import write_geojson

        features = {3: _make_feature(3), 1: _make_feature(1), 2: _make_feature(2)}
        out = tmp_path / "test.geojson"
        write_geojson(features, out)

        data = json.loads(out.read_text())
        assert data["type"] == "FeatureCollection"
        assert len(data["features"]) == 3
        # Should be sorted by tcc_index
        indices = [f["properties"]["tcc_index"] for f in data["features"]]
        assert indices == [1, 2, 3]

    def test_creates_parent_dirs(self, tmp_path):
        from src.build import write_geojson

        nested = tmp_path / "a" / "b" / "c.geojson"
        write_geojson({1: _make_feature(1)}, nested)
        assert nested.exists()


class TestExtractFeature:
    """Tests for the _extract_feature dispatcher."""

    def test_dispatch_direct(self, subunits_gdf, units_gdf, admin1_gdf, disputed_gdf, base_dest):
        from src.build import _extract_feature

        feat = _extract_feature(
            base_dest, "direct", subunits_gdf, units_gdf, admin1_gdf, disputed_gdf, {}
        )
        assert feat is not None

    def test_dispatch_unknown_strategy(
        self, subunits_gdf, units_gdf, admin1_gdf, disputed_gdf, base_dest
    ):
        from src.build import _extract_feature

        dest = {**base_dest, "strategy": "totally_unknown"}
        feat = _extract_feature(
            dest, "totally_unknown", subunits_gdf, units_gdf, admin1_gdf, disputed_gdf, {}
        )
        assert feat is None

    def test_dispatch_subunit(self, subunits_gdf, units_gdf, admin1_gdf, disputed_gdf):
        from src.build import _extract_feature

        dest = {
            "tcc_index": 10,
            "name": "Testland",
            "region": "Test",
            "iso_a2": None,
            "iso_a3": "TST",
            "iso_n3": None,
            "sovereign": "Testland",
            "type": "subnational",
            "su_a3": "TST",
        }
        feat = _extract_feature(
            dest, "subunit", subunits_gdf, units_gdf, admin1_gdf, disputed_gdf, {}
        )
        assert feat is not None

    def test_dispatch_admin1(self, subunits_gdf, units_gdf, admin1_gdf, disputed_gdf, admin1_dest):
        from src.build import _extract_feature

        feat = _extract_feature(
            admin1_dest, "admin1", subunits_gdf, units_gdf, admin1_gdf, disputed_gdf, {}
        )
        assert feat is not None

    def test_dispatch_point(self, subunits_gdf, units_gdf, admin1_gdf, disputed_gdf):
        from src.build import _extract_feature

        dest = {
            "tcc_index": 18,
            "name": "Midway",
            "region": "Pacific Ocean",
            "iso_a2": None,
            "iso_a3": None,
            "iso_n3": None,
            "sovereign": "United States",
            "type": "territory",
            "lat": 28.2,
            "lon": -177.4,
        }
        feat = _extract_feature(
            dest, "point", subunits_gdf, units_gdf, admin1_gdf, disputed_gdf, {}
        )
        assert feat is not None
        assert feat["properties"]["is_point"] is True

    def test_dispatch_antarctic(self, subunits_gdf, units_gdf, admin1_gdf, disputed_gdf):
        from src.build import _extract_feature

        dest = {
            "tcc_index": 181,
            "name": "Test Antarctic",
            "region": "Antarctica",
            "iso_a2": None,
            "iso_a3": None,
            "iso_n3": None,
            "sovereign": "Argentina",
            "type": "antarctic",
            "lon_west": -74,
            "lon_east": -25,
        }
        feat = _extract_feature(
            dest, "antarctic", subunits_gdf, units_gdf, admin1_gdf, disputed_gdf, {}
        )
        assert feat is not None

    def test_dispatch_disputed(self, subunits_gdf, units_gdf, admin1_gdf, disputed_gdf):
        from src.build import _extract_feature

        dest = {
            "tcc_index": 50,
            "name": "Disputed Zone",
            "region": "Test",
            "iso_a2": None,
            "iso_a3": None,
            "iso_n3": None,
            "sovereign": "Test",
            "type": "disputed",
        }
        feat = _extract_feature(
            dest, "disputed", subunits_gdf, units_gdf, admin1_gdf, disputed_gdf, {}
        )
        assert feat is not None

    def test_dispatch_remainder(self, subunits_gdf, units_gdf, admin1_gdf, disputed_gdf):
        from src.build import _extract_feature

        dest = {
            "tcc_index": 10,
            "name": "Testland",
            "region": "Test",
            "iso_a2": None,
            "iso_a3": None,
            "iso_n3": None,
            "sovereign": "Testland",
            "type": "country",
            "adm0_a3": "TST",
        }
        feat = _extract_feature(
            dest, "remainder", subunits_gdf, units_gdf, admin1_gdf, disputed_gdf, {}
        )
        assert feat is not None

    def test_dispatch_island_bbox(
        self, subunits_gdf, units_gdf, admin1_gdf, disputed_gdf, island_dest
    ):
        from src.build import _extract_feature

        feat = _extract_feature(
            island_dest, "island_bbox", subunits_gdf, units_gdf, admin1_gdf, disputed_gdf, {}
        )
        assert feat is not None

    def test_dispatch_disputed_remainder(self, subunits_gdf, units_gdf, admin1_gdf, disputed_gdf):
        from src.build import _extract_feature

        dest = {
            "tcc_index": 10,
            "name": "Testland",
            "region": "Test",
            "iso_a2": None,
            "iso_a3": None,
            "iso_n3": None,
            "sovereign": "Testland",
            "type": "country",
            "adm0_a3": "TST",
        }
        for strat in ("disputed_remainder", "disputed_subtract"):
            feat = _extract_feature(
                dest, strat, subunits_gdf, units_gdf, admin1_gdf, disputed_gdf, {}
            )
            assert feat is not None


class TestLoadData:
    """Test load_data() with mocked geopandas."""

    def test_returns_four_gdfs(self, subunits_gdf, units_gdf, admin1_gdf, disputed_gdf, mocker):
        from src import build as bld

        mocker.patch(
            "geopandas.read_file", side_effect=[subunits_gdf, units_gdf, admin1_gdf, disputed_gdf]
        )
        mocker.patch.object(bld, "DATA_DIR", MagicMock())

        sub, uni, adm, dis = bld.load_data()
        assert len(sub) == len(subunits_gdf)
        assert len(uni) == len(units_gdf)
        assert len(adm) == len(admin1_gdf)
        assert len(dis) == len(disputed_gdf)


class TestBuildFeatures:
    """Test the two-pass build logic."""

    def _make_minimal_gdf(self):
        return gpd.GeoDataFrame(
            {"ADM0_A3": ["ATA"], "SU_A3": ["ATA"], "GU_A3": ["ATA"], "ISO_A3": ["ATA"]},
            geometry=[box(-180, -90, 180, -60)],
            crs="EPSG:4326",
        )

    def test_defers_group_remainder(
        self, subunits_gdf, units_gdf, admin1_gdf, disputed_gdf, mocker
    ):
        """group_remainder destinations should be processed in the second pass."""
        from src import build as bld

        # Country spans 10-20; feature 1 takes only the left half (10-15)
        # so feature 2 (remainder) gets the right half (15-20)
        direct_dest = {
            "tcc_index": 1,
            "name": "Testland North",
            "region": "Test",
            "iso_a2": None,
            "iso_a3": "TST",
            "iso_n3": None,
            "sovereign": "Testland",
            "type": "subnational",
            "strategy": "admin1",
            "adm0_a3": "TST",
            "admin1": ["North Province"],
        }
        remainder_dest = {
            "tcc_index": 2,
            "name": "Testland Remainder",
            "region": "Test",
            "iso_a2": None,
            "iso_a3": None,
            "iso_n3": None,
            "sovereign": "Testland",
            "type": "country",
            "strategy": "group_remainder",
            "adm0_a3": "TST",
            "subtract_indices": [1],
        }
        mocker.patch.object(bld, "get_destinations", return_value=[direct_dest, remainder_dest])

        # units_gdf needs ATA for Antarctica detection; add TST too
        units_with_tst = gpd.GeoDataFrame(
            {
                "ADM0_A3": ["TST", "ATA"],
                "SU_A3": ["TST", "ATA"],
                "GU_A3": ["TST", "ATA"],
                "ISO_A3": ["TST", "ATA"],
                "NAME": ["Testland", "Antarctica"],
                "NAME_EN": ["Testland", "Antarctica"],
            },
            geometry=[box(10, 10, 20, 20), box(-180, -90, 180, -60)],
            crs="EPSG:4326",
        )

        built = bld.build_features(subunits_gdf, units_with_tst, admin1_gdf, disputed_gdf)
        # First pass: admin1 feature (North Province) is built
        assert 1 in built
        # Second pass: remainder after subtracting feature 1 should be non-empty
        assert 2 in built

    def test_reports_failures(
        self, subunits_gdf, units_gdf, admin1_gdf, disputed_gdf, mocker, capsys
    ):
        """Failed extractions should be reported but not crash the build."""
        from src import build as bld

        failing_dest = {
            "tcc_index": 99,
            "name": "Missing",
            "region": "Test",
            "iso_a2": None,
            "iso_a3": "ZZZ",
            "iso_n3": None,
            "sovereign": "Nobody",
            "type": "country",
            "strategy": "direct",
        }
        mocker.patch.object(bld, "get_destinations", return_value=[failing_dest])

        built = bld.build_features(subunits_gdf, units_gdf, admin1_gdf, disputed_gdf)
        assert 99 not in built
        captured = capsys.readouterr()
        assert "FAILED" in captured.out


class TestMain:
    def test_main_orchestrates_build(
        self, subunits_gdf, units_gdf, admin1_gdf, disputed_gdf, tmp_path, mocker
    ):
        from src import build as bld

        mocker.patch.object(
            bld, "load_data", return_value=(subunits_gdf, units_gdf, admin1_gdf, disputed_gdf)
        )
        mocker.patch.object(bld, "OUTPUT_DIR", tmp_path)

        # Patch get_destinations to return minimal set to avoid 330-feature build
        mocker.patch.object(
            bld,
            "get_destinations",
            return_value=[
                {
                    "tcc_index": 42,
                    "name": "Testland",
                    "region": "Test",
                    "iso_a2": None,
                    "iso_a3": "TST",
                    "iso_n3": None,
                    "sovereign": "Testland",
                    "type": "country",
                    "strategy": "direct",
                }
            ],
        )

        bld.main()

        out = tmp_path / "merged.geojson"
        assert out.exists()
        data = json.loads(out.read_text())
        assert data["type"] == "FeatureCollection"
