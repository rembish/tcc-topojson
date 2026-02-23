"""Markers TopoJSON generator — replaces tiny polygons with centroid Points.

Pipeline:
1. Read output/merged.geojson (full-detail GeoJSON from build step)
2. Project to ESRI:54009 (Mollweide equal-area) to compute area_km2
3. Classify each feature:
   - Already a Point → keep as-is
   - Polygon with area_km2 < AREA_THRESHOLD_KM2 → replace with centroid Point, mark marker=True
   - Polygon with area_km2 >= AREA_THRESHOLD_KM2 → keep polygon as-is
4. Write output/merged-markers.geojson  (polygons only — points kept separate)
5. Run mapshaper to produce output/tcc-330-markers.json
6. Inject point markers back into the TopoJSON as a second object

Run with: python -m src.markers
"""

from __future__ import annotations

import json
import math
import os
import subprocess
from pathlib import Path
from typing import Any

import geopandas as gpd
from shapely.geometry import Point, mapping

AREA_THRESHOLD_KM2: float = 1000.0

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"
MERGED_GEOJSON = OUTPUT_DIR / "merged.geojson"
MARKERS_GEOJSON = OUTPUT_DIR / "merged-markers.geojson"
MARKERS_TOPOJSON = OUTPUT_DIR / "tcc-330-markers.json"


def _km2_to_m2(km2: float) -> float:
    return km2 * 1_000_000.0


def _sanitize(value: Any) -> Any:
    """Convert numpy scalars and NaN/Inf to JSON-safe Python types.

    geopandas fills missing properties with numpy NaN, which json.dump
    serialises as the bare token ``NaN`` — invalid JSON.  This converts
    every value to a plain Python type before serialisation.
    """
    if hasattr(value, "item"):  # numpy scalar → Python native
        value = value.item()
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    return value


def build_markers_collection(
    gdf: gpd.GeoDataFrame,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Classify and transform features.

    Args:
        gdf: GeoDataFrame loaded from merged.geojson (EPSG:4326).

    Returns:
        A 2-tuple of:
        - polygon_collection: GeoJSON FeatureCollection containing only the
          polygon features that exceed the area threshold (safe to pass to
          mapshaper for simplification).
        - point_features: list of GeoJSON Feature dicts for features that are
          already Points or were converted to centroid Points (must be stitched
          back into the TopoJSON after mapshaper runs — mapshaper splits mixed
          collections into separate objects, which makes the output fragile).
    """
    # Project to equal-area CRS for accurate area computation
    gdf_ea = gdf.to_crs("ESRI:54009")

    n_markers = 0
    n_polygons = 0
    polygon_features: list[dict[str, Any]] = []
    point_features: list[dict[str, Any]] = []

    for idx, row in gdf.iterrows():
        geom_wgs = row.geometry
        geom_ea = gdf_ea.loc[idx, "geometry"]
        props: dict[str, Any] = {k: _sanitize(v) for k, v in row.items() if k != "geometry"}

        if geom_wgs is None or geom_wgs.is_empty:
            # Degenerate — skip
            continue

        if geom_wgs.geom_type == "Point":
            # Already a point marker from build step (Midway, Wake, etc.)
            props["marker"] = True
            point_features.append(
                {"type": "Feature", "properties": props, "geometry": mapping(geom_wgs)}
            )
            n_markers += 1

        else:
            # Polygon or MultiPolygon — check area
            area_km2 = geom_ea.area / 1_000_000.0  # m² → km²

            if area_km2 < AREA_THRESHOLD_KM2:
                # Replace with centroid point
                centroid: Point = geom_wgs.centroid
                props["marker"] = True
                props["area_km2"] = round(area_km2, 1)
                point_features.append(
                    {"type": "Feature", "properties": props, "geometry": mapping(centroid)}
                )
                n_markers += 1
            else:
                # Keep as polygon
                props["marker"] = False
                props["area_km2"] = round(area_km2, 1)
                polygon_features.append(
                    {"type": "Feature", "properties": props, "geometry": mapping(geom_wgs)}
                )
                n_polygons += 1

    polygon_collection: dict[str, Any] = {
        "type": "FeatureCollection",
        "features": polygon_features,
    }

    print(f"  Polygons kept:          {n_polygons}")
    print(f"  Converted to markers:   {n_markers}")
    print(f"  Total features:         {n_polygons + n_markers}")

    return polygon_collection, point_features


def run_mapshaper(input_path: Path, output_path: Path, simplify: str = "3%") -> None:
    """Run mapshaper to simplify and convert to TopoJSON.

    Args:
        input_path: Path to input GeoJSON.
        output_path: Path for output TopoJSON.
        simplify: Mapshaper simplification percentage, e.g. ``"3%"``.
            Override via the ``SIMPLIFY`` environment variable.
    """
    cmd = [
        "npx",
        "mapshaper",
        str(input_path),
        "-simplify",
        simplify,
        "weighted",
        "keep-shapes",
        "-o",
        "format=topojson",
        str(output_path),
        "quantization=1e5",
    ]
    print(f"\nRunning mapshaper: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  mapshaper stderr:\n{result.stderr}")
        msg = f"mapshaper failed with exit code {result.returncode}"
        raise RuntimeError(msg)
    if result.stdout:
        print(result.stdout.strip())


def _quantize(lon: float, lat: float, transform: dict[str, Any]) -> list[int]:
    """Convert WGS84 coordinates to quantized integers matching the topology transform.

    TopoJSON's ``transform`` encodes coordinates as integers:
        lon = quantized_x * scale[0] + translate[0]
    so the inverse is:
        quantized_x = round((lon - translate[0]) / scale[0])

    Without this, ``topojson.feature()`` on the client applies the transform
    to raw floats and produces completely wrong coordinates.

    Args:
        lon: Longitude in degrees.
        lat: Latitude in degrees.
        transform: The ``transform`` object from the TopoJSON topology.

    Returns:
        ``[quantized_x, quantized_y]`` as a list of ints.
    """
    sx, sy = transform["scale"]
    dx, dy = transform["translate"]
    return [round((lon - dx) / sx), round((lat - dy) / sy)]


def inject_points(topojson_path: Path, point_features: list[dict[str, Any]]) -> None:
    """Add point features into an existing TopoJSON file as a second object.

    Point geometries don't use arcs, so they can be appended to the topology
    without touching the existing arc list.  Coordinates are quantized to match
    the topology's transform so that ``topojson.feature()`` on the client
    decodes them back to correct WGS84 positions.

    Args:
        topojson_path: Path to the TopoJSON file produced by mapshaper.
        point_features: GeoJSON Feature dicts whose geometry is a Point.
    """
    with topojson_path.open() as f:
        topology: dict[str, Any] = json.load(f)

    transform: dict[str, Any] | None = topology.get("transform")

    def coords(feat: dict[str, Any]) -> list[int] | list[float]:
        lon, lat = feat["geometry"]["coordinates"]
        return _quantize(lon, lat, transform) if transform else [lon, lat]

    topology["objects"]["points"] = {
        "type": "GeometryCollection",
        "geometries": [
            {
                "type": "Point",
                "coordinates": coords(feat),
                "properties": feat["properties"],
            }
            for feat in point_features
        ],
    }

    with topojson_path.open("w") as f:
        json.dump(topology, f)


def main() -> None:
    """Run the markers pipeline."""
    if not MERGED_GEOJSON.exists():
        msg = f"Input file not found: {MERGED_GEOJSON}\nRun 'make build' first."
        raise FileNotFoundError(msg)

    simplify = os.environ.get("SIMPLIFY", "3%")

    print(f"Reading {MERGED_GEOJSON}...")
    gdf = gpd.read_file(MERGED_GEOJSON)
    print(f"  Loaded {len(gdf)} features")
    print(f"  Area threshold: {AREA_THRESHOLD_KM2} km²")
    print(f"  Simplification: {simplify}\n")

    polygon_collection, point_features = build_markers_collection(gdf)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with MARKERS_GEOJSON.open("w") as f:
        json.dump(polygon_collection, f)

    size_mb = MARKERS_GEOJSON.stat().st_size / (1024 * 1024)
    print(f"\nWrote {MARKERS_GEOJSON} ({size_mb:.1f} MB)")

    run_mapshaper(MARKERS_GEOJSON, MARKERS_TOPOJSON, simplify=simplify)
    inject_points(MARKERS_TOPOJSON, point_features)
    print(f"  Injected {len(point_features)} point markers into topology")

    outputs = [
        ("tcc-330.json", OUTPUT_DIR / "tcc-330.json"),
        ("tcc-330-markers.json", MARKERS_TOPOJSON),
    ]
    print("\nOutput files:")
    for label, path in outputs:
        size = path.stat().st_size if path.exists() else None
        human = f"{size / 1024:.0f} KB" if size is not None else "missing"
        print(f"  {label:<26} {human}")


if __name__ == "__main__":
    main()
