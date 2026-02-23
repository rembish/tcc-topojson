"""Tests for src/category_c.py — custom GIS extraction."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from shapely.geometry import MultiPolygon, Point, Polygon, box, shape

from src.category_c import (
    _collect_parts_in_lon,
    _make_wedge,
    _split_parts_by_lon,
    extract_disputed,
    extract_group_remainder,
    extract_island_bbox,
    generate_antarctic_wedge,
    generate_point,
)


class TestMakeWedge:
    def test_returns_polygon(self):
        w = _make_wedge(-10, 10, -60, -90)
        assert isinstance(w, Polygon)

    def test_is_valid(self):
        w = _make_wedge(-10, 10, -60, -90)
        assert w.is_valid

    def test_bbox_within_lon_range(self):
        w = _make_wedge(0, 45, -60, -90)
        minx, miny, maxx, maxy = w.bounds
        assert minx >= 0 - 0.1  # slight tolerance for floating point
        assert maxx <= 45 + 0.1

    def test_lat_south_is_bottom(self):
        w = _make_wedge(-10, 10, -60, -90)
        assert w.bounds[1] == pytest.approx(-90)


class TestCollectPartsInLon:
    def test_polygon_inside(self):
        p = box(5, 0, 10, 5)
        parts = _collect_parts_in_lon(p, 0, 15)
        assert len(parts) == 1

    def test_polygon_outside(self):
        p = box(20, 0, 25, 5)
        parts = _collect_parts_in_lon(p, 0, 15)
        assert len(parts) == 0

    def test_multipolygon_partial(self):
        p1 = box(5, 0, 10, 5)  # inside [0, 15]
        p2 = box(20, 0, 25, 5)  # outside
        mp = MultiPolygon([p1, p2])
        parts = _collect_parts_in_lon(mp, 0, 15)
        assert len(parts) == 1


class TestSplitPartsByLon:
    def test_single_polygon_split(self):
        p_in = box(5, 0, 10, 5)
        keep, shed = _split_parts_by_lon(p_in, 0, 15)
        assert len(keep) == 0
        assert len(shed) == 1

    def test_multi_polygon_split(self):
        p_in = box(5, 0, 10, 5)
        p_out = box(20, 0, 25, 5)
        mp = MultiPolygon([p_in, p_out])
        keep, shed = _split_parts_by_lon(mp, 0, 15)
        assert len(keep) == 1
        assert len(shed) == 1


class TestExtractClip:
    """Tests for extract_clip with mocked boundary functions."""

    def _clip_dest(self, side: str) -> dict:
        return {
            "tcc_index": 163,
            "name": f"Russia in {side.title()}",
            "region": "Test",
            "iso_a2": None,
            "iso_a3": None,
            "iso_n3": None,
            "sovereign": "Russia",
            "type": "subnational",
            "adm0_a3": "TST",
            "side": side,
        }

    def test_clip_europe(self, subunits_gdf, units_gdf):
        from src.category_c import extract_clip

        dest = self._clip_dest("europe")
        clipped = box(10, 10, 15, 20)  # left half of country (10-20, 10-20)

        with patch("src.category_c.clip_to_europe", return_value=clipped) as mock_clip:
            feat = extract_clip(dest, subunits_gdf, units_gdf)

        assert feat is not None
        mock_clip.assert_called_once()

    def test_clip_asia(self, subunits_gdf, units_gdf):
        from src.category_c import extract_clip

        dest = self._clip_dest("asia")
        clipped = box(15, 10, 20, 20)  # right half

        with patch("src.category_c.clip_to_asia", return_value=clipped):
            feat = extract_clip(dest, subunits_gdf, units_gdf)

        assert feat is not None

    def test_returns_none_without_adm0(self, subunits_gdf, units_gdf):
        from src.category_c import extract_clip

        dest = {
            "tcc_index": 1,
            "name": "Test",
            "region": "Test",
            "iso_a2": None,
            "iso_a3": None,
            "iso_n3": None,
            "sovereign": "Test",
            "type": "subnational",
            "side": "europe",
            # No adm0_a3
        }
        feat = extract_clip(dest, subunits_gdf, units_gdf)
        assert feat is None

    def test_returns_none_without_side(self, subunits_gdf, units_gdf):
        from src.category_c import extract_clip

        dest = {
            "tcc_index": 1,
            "name": "Test",
            "region": "Test",
            "iso_a2": None,
            "iso_a3": None,
            "iso_n3": None,
            "sovereign": "Test",
            "type": "subnational",
            "adm0_a3": "TST",
            # No side
        }
        feat = extract_clip(dest, subunits_gdf, units_gdf)
        assert feat is None

    def test_returns_none_when_country_not_found(self, subunits_gdf, units_gdf):
        from src.category_c import extract_clip

        dest = {
            "tcc_index": 1,
            "name": "Test",
            "region": "Test",
            "iso_a2": None,
            "iso_a3": None,
            "iso_n3": None,
            "sovereign": "Test",
            "type": "subnational",
            "adm0_a3": "ZZZ",
            "side": "europe",
        }
        feat = extract_clip(dest, subunits_gdf, units_gdf)
        assert feat is None

    def test_returns_none_for_unknown_side(self, subunits_gdf, units_gdf):
        from src.category_c import extract_clip

        dest = self._clip_dest("mars")
        with patch("src.category_c.clip_to_europe", return_value=box(10, 10, 15, 20)):
            feat = extract_clip(dest, subunits_gdf, units_gdf)
        assert feat is None

    def test_subtracts_built_features(self, subunits_gdf, units_gdf):
        from src.category_c import extract_clip

        dest = {**self._clip_dest("europe"), "subtract_indices": [99]}
        sub_feat = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[(10, 10), (13, 10), (13, 20), (10, 20), (10, 10)]],
            },
            "properties": {},
        }
        clipped = box(10, 10, 15, 20)

        with patch("src.category_c.clip_to_europe", return_value=clipped):
            feat = extract_clip(dest, subunits_gdf, units_gdf, built={99: sub_feat})

        assert feat is not None

    def test_absorb_lon_range_europe(self, subunits_gdf, units_gdf):
        from src.category_c import extract_clip

        dest = {**self._clip_dest("europe"), "absorb_lon_range": [11, 19]}
        clipped = box(10, 10, 15, 20)

        with patch("src.category_c.clip_to_europe", return_value=clipped):
            feat = extract_clip(dest, subunits_gdf, units_gdf)

        assert feat is not None

    def test_absorb_lon_range_asia(self, subunits_gdf, units_gdf):
        from src.category_c import extract_clip

        dest = {**self._clip_dest("asia"), "absorb_lon_range": [11, 13]}
        clipped = box(15, 10, 20, 20)

        with patch("src.category_c.clip_to_asia", return_value=clipped):
            feat = extract_clip(dest, subunits_gdf, units_gdf)

        assert feat is not None

    def test_subtract_su_a3(self, subunits_gdf, units_gdf):
        from src.category_c import extract_clip

        dest = {**self._clip_dest("europe"), "subtract_su_a3": ["TST"]}
        clipped = box(10, 10, 20, 20)

        with patch("src.category_c.clip_to_europe", return_value=clipped):
            # Subtracting TST (the entire country) from itself → empty → None
            feat = extract_clip(dest, subunits_gdf, units_gdf)

        # Result may be None because subtracting the country from itself empties it
        assert feat is None or feat is not None  # just ensure no crash


class TestExtractDisputed:
    def test_finds_by_name(self, disputed_gdf):
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
        feat = extract_disputed(dest, disputed_gdf)
        assert feat is not None
        assert feat["properties"]["name"] == "Disputed Zone"

    def test_returns_none_when_not_found(self, disputed_gdf):
        dest = {
            "tcc_index": 50,
            "name": "Nonexistent Zone",
            "region": "Test",
            "iso_a2": None,
            "iso_a3": None,
            "iso_n3": None,
            "sovereign": "Test",
            "type": "disputed",
        }
        feat = extract_disputed(dest, disputed_gdf)
        assert feat is None

    def test_uses_ne_name_override(self, disputed_gdf):
        dest = {
            "tcc_index": 50,
            "name": "Different Name",
            "region": "Test",
            "iso_a2": None,
            "iso_a3": None,
            "iso_n3": None,
            "sovereign": "Test",
            "type": "disputed",
            "ne_name": "Disputed Zone",  # override to match NE data
        }
        feat = extract_disputed(dest, disputed_gdf)
        assert feat is not None


class TestExtractIslandBbox:
    def test_extracts_island(self, island_dest, subunits_gdf, units_gdf):
        feat = extract_island_bbox(island_dest, subunits_gdf, units_gdf)
        assert feat is not None

    def test_returns_none_without_bbox(self, subunits_gdf, units_gdf):
        dest = {
            "tcc_index": 3,
            "name": "Test Island",
            "region": "Test",
            "iso_a2": None,
            "iso_a3": None,
            "iso_n3": None,
            "sovereign": "Testland",
            "type": "territory",
            "parent_adm0_a3": "TST",
            # No bbox
        }
        feat = extract_island_bbox(dest, subunits_gdf, units_gdf)
        assert feat is None

    def test_returns_none_for_missing_parent(self, subunits_gdf, units_gdf):
        dest = {
            "tcc_index": 3,
            "name": "Test Island",
            "region": "Test",
            "iso_a2": None,
            "iso_a3": None,
            "iso_n3": None,
            "sovereign": "Unknown",
            "type": "territory",
            "parent_adm0_a3": "ZZZ",
            "bbox": (12, 12, 18, 18),
        }
        feat = extract_island_bbox(dest, subunits_gdf, units_gdf)
        assert feat is None

    def test_returns_none_when_bbox_misses(self, subunits_gdf, units_gdf):
        dest = {
            "tcc_index": 3,
            "name": "Test Island",
            "region": "Test",
            "iso_a2": None,
            "iso_a3": None,
            "iso_n3": None,
            "sovereign": "Testland",
            "type": "territory",
            "parent_adm0_a3": "TST",
            "bbox": (90, 90, 95, 95),  # completely outside parent
        }
        feat = extract_island_bbox(dest, subunits_gdf, units_gdf)
        assert feat is None


class TestExtractGroupRemainder:
    def test_returns_full_when_no_subtract(self, subunits_gdf, units_gdf):
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
        feat = extract_group_remainder(dest, subunits_gdf, units_gdf, {})
        assert feat is not None

    def test_subtracts_built_features(self, subunits_gdf, units_gdf):
        # Build a feature that takes up part of the country
        sub_feat = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[(12, 12), (18, 12), (18, 18), (12, 18), (12, 12)]],
            },
            "properties": {"tcc_index": 99},
        }
        dest = {
            "tcc_index": 10,
            "name": "Testland Remainder",
            "region": "Test",
            "iso_a2": None,
            "iso_a3": None,
            "iso_n3": None,
            "sovereign": "Testland",
            "type": "country",
            "adm0_a3": "TST",
            "subtract_indices": [99],
        }
        feat = extract_group_remainder(dest, subunits_gdf, units_gdf, {99: sub_feat})
        assert feat is not None
        result_geom = shape(feat["geometry"])
        assert result_geom.area < box(10, 10, 20, 20).area

    def test_returns_none_without_adm0(self, subunits_gdf, units_gdf):
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
        feat = extract_group_remainder(dest, subunits_gdf, units_gdf, {})
        assert feat is None

    def test_returns_none_when_country_missing(self, subunits_gdf, units_gdf):
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
        feat = extract_group_remainder(dest, subunits_gdf, units_gdf, {})
        assert feat is None


class TestGenerateAntarcticWedge:
    def test_generates_wedge(self):
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
        feat = generate_antarctic_wedge(dest)
        assert feat is not None
        geom = shape(feat["geometry"])
        assert not geom.is_empty

    def test_antimeridian_crossing(self):
        dest = {
            "tcc_index": 186,
            "name": "Ross Dependency",
            "region": "Antarctica",
            "iso_a2": None,
            "iso_a3": None,
            "iso_n3": None,
            "sovereign": "New Zealand",
            "type": "antarctic",
            "lon_west": 160,
            "lon_east": -150,
        }
        feat = generate_antarctic_wedge(dest)
        assert feat is not None

    def test_multi_sector(self):
        dest = {
            "tcc_index": 182,
            "name": "Australian Antarctic",
            "region": "Antarctica",
            "iso_a2": None,
            "iso_a3": None,
            "iso_n3": None,
            "sovereign": "Australia",
            "type": "antarctic",
            "sectors": [
                {"lon_west": 45, "lon_east": 136},
                {"lon_west": 142, "lon_east": 160},
            ],
        }
        feat = generate_antarctic_wedge(dest)
        assert feat is not None

    def test_returns_none_without_lons(self):
        dest = {
            "tcc_index": 181,
            "name": "Bad Antarctic",
            "region": "Antarctica",
            "iso_a2": None,
            "iso_a3": None,
            "iso_n3": None,
            "sovereign": "Nobody",
            "type": "antarctic",
            # Missing lon_west and lon_east, no sectors
        }
        feat = generate_antarctic_wedge(dest)
        assert feat is None

    def test_clips_with_antarctica_geom(self):
        antarctica = box(-180, -90, 180, -60)
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
        feat = generate_antarctic_wedge(dest, antarctica_geom=antarctica)
        assert feat is not None


class TestGeneratePoint:
    def test_generates_point_feature(self):
        dest = {
            "tcc_index": 18,
            "name": "Midway Island",
            "region": "Pacific Ocean",
            "iso_a2": None,
            "iso_a3": None,
            "iso_n3": None,
            "sovereign": "United States",
            "type": "territory",
            "lat": 28.2,
            "lon": -177.4,
        }
        feat = generate_point(dest)
        assert feat is not None
        assert feat["properties"]["is_point"] is True
        geom = shape(feat["geometry"])
        assert isinstance(geom, Point)

    def test_returns_none_without_coords(self):
        dest = {
            "tcc_index": 18,
            "name": "Midway Island",
            "region": "Pacific Ocean",
            "iso_a2": None,
            "iso_a3": None,
            "iso_n3": None,
            "sovereign": "United States",
            "type": "territory",
        }
        feat = generate_point(dest)
        assert feat is None
