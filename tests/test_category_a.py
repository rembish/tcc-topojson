"""Tests for src/category_a.py — direct feature extraction."""

from __future__ import annotations

import pytest
import geopandas as gpd
from shapely.geometry import box

from src.category_a import _find_geom, extract_direct, extract_subunit


class TestFindGeom:
    def test_finds_by_su_a3(self, subunits_gdf, units_gdf):
        result = _find_geom("TST", subunits_gdf, units_gdf)
        assert result is not None
        assert not result.is_empty

    def test_returns_none_for_missing(self, subunits_gdf, units_gdf):
        result = _find_geom("ZZZ", subunits_gdf, units_gdf)
        assert result is None

    def test_falls_back_to_units_gdf(self):
        empty_sub = gpd.GeoDataFrame(
            {"SU_A3": [], "ADM0_A3": [], "GU_A3": [], "ISO_A3": []},
            geometry=[],
            crs="EPSG:4326",
        )
        units = gpd.GeoDataFrame(
            {"ADM0_A3": ["XYZ"], "SU_A3": ["XYZ"], "GU_A3": ["XYZ"], "ISO_A3": ["XYZ"]},
            geometry=[box(0, 0, 5, 5)],
            crs="EPSG:4326",
        )
        result = _find_geom("XYZ", empty_sub, units)
        assert result is not None


class TestExtractDirect:
    def test_extracts_by_iso_a3(self, base_dest, subunits_gdf, units_gdf):
        feat = extract_direct(base_dest, subunits_gdf, units_gdf)
        assert feat is not None
        assert feat["type"] == "Feature"
        assert feat["properties"]["tcc_index"] == base_dest["tcc_index"]

    def test_returns_none_when_not_found(self, units_gdf, subunits_gdf):
        dest = {
            "tcc_index": 99,
            "name": "Nowhere",
            "region": "Test",
            "iso_a3": "ZZZ",
            "iso_a2": None,
            "iso_n3": None,
            "sovereign": "None",
            "type": "country",
        }
        feat = extract_direct(dest, subunits_gdf, units_gdf)
        assert feat is None

    def test_falls_back_to_name_match(self, units_gdf, subunits_gdf):
        dest = {
            "tcc_index": 5,
            "name": "Testland",
            "region": "Test",
            "iso_a3": None,
            "iso_a2": None,
            "iso_n3": None,
            "sovereign": "Testland",
            "type": "country",
        }
        feat = extract_direct(dest, subunits_gdf, units_gdf)
        assert feat is not None

    def test_merges_extra_features(self, base_dest, subunits_gdf, units_gdf):
        """merge_a3 should dissolve additional geometry into the result."""
        # Add a second feature to the GDFs
        extra_gdf = gpd.GeoDataFrame(
            {
                "SU_A3": ["EXT"],
                "ADM0_A3": ["EXT"],
                "GU_A3": ["EXT"],
                "ISO_A3": ["EXT"],
                "NAME": ["Extra"],
                "NAME_EN": ["Extra"],
            },
            geometry=[box(20, 10, 30, 20)],
            crs="EPSG:4326",
        )
        combined = gpd.pd.concat([subunits_gdf, extra_gdf], ignore_index=True)
        combined = gpd.GeoDataFrame(combined, crs="EPSG:4326")

        dest = {**base_dest, "merge_a3": ["EXT"]}
        feat = extract_direct(dest, combined, units_gdf)
        assert feat is not None
        # Merged area should be larger than the original box
        from shapely.geometry import shape

        geom = shape(feat["geometry"])
        assert geom.area > box(10, 10, 20, 20).area

    def test_uses_ne_a3_override(self, subunits_gdf, units_gdf):
        """ne_a3 should override iso_a3 for lookup."""
        dest = {
            "tcc_index": 7,
            "name": "Override",
            "region": "Test",
            "iso_a3": "ZZZ",
            "ne_a3": "TST",  # ne_a3 should be used
            "iso_a2": None,
            "iso_n3": None,
            "sovereign": "Testland",
            "type": "country",
        }
        feat = extract_direct(dest, subunits_gdf, units_gdf)
        assert feat is not None


class TestExtractSubunit:
    def test_extracts_by_su_a3(self, subunits_gdf):
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
        feat = extract_subunit(dest, subunits_gdf)
        assert feat is not None

    def test_returns_none_without_su_a3(self, subunits_gdf):
        dest = {
            "tcc_index": 11,
            "name": "Testland",
            "region": "Test",
            "iso_a2": None,
            "iso_a3": None,
            "iso_n3": None,
            "sovereign": "Testland",
            "type": "subnational",
            # No su_a3 key
        }
        feat = extract_subunit(dest, subunits_gdf)
        assert feat is None

    def test_falls_back_to_name_match(self, subunits_gdf):
        dest = {
            "tcc_index": 12,
            "name": "Testland",
            "region": "Test",
            "iso_a2": None,
            "iso_a3": None,
            "iso_n3": None,
            "sovereign": "Testland",
            "type": "subnational",
            "su_a3": "NOMATCH",  # Won't match by SU_A3
        }
        feat = extract_subunit(dest, subunits_gdf)
        assert feat is not None  # Falls back to name match
