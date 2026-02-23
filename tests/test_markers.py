"""Tests for src/markers.py — markers TopoJSON generator."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
import geopandas as gpd
from shapely.geometry import Point, Polygon, box


def _gdf(geoms: list, props: list[dict] | None = None) -> gpd.GeoDataFrame:
    """Build a GeoDataFrame with the given geometries and optional properties."""
    if props is None:
        props = [{"name": f"Feature {i}", "tcc_index": i + 1} for i in range(len(geoms))]
    return gpd.GeoDataFrame(props, geometry=geoms, crs="EPSG:4326")


# Synthetic geometries — chosen to be reliably above/below the 1000 km² threshold
# when projected to ESRI:54009.
# 5°×5° near equator ≈ 300 000 km²  (large)
LARGE_BOX = box(0.0, 0.0, 5.0, 5.0)
# 0.05°×0.05° near equator ≈ 30 km²  (small)
SMALL_BOX = box(0.0, 0.0, 0.05, 0.05)


# ---------------------------------------------------------------------------
# build_markers_collection — Points
# ---------------------------------------------------------------------------

class TestBuildCompactCollectionPoints:
    """Pre-existing Point geometries go directly into the point_features list."""

    def test_point_goes_to_point_features(self):
        from src.markers import build_markers_collection

        _, point_features = build_markers_collection(_gdf([Point(10.0, 20.0)]))
        assert len(point_features) == 1

    def test_polygon_collection_empty_for_point_input(self):
        from src.markers import build_markers_collection

        poly_coll, _ = build_markers_collection(_gdf([Point(10.0, 20.0)]))
        assert poly_coll["features"] == []

    def test_point_gets_marker_true(self):
        from src.markers import build_markers_collection

        _, point_features = build_markers_collection(_gdf([Point(10.0, 20.0)]))
        assert point_features[0]["properties"]["marker"] is True

    def test_point_geometry_type_preserved(self):
        from src.markers import build_markers_collection

        _, point_features = build_markers_collection(_gdf([Point(10.0, 20.0)]))
        assert point_features[0]["geometry"]["type"] == "Point"

    def test_point_coordinates_preserved(self):
        from src.markers import build_markers_collection

        _, point_features = build_markers_collection(_gdf([Point(-177.4, 28.2)]))
        coords = point_features[0]["geometry"]["coordinates"]
        assert coords[0] == pytest.approx(-177.4)
        assert coords[1] == pytest.approx(28.2)


# ---------------------------------------------------------------------------
# build_markers_collection — Small polygon (below threshold)
# ---------------------------------------------------------------------------

class TestBuildCompactCollectionSmallPolygon:
    """Polygons below AREA_THRESHOLD_KM2 are converted to centroid Points."""

    def test_small_polygon_goes_to_point_features(self):
        from src.markers import build_markers_collection

        _, point_features = build_markers_collection(_gdf([SMALL_BOX]))
        assert len(point_features) == 1

    def test_small_polygon_polygon_collection_empty(self):
        from src.markers import build_markers_collection

        poly_coll, _ = build_markers_collection(_gdf([SMALL_BOX]))
        assert poly_coll["features"] == []

    def test_small_polygon_becomes_point_geometry(self):
        from src.markers import build_markers_collection

        _, point_features = build_markers_collection(_gdf([SMALL_BOX]))
        assert point_features[0]["geometry"]["type"] == "Point"

    def test_small_polygon_gets_marker_true(self):
        from src.markers import build_markers_collection

        _, point_features = build_markers_collection(_gdf([SMALL_BOX]))
        assert point_features[0]["properties"]["marker"] is True

    def test_small_polygon_centroid_within_bounds(self):
        from src.markers import build_markers_collection

        _, point_features = build_markers_collection(_gdf([SMALL_BOX]))
        cx, cy = point_features[0]["geometry"]["coordinates"]
        assert 0.0 <= cx <= 0.05
        assert 0.0 <= cy <= 0.05

    def test_small_polygon_area_km2_stored(self):
        from src.markers import build_markers_collection

        _, point_features = build_markers_collection(_gdf([SMALL_BOX]))
        area = point_features[0]["properties"]["area_km2"]
        assert isinstance(area, float)
        assert area < 1000.0

    def test_small_polygon_area_km2_rounded(self):
        from src.markers import build_markers_collection

        _, point_features = build_markers_collection(_gdf([SMALL_BOX]))
        area = point_features[0]["properties"]["area_km2"]
        assert area == round(area, 1)


# ---------------------------------------------------------------------------
# build_markers_collection — Large polygon (above threshold)
# ---------------------------------------------------------------------------

class TestBuildCompactCollectionLargePolygon:
    """Polygons at or above AREA_THRESHOLD_KM2 are kept as polygons."""

    def test_large_polygon_goes_to_polygon_collection(self):
        from src.markers import build_markers_collection

        poly_coll, _ = build_markers_collection(_gdf([LARGE_BOX]))
        assert len(poly_coll["features"]) == 1

    def test_large_polygon_point_features_empty(self):
        from src.markers import build_markers_collection

        _, point_features = build_markers_collection(_gdf([LARGE_BOX]))
        assert point_features == []

    def test_large_polygon_geometry_type_preserved(self):
        from src.markers import build_markers_collection

        poly_coll, _ = build_markers_collection(_gdf([LARGE_BOX]))
        assert poly_coll["features"][0]["geometry"]["type"] == "Polygon"

    def test_large_polygon_gets_marker_false(self):
        from src.markers import build_markers_collection

        poly_coll, _ = build_markers_collection(_gdf([LARGE_BOX]))
        assert poly_coll["features"][0]["properties"]["marker"] is False

    def test_large_polygon_area_km2_above_threshold(self):
        from src.markers import build_markers_collection

        poly_coll, _ = build_markers_collection(_gdf([LARGE_BOX]))
        assert poly_coll["features"][0]["properties"]["area_km2"] >= 1000.0

    def test_large_polygon_area_km2_rounded(self):
        from src.markers import build_markers_collection

        poly_coll, _ = build_markers_collection(_gdf([LARGE_BOX]))
        area = poly_coll["features"][0]["properties"]["area_km2"]
        assert area == round(area, 1)


# ---------------------------------------------------------------------------
# build_markers_collection — Mixed collection
# ---------------------------------------------------------------------------

class TestBuildCompactCollectionMixed:
    """Mixed collection: large polygon + small polygon + pre-existing point."""

    def _mixed_gdf(self) -> gpd.GeoDataFrame:
        return _gdf(
            [LARGE_BOX, SMALL_BOX, Point(10.0, 20.0)],
            props=[
                {"name": "BigLand", "tcc_index": 1},
                {"name": "TinyIsland", "tcc_index": 2},
                {"name": "Midway", "tcc_index": 3},
            ],
        )

    def test_polygon_collection_is_feature_collection(self):
        from src.markers import build_markers_collection

        poly_coll, _ = build_markers_collection(self._mixed_gdf())
        assert poly_coll["type"] == "FeatureCollection"

    def test_one_polygon_in_collection(self):
        from src.markers import build_markers_collection

        poly_coll, _ = build_markers_collection(self._mixed_gdf())
        assert len(poly_coll["features"]) == 1
        assert poly_coll["features"][0]["geometry"]["type"] == "Polygon"

    def test_two_markers_in_point_features(self):
        from src.markers import build_markers_collection

        _, point_features = build_markers_collection(self._mixed_gdf())
        assert len(point_features) == 2
        assert all(f["geometry"]["type"] == "Point" for f in point_features)

    def test_all_markers_have_marker_true(self):
        from src.markers import build_markers_collection

        _, point_features = build_markers_collection(self._mixed_gdf())
        assert all(f["properties"]["marker"] is True for f in point_features)


# ---------------------------------------------------------------------------
# build_markers_collection — Edge cases
# ---------------------------------------------------------------------------

class TestBuildCompactCollectionEdgeCases:
    """Edge cases: empty geometry, property passthrough."""

    def test_empty_geometry_skipped(self):
        from src.markers import build_markers_collection

        empty = Polygon()
        poly_coll, point_features = build_markers_collection(_gdf([empty]))
        assert poly_coll["features"] == []
        assert point_features == []

    def test_empty_gdf_returns_empty_results(self):
        from src.markers import build_markers_collection

        empty_gdf = gpd.GeoDataFrame({"name": []}, geometry=[], crs="EPSG:4326")
        poly_coll, point_features = build_markers_collection(empty_gdf)
        assert poly_coll["features"] == []
        assert point_features == []

    def test_extra_properties_preserved_on_polygon(self):
        from src.markers import build_markers_collection

        props = [{"name": "BigLand", "region": "Asia", "tcc_index": 42, "iso_a3": "BGL"}]
        poly_coll, _ = build_markers_collection(_gdf([LARGE_BOX], props))
        p = poly_coll["features"][0]["properties"]
        assert p["name"] == "BigLand"
        assert p["region"] == "Asia"
        assert p["tcc_index"] == 42
        assert p["iso_a3"] == "BGL"


# ---------------------------------------------------------------------------
# NaN sanitisation
# ---------------------------------------------------------------------------

class TestNanPropertiesSanitized:
    """NaN from geopandas re-read must not appear in output JSON."""

    def test_nan_props_become_null_in_polygon_collection(self):
        import numpy as np
        from src.markers import build_markers_collection

        gdf = gpd.GeoDataFrame(
            [{"name": "BigLand", "tcc_index": 1, "iso_a2": np.nan, "iso_n3": np.nan}],
            geometry=[LARGE_BOX],
            crs="EPSG:4326",
        )
        poly_coll, _ = build_markers_collection(gdf)
        text = json.dumps(poly_coll)
        assert "NaN" not in text
        data = json.loads(text)
        assert data["features"][0]["properties"]["iso_a2"] is None
        assert data["features"][0]["properties"]["iso_n3"] is None

    def test_nan_props_become_null_in_point_features(self):
        import numpy as np
        from src.markers import build_markers_collection

        gdf = gpd.GeoDataFrame(
            [{"name": "TinyIsland", "tcc_index": 1, "iso_a2": np.nan}],
            geometry=[SMALL_BOX],
            crs="EPSG:4326",
        )
        _, point_features = build_markers_collection(gdf)
        text = json.dumps(point_features)
        assert "NaN" not in text
        data = json.loads(text)
        assert data[0]["properties"]["iso_a2"] is None


# ---------------------------------------------------------------------------
# inject_points
# ---------------------------------------------------------------------------

class TestQuantize:
    """Tests for _quantize()."""

    def test_roundtrip(self):
        """Quantized coords decoded with the same transform recover originals."""
        from src.markers import _quantize

        transform = {"scale": [0.0036, 0.0018], "translate": [-180.0, -90.0]}
        lon, lat = -147.7, -24.8
        qx, qy = _quantize(lon, lat, transform)
        sx, sy = transform["scale"]
        dx, dy = transform["translate"]
        assert qx * sx + dx == pytest.approx(lon, abs=0.005)
        assert qy * sy + dy == pytest.approx(lat, abs=0.005)

    def test_returns_integers(self):
        from src.markers import _quantize

        transform = {"scale": [0.0036, 0.0018], "translate": [-180.0, -90.0]}
        result = _quantize(0.0, 0.0, transform)
        assert all(isinstance(v, int) for v in result)

    def test_origin(self):
        """(0, 0) should map to roughly the centre of a world quantization grid."""
        from src.markers import _quantize

        transform = {"scale": [0.0036, 0.0018], "translate": [-180.0, -90.0]}
        qx, qy = _quantize(0.0, 0.0, transform)
        assert qx == round(180.0 / 0.0036)
        assert qy == round(90.0 / 0.0018)


class TestInjectPoints:
    """Tests for inject_points()."""

    def _minimal_topology(self, with_transform: bool = False) -> dict:
        topo: dict = {
            "type": "Topology",
            "arcs": [],
            "objects": {
                "polygons": {
                    "type": "GeometryCollection",
                    "geometries": [],
                }
            },
        }
        if with_transform:
            topo["transform"] = {"scale": [0.0036, 0.0018], "translate": [-180.0, -90.0]}
        return topo

    def test_adds_points_object(self, tmp_path):
        from src.markers import inject_points

        topo_path = tmp_path / "topo.json"
        topo_path.write_text(json.dumps(self._minimal_topology()))
        inject_points(topo_path, [
            {"type": "Feature", "properties": {"name": "Midway"}, "geometry": {"type": "Point", "coordinates": [-177.4, 28.2]}},
        ])

        assert "points" in json.loads(topo_path.read_text())["objects"]

    def test_coordinates_quantized_when_transform_present(self, tmp_path):
        from src.markers import inject_points

        topo_path = tmp_path / "topo.json"
        topo_path.write_text(json.dumps(self._minimal_topology(with_transform=True)))
        inject_points(topo_path, [
            {"type": "Feature", "properties": {}, "geometry": {"type": "Point", "coordinates": [-177.4, 28.2]}},
        ])

        data = json.loads(topo_path.read_text())
        coords = data["objects"]["points"]["geometries"][0]["coordinates"]
        # Must be integers (quantized), not raw floats
        assert all(isinstance(v, int) for v in coords)

    def test_coordinates_decode_correctly_via_transform(self, tmp_path):
        from src.markers import inject_points

        topo_path = tmp_path / "topo.json"
        topo = self._minimal_topology(with_transform=True)
        topo_path.write_text(json.dumps(topo))
        lon, lat = -177.4, 28.2
        inject_points(topo_path, [
            {"type": "Feature", "properties": {}, "geometry": {"type": "Point", "coordinates": [lon, lat]}},
        ])

        data = json.loads(topo_path.read_text())
        sx, sy = data["transform"]["scale"]
        dx, dy = data["transform"]["translate"]
        qx, qy = data["objects"]["points"]["geometries"][0]["coordinates"]
        assert qx * sx + dx == pytest.approx(lon, abs=0.005)
        assert qy * sy + dy == pytest.approx(lat, abs=0.005)

    def test_coordinates_raw_when_no_transform(self, tmp_path):
        from src.markers import inject_points

        topo_path = tmp_path / "topo.json"
        topo_path.write_text(json.dumps(self._minimal_topology(with_transform=False)))
        inject_points(topo_path, [
            {"type": "Feature", "properties": {}, "geometry": {"type": "Point", "coordinates": [-177.4, 28.2]}},
        ])

        coords = json.loads(topo_path.read_text())["objects"]["points"]["geometries"][0]["coordinates"]
        assert coords == pytest.approx([-177.4, 28.2])

    def test_point_properties_in_topology(self, tmp_path):
        from src.markers import inject_points

        topo_path = tmp_path / "topo.json"
        topo_path.write_text(json.dumps(self._minimal_topology()))
        inject_points(topo_path, [
            {"type": "Feature", "properties": {"name": "Midway", "tcc_index": 18}, "geometry": {"type": "Point", "coordinates": [0, 0]}},
        ])

        props = json.loads(topo_path.read_text())["objects"]["points"]["geometries"][0]["properties"]
        assert props["name"] == "Midway"
        assert props["tcc_index"] == 18

    def test_existing_objects_preserved(self, tmp_path):
        from src.markers import inject_points

        topo_path = tmp_path / "topo.json"
        topo_path.write_text(json.dumps(self._minimal_topology()))
        inject_points(topo_path, [])

        assert "polygons" in json.loads(topo_path.read_text())["objects"]

    def test_empty_point_features_writes_empty_collection(self, tmp_path):
        from src.markers import inject_points

        topo_path = tmp_path / "topo.json"
        topo_path.write_text(json.dumps(self._minimal_topology()))
        inject_points(topo_path, [])

        assert json.loads(topo_path.read_text())["objects"]["points"]["geometries"] == []

    def test_multiple_points(self, tmp_path):
        from src.markers import inject_points

        topo_path = tmp_path / "topo.json"
        topo_path.write_text(json.dumps(self._minimal_topology()))
        points = [
            {"type": "Feature", "properties": {"name": f"P{i}"}, "geometry": {"type": "Point", "coordinates": [float(i), 0.0]}}
            for i in range(5)
        ]
        inject_points(topo_path, points)

        assert len(json.loads(topo_path.read_text())["objects"]["points"]["geometries"]) == 5


# ---------------------------------------------------------------------------
# run_mapshaper
# ---------------------------------------------------------------------------

class TestRunMapshaper:
    """Tests for run_mapshaper()."""

    def test_success_does_not_raise(self, tmp_path):
        from src.markers import run_mapshaper

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            run_mapshaper(tmp_path / "in.geojson", tmp_path / "out.json")

        assert mock_run.called

    def test_nonzero_exit_raises_runtime_error(self, tmp_path):
        from src.markers import run_mapshaper

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="bad error")
            with pytest.raises(RuntimeError, match="mapshaper failed"):
                run_mapshaper(tmp_path / "in.geojson", tmp_path / "out.json")

    def test_stdout_printed(self, tmp_path, capsys):
        from src.markers import run_mapshaper

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="Wrote 1 file", stderr="")
            run_mapshaper(tmp_path / "in.geojson", tmp_path / "out.json")

        assert "Wrote 1 file" in capsys.readouterr().out

    def test_default_simplify_is_3pct(self, tmp_path):
        from src.markers import run_mapshaper

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            run_mapshaper(tmp_path / "in.geojson", tmp_path / "out.json")

        cmd = mock_run.call_args[0][0]
        assert "3%" in cmd

    def test_custom_simplify_param(self, tmp_path):
        from src.markers import run_mapshaper

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            run_mapshaper(tmp_path / "in.geojson", tmp_path / "out.json", simplify="7%")

        cmd = mock_run.call_args[0][0]
        assert "7%" in cmd

    def test_command_contains_simplify_flags(self, tmp_path):
        from src.markers import run_mapshaper

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            run_mapshaper(tmp_path / "in.geojson", tmp_path / "out.json")

        cmd = mock_run.call_args[0][0]
        assert "weighted" in cmd
        assert "keep-shapes" in cmd
        assert "format=topojson" in cmd

    def test_command_contains_input_and_output_paths(self, tmp_path):
        from src.markers import run_mapshaper

        inp = tmp_path / "in.geojson"
        out = tmp_path / "out.json"

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            run_mapshaper(inp, out)

        cmd = mock_run.call_args[0][0]
        assert str(inp) in cmd
        assert str(out) in cmd


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

class TestMain:
    """Tests for the main() entry point."""

    def test_missing_input_raises_file_not_found(self, tmp_path):
        from src import markers as cmp

        with patch.object(cmp, "MERGED_GEOJSON", tmp_path / "nonexistent.geojson"):
            with pytest.raises(FileNotFoundError, match="not found"):
                cmp.main()

    def test_full_pipeline_writes_markers_geojson(self, tmp_path):
        from src import markers as cmp

        gdf = gpd.GeoDataFrame(
            [{"name": "BigLand", "region": "Asia", "tcc_index": 1}],
            geometry=[LARGE_BOX],
            crs="EPSG:4326",
        )
        merged = tmp_path / "merged.geojson"
        gdf.to_file(merged, driver="GeoJSON")

        markers_geojson = tmp_path / "merged-markers.geojson"
        markers_topojson = tmp_path / "tcc-330-markers.json"

        minimal_topo = json.dumps({
            "type": "Topology", "arcs": [],
            "objects": {"polygons": {"type": "GeometryCollection", "geometries": []}},
        })

        def fake_run(cmd, **kwargs):
            markers_topojson.write_text(minimal_topo)
            return MagicMock(returncode=0, stdout="", stderr="")

        with (
            patch.object(cmp, "MERGED_GEOJSON", merged),
            patch.object(cmp, "MARKERS_GEOJSON", markers_geojson),
            patch.object(cmp, "MARKERS_TOPOJSON", markers_topojson),
            patch.object(cmp, "OUTPUT_DIR", tmp_path),
            patch("subprocess.run", side_effect=fake_run),
        ):
            cmp.main()

        # Compact GeoJSON must exist and contain only polygon features
        assert markers_geojson.exists()
        data = json.loads(markers_geojson.read_text())
        assert data["type"] == "FeatureCollection"
        assert len(data["features"]) == 1

    def test_full_pipeline_injects_points_into_topology(self, tmp_path):
        from src import markers as cmp

        # Mix: one large polygon + one tiny polygon (becomes marker)
        gdf = gpd.GeoDataFrame(
            [
                {"name": "BigLand", "region": "Asia", "tcc_index": 1},
                {"name": "TinyIsland", "region": "Caribbean", "tcc_index": 2},
            ],
            geometry=[LARGE_BOX, SMALL_BOX],
            crs="EPSG:4326",
        )
        merged = tmp_path / "merged.geojson"
        gdf.to_file(merged, driver="GeoJSON")

        markers_geojson = tmp_path / "merged-markers.geojson"
        markers_topojson = tmp_path / "tcc-330-markers.json"

        minimal_topo = json.dumps({
            "type": "Topology", "arcs": [],
            "objects": {"polygons": {"type": "GeometryCollection", "geometries": []}},
        })

        def fake_run(cmd, **kwargs):
            markers_topojson.write_text(minimal_topo)
            return MagicMock(returncode=0, stdout="", stderr="")

        with (
            patch.object(cmp, "MERGED_GEOJSON", merged),
            patch.object(cmp, "MARKERS_GEOJSON", markers_geojson),
            patch.object(cmp, "MARKERS_TOPOJSON", markers_topojson),
            patch.object(cmp, "OUTPUT_DIR", tmp_path),
            patch("subprocess.run", side_effect=fake_run),
        ):
            cmp.main()

        # Points object must have been injected
        topo = json.loads(markers_topojson.read_text())
        assert "points" in topo["objects"]
        assert len(topo["objects"]["points"]["geometries"]) == 1
        assert topo["objects"]["points"]["geometries"][0]["type"] == "Point"

    def test_small_polygon_only_in_points_not_geojson(self, tmp_path):
        from src import markers as cmp

        gdf = gpd.GeoDataFrame(
            [{"name": "TinyIsland", "region": "Caribbean", "tcc_index": 1}],
            geometry=[SMALL_BOX],
            crs="EPSG:4326",
        )
        merged = tmp_path / "merged.geojson"
        gdf.to_file(merged, driver="GeoJSON")

        markers_geojson = tmp_path / "merged-markers.geojson"
        markers_topojson = tmp_path / "tcc-330-markers.json"

        minimal_topo = json.dumps({
            "type": "Topology", "arcs": [],
            "objects": {"polygons": {"type": "GeometryCollection", "geometries": []}},
        })

        def fake_run(cmd, **kwargs):
            markers_topojson.write_text(minimal_topo)
            return MagicMock(returncode=0, stdout="", stderr="")

        with (
            patch.object(cmp, "MERGED_GEOJSON", merged),
            patch.object(cmp, "MARKERS_GEOJSON", markers_geojson),
            patch.object(cmp, "MARKERS_TOPOJSON", markers_topojson),
            patch.object(cmp, "OUTPUT_DIR", tmp_path),
            patch("subprocess.run", side_effect=fake_run),
        ):
            cmp.main()

        # The markers GeoJSON sent to mapshaper must have no features (tiny → marker)
        poly_data = json.loads(markers_geojson.read_text())
        assert poly_data["features"] == []
        # But the topology must have it as a point
        topo = json.loads(markers_topojson.read_text())
        assert len(topo["objects"]["points"]["geometries"]) == 1


    def test_simplify_env_var_passed_to_mapshaper(self, tmp_path, monkeypatch):
        from src import markers as cmp

        gdf = gpd.GeoDataFrame(
            [{"name": "BigLand", "region": "Asia", "tcc_index": 1}],
            geometry=[LARGE_BOX],
            crs="EPSG:4326",
        )
        merged = tmp_path / "merged.geojson"
        gdf.to_file(merged, driver="GeoJSON")

        markers_geojson = tmp_path / "merged-markers.geojson"
        markers_topojson = tmp_path / "tcc-330-markers.json"
        minimal_topo = json.dumps({
            "type": "Topology", "arcs": [],
            "objects": {"polygons": {"type": "GeometryCollection", "geometries": []}},
        })

        called_with: list[list[str]] = []

        def fake_run(cmd, **kwargs):
            called_with.append(cmd)
            markers_topojson.write_text(minimal_topo)
            return MagicMock(returncode=0, stdout="", stderr="")

        monkeypatch.setenv("SIMPLIFY", "5%")

        with (
            patch.object(cmp, "MERGED_GEOJSON", merged),
            patch.object(cmp, "MARKERS_GEOJSON", markers_geojson),
            patch.object(cmp, "MARKERS_TOPOJSON", markers_topojson),
            patch.object(cmp, "OUTPUT_DIR", tmp_path),
            patch("subprocess.run", side_effect=fake_run),
        ):
            cmp.main()

        assert any("5%" in " ".join(cmd) for cmd in called_with)


# ---------------------------------------------------------------------------
# _sanitize
# ---------------------------------------------------------------------------

class TestSanitize:
    """Tests for the _sanitize helper."""

    def test_none_passthrough(self):
        from src.markers import _sanitize

        assert _sanitize(None) is None

    def test_string_passthrough(self):
        from src.markers import _sanitize

        assert _sanitize("hello") == "hello"

    def test_python_int_passthrough(self):
        from src.markers import _sanitize

        assert _sanitize(42) == 42

    def test_python_float_passthrough(self):
        from src.markers import _sanitize

        assert _sanitize(3.14) == pytest.approx(3.14)

    def test_nan_becomes_none(self):
        from src.markers import _sanitize

        assert _sanitize(float("nan")) is None

    def test_inf_becomes_none(self):
        from src.markers import _sanitize

        assert _sanitize(float("inf")) is None
        assert _sanitize(float("-inf")) is None

    def test_numpy_float_nan_becomes_none(self):
        import numpy as np
        from src.markers import _sanitize

        assert _sanitize(np.float64("nan")) is None

    def test_numpy_float_valid_returns_python_float(self):
        import numpy as np
        from src.markers import _sanitize

        result = _sanitize(np.float64(1.5))
        assert result == pytest.approx(1.5)
        assert isinstance(result, float)

    def test_numpy_int_returns_python_int(self):
        import numpy as np
        from src.markers import _sanitize

        result = _sanitize(np.int64(7))
        assert result == 7
        assert isinstance(result, int)

    def test_numpy_bool_returns_python_bool(self):
        import numpy as np
        from src.markers import _sanitize

        assert _sanitize(np.bool_(True)) is True
        assert isinstance(_sanitize(np.bool_(True)), bool)


# ---------------------------------------------------------------------------
# _km2_to_m2
# ---------------------------------------------------------------------------

class TestKm2ToM2:
    def test_one_km2(self):
        from src.markers import _km2_to_m2

        assert _km2_to_m2(1.0) == pytest.approx(1_000_000.0)

    def test_zero(self):
        from src.markers import _km2_to_m2

        assert _km2_to_m2(0.0) == pytest.approx(0.0)

    def test_large(self):
        from src.markers import _km2_to_m2

        assert _km2_to_m2(1000.0) == pytest.approx(1_000_000_000.0)
