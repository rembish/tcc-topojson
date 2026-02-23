"""Tests for src/utils.py — GIS utility functions."""

from __future__ import annotations

import pytest
from shapely.geometry import MultiPolygon, Point, Polygon, box

from src.utils import (
    dissolve_geometries,
    extract_polygons_by_bbox,
    get_country_geom,
    make_properties,
    subtract_polygons_by_bbox,
    to_feature,
)


class TestDissolveGeometries:
    def test_dissolves_two_polygons(self):
        p1 = box(0, 0, 1, 1)
        p2 = box(1, 0, 2, 1)
        result = dissolve_geometries([p1, p2])
        assert not result.is_empty
        assert result.area == pytest.approx(2.0)

    def test_single_polygon(self):
        p = box(0, 0, 1, 1)
        result = dissolve_geometries([p])
        assert result.equals(p)


class TestExtractPolygonsByBbox:
    def test_extracts_matching_polygon(self):
        # MultiPolygon: one poly inside bbox, one outside
        p_in = box(0, 0, 1, 1)
        p_out = box(10, 10, 11, 11)
        mp = MultiPolygon([p_in, p_out])
        result = extract_polygons_by_bbox(mp, (-1, -1, 5, 5))
        assert result is not None
        assert result.equals(p_in)

    def test_returns_none_when_no_match(self):
        p = box(10, 10, 11, 11)
        result = extract_polygons_by_bbox(p, (0, 0, 5, 5))
        assert result is None

    def test_single_polygon_in_bbox(self):
        p = box(0, 0, 2, 2)
        result = extract_polygons_by_bbox(p, (-1, -1, 5, 5))
        assert result is not None
        assert result.equals(p)

    def test_returns_multipolygon_for_multiple_matches(self):
        p1 = box(0, 0, 1, 1)
        p2 = box(2, 0, 3, 1)
        mp = MultiPolygon([p1, p2])
        result = extract_polygons_by_bbox(mp, (-1, -1, 5, 5))
        assert isinstance(result, MultiPolygon)
        assert len(list(result.geoms)) == 2

    def test_fallback_intersection_when_centroid_outside(self):
        # Large polygon whose centroid is outside the small bbox, but intersects
        p = box(-5, -5, 2, 2)
        result = extract_polygons_by_bbox(p, (0, 0, 1, 1))
        # Falls back to intersection check → should still find it
        assert result is not None

    def test_non_polygon_returns_none(self):
        pt = Point(1, 1)
        result = extract_polygons_by_bbox(pt, (0, 0, 2, 2))
        assert result is None


class TestSubtractPolygonsByBbox:
    def test_removes_matching_polygon(self):
        p_in = box(0, 0, 1, 1)
        p_out = box(10, 10, 11, 11)
        mp = MultiPolygon([p_in, p_out])
        result = subtract_polygons_by_bbox(mp, (-1, -1, 5, 5))
        assert result is not None
        assert result.equals(p_out)

    def test_returns_none_when_all_removed(self):
        p = box(0, 0, 1, 1)
        result = subtract_polygons_by_bbox(p, (-1, -1, 5, 5))
        assert result is None

    def test_returns_original_for_non_polygon(self):
        pt = Point(1, 1)
        result = subtract_polygons_by_bbox(pt, (0, 0, 2, 2))
        assert result is pt

    def test_no_match_returns_all(self):
        p1 = box(0, 0, 1, 1)
        p2 = box(2, 0, 3, 1)
        mp = MultiPolygon([p1, p2])
        result = subtract_polygons_by_bbox(mp, (100, 100, 110, 110))
        assert isinstance(result, MultiPolygon)
        assert len(list(result.geoms)) == 2


class TestToFeature:
    def test_returns_feature_dict(self):
        geom = box(0, 0, 1, 1)
        props = {"name": "Test", "tcc_index": 1}
        feat = to_feature(geom, props)
        assert feat["type"] == "Feature"
        assert feat["properties"] == props
        assert "geometry" in feat
        assert feat["geometry"]["type"] == "Polygon"

    def test_geometry_is_serializable(self):
        import json

        geom = Point(5, 5)
        feat = to_feature(geom, {"x": 1})
        # Should not raise
        json.dumps(feat)


class TestMakeProperties:
    def test_standard_fields(self):
        dest = {
            "tcc_index": 42,
            "name": "Testland",
            "region": "Test Region",
            "iso_a2": "TS",
            "iso_a3": "TST",
            "iso_n3": 999,
            "sovereign": "Testland",
            "type": "country",
        }
        props = make_properties(dest)
        assert props["tcc_index"] == 42
        assert props["name"] == "Testland"
        assert props["iso_a2"] == "TS"
        assert props["type"] == "country"

    def test_optional_fields_default_to_none(self):
        dest = {
            "tcc_index": 1,
            "name": "Nowhere",
            "region": "Pacific Ocean",
            "sovereign": "France",
            "type": "territory",
        }
        props = make_properties(dest)
        assert props["iso_a2"] is None
        assert props["iso_a3"] is None
        assert props["iso_n3"] is None


class TestGetCountryGeom:
    def test_finds_by_adm0_a3(self, subunits_gdf, units_gdf):
        result = get_country_geom("TST", subunits_gdf, units_gdf)
        assert result is not None
        assert not result.is_empty

    def test_returns_none_for_unknown_code(self, subunits_gdf, units_gdf):
        result = get_country_geom("ZZZ", subunits_gdf, units_gdf)
        assert result is None

    def test_dissolves_multiple_rows(self, units_gdf):
        """When multiple rows share an ADM0_A3, they should be dissolved."""
        import geopandas as gpd

        double_gdf = gpd.GeoDataFrame(
            {
                "ADM0_A3": ["TST", "TST"],
                "SU_A3": ["TST", "TST"],
                "GU_A3": ["TST", "TST"],
                "ISO_A3": ["TST", "TST"],
            },
            geometry=[box(0, 0, 1, 1), box(1, 0, 2, 1)],
            crs="EPSG:4326",
        )
        empty = units_gdf.iloc[0:0]
        result = get_country_geom("TST", double_gdf, empty)
        assert result is not None
        assert result.area == pytest.approx(2.0)
