"""Tests for src/category_b.py — admin1 extraction and remainder."""

from __future__ import annotations

import pytest
import geopandas as gpd
from shapely.geometry import box, shape

from src.category_b import (
    _match_provinces,
    extract_admin1,
    extract_disputed_remainder,
    extract_remainder,
)


class TestMatchProvinces:
    def test_exact_match(self, admin1_gdf):
        result = _match_provinces(admin1_gdf, ["North Province"])
        assert len(result) == 1
        assert result.iloc[0]["name"] == "North Province"

    def test_case_insensitive(self, admin1_gdf):
        result = _match_provinces(admin1_gdf, ["NORTH PROVINCE"])
        assert len(result) == 1

    def test_multiple_names(self, admin1_gdf):
        result = _match_provinces(admin1_gdf, ["North Province", "South Province"])
        assert len(result) == 2

    def test_contains_fallback(self, admin1_gdf):
        result = _match_provinces(admin1_gdf, ["North"])
        # Should find "North Province" via contains fallback
        assert len(result) >= 1

    def test_no_match_returns_empty(self, admin1_gdf):
        result = _match_provinces(admin1_gdf, ["Nonexistent Province"])
        assert len(result) == 0


class TestExtractAdmin1:
    def test_extracts_province(self, admin1_dest, admin1_gdf, subunits_gdf, units_gdf):
        feat = extract_admin1(admin1_dest, admin1_gdf, subunits_gdf, units_gdf)
        assert feat is not None
        assert feat["type"] == "Feature"
        assert feat["properties"]["name"] == "North Province"

    def test_returns_none_without_adm0(self, admin1_gdf, subunits_gdf, units_gdf):
        dest = {
            "tcc_index": 99,
            "name": "Test",
            "region": "Test",
            "iso_a2": None,
            "iso_a3": None,
            "iso_n3": None,
            "sovereign": "Test",
            "type": "subnational",
            "admin1": ["North Province"],
            # No adm0_a3
        }
        feat = extract_admin1(dest, admin1_gdf, subunits_gdf, units_gdf)
        assert feat is None

    def test_returns_none_without_admin1(self, admin1_gdf, subunits_gdf, units_gdf):
        dest = {
            "tcc_index": 99,
            "name": "Test",
            "region": "Test",
            "iso_a2": None,
            "iso_a3": None,
            "iso_n3": None,
            "sovereign": "Test",
            "type": "subnational",
            "adm0_a3": "TST",
            # No admin1 list
        }
        feat = extract_admin1(dest, admin1_gdf, subunits_gdf, units_gdf)
        assert feat is None

    def test_returns_none_when_no_match(self, admin1_gdf, subunits_gdf, units_gdf):
        dest = {
            "tcc_index": 99,
            "name": "Test",
            "region": "Test",
            "iso_a2": None,
            "iso_a3": None,
            "iso_n3": None,
            "sovereign": "Test",
            "type": "subnational",
            "adm0_a3": "TST",
            "admin1": ["Nonexistent Province"],
        }
        feat = extract_admin1(dest, admin1_gdf, subunits_gdf, units_gdf)
        assert feat is None


class TestExtractRemainder:
    def test_subtracts_admin1(self, subunits_gdf, units_gdf, admin1_gdf):
        dest = {
            "tcc_index": 10,
            "name": "Testland Mainland",
            "region": "Test",
            "iso_a2": None,
            "iso_a3": None,
            "iso_n3": None,
            "sovereign": "Testland",
            "type": "country",
            "adm0_a3": "TST",
            "subtract_admin1": ["North Province"],
        }
        feat = extract_remainder(dest, admin1_gdf, subunits_gdf, units_gdf)
        assert feat is not None
        # The result should be smaller than the full country
        result_geom = shape(feat["geometry"])
        country_area = box(10, 10, 20, 20).area
        assert result_geom.area < country_area

    def test_returns_none_without_adm0(self, subunits_gdf, units_gdf, admin1_gdf):
        dest = {
            "tcc_index": 10,
            "name": "Test",
            "region": "Test",
            "iso_a2": None,
            "iso_a3": None,
            "iso_n3": None,
            "sovereign": "Test",
            "type": "country",
            # No adm0_a3
        }
        feat = extract_remainder(dest, admin1_gdf, subunits_gdf, units_gdf)
        assert feat is None

    def test_returns_none_when_country_not_found(self, subunits_gdf, units_gdf, admin1_gdf):
        dest = {
            "tcc_index": 10,
            "name": "Test",
            "region": "Test",
            "iso_a2": None,
            "iso_a3": None,
            "iso_n3": None,
            "sovereign": "Test",
            "type": "country",
            "adm0_a3": "ZZZ",
        }
        feat = extract_remainder(dest, admin1_gdf, subunits_gdf, units_gdf)
        assert feat is None

    def test_no_subtract_names_returns_full(self, subunits_gdf, units_gdf, admin1_gdf):
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
            # No subtract_admin1
        }
        feat = extract_remainder(dest, admin1_gdf, subunits_gdf, units_gdf)
        assert feat is not None
        result_geom = shape(feat["geometry"])
        assert result_geom.area == pytest.approx(box(10, 10, 20, 20).area, rel=1e-3)

    def test_subtracts_disputed_areas(self, subunits_gdf, units_gdf, admin1_gdf, disputed_gdf):
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
            "subtract_disputed": ["Disputed Zone"],
        }
        feat = extract_remainder(dest, admin1_gdf, subunits_gdf, units_gdf, disputed_gdf)
        assert feat is not None
        result_geom = shape(feat["geometry"])
        # Disputed zone (12-14, 12-14) was subtracted — area should be less
        assert result_geom.area < box(10, 10, 20, 20).area

    def test_merges_disputed_areas(self, subunits_gdf, units_gdf, admin1_gdf, disputed_gdf):
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
            "merge_disputed": ["Disputed Zone"],
        }
        feat = extract_remainder(dest, admin1_gdf, subunits_gdf, units_gdf, disputed_gdf)
        assert feat is not None
        # Disputed zone already overlaps, so union should be >= original area
        result_geom = shape(feat["geometry"])
        assert result_geom.area >= box(10, 10, 20, 20).area


class TestExtractDisputedRemainder:
    def test_subtracts_disputed(self, subunits_gdf, units_gdf, admin1_gdf, disputed_gdf):
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
            "subtract_disputed": ["Disputed Zone"],
        }
        feat = extract_disputed_remainder(dest, admin1_gdf, subunits_gdf, units_gdf, disputed_gdf)
        assert feat is not None
        result_geom = shape(feat["geometry"])
        assert result_geom.area < box(10, 10, 20, 20).area

    def test_returns_full_when_no_subtract(self, subunits_gdf, units_gdf, admin1_gdf, disputed_gdf):
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
        feat = extract_disputed_remainder(dest, admin1_gdf, subunits_gdf, units_gdf, disputed_gdf)
        assert feat is not None
        result_geom = shape(feat["geometry"])
        assert result_geom.area == pytest.approx(box(10, 10, 20, 20).area, rel=1e-3)

    def test_returns_none_without_adm0(self, subunits_gdf, units_gdf, admin1_gdf, disputed_gdf):
        dest = {
            "tcc_index": 10,
            "name": "Test",
            "region": "Test",
            "iso_a2": None,
            "iso_a3": None,
            "iso_n3": None,
            "sovereign": "Test",
            "type": "country",
        }
        feat = extract_disputed_remainder(dest, admin1_gdf, subunits_gdf, units_gdf, disputed_gdf)
        assert feat is None
