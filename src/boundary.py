"""Trubetskoy Europe-Asia boundary loading and clipping helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from shapely.geometry import (
    GeometryCollection,
    LineString,
    MultiLineString,
    MultiPolygon,
    Polygon,
    shape,
)
from shapely.ops import linemerge, unary_union

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

_boundary_line: MultiLineString | LineString | None = None
_ordered_path: list[tuple[float, float]] | None = None


def load_boundary() -> MultiLineString | LineString:
    """Load the Trubetskoy Europe-Asia boundary as a shapely geometry.

    Results are cached in the module-level ``_boundary_line`` variable so
    subsequent calls return immediately.

    Returns:
        A ``MultiLineString`` or ``LineString`` representing the boundary.
    """
    global _boundary_line
    if _boundary_line is not None:
        return _boundary_line

    path = DATA_DIR / "europe_asia_boundary.geojson"
    with open(path) as f:
        data = json.load(f)

    lines: list[LineString] = []
    for feat in data["features"]:
        geom = shape(feat["geometry"])
        if geom.geom_type == "LineString":
            lines.append(geom)
        elif geom.geom_type == "MultiLineString":
            lines.extend(geom.geoms)

    _boundary_line = MultiLineString(lines) if len(lines) > 1 else lines[0]
    return _boundary_line


def _build_ordered_path(boundary: MultiLineString | LineString) -> list[tuple[float, float]]:
    """Merge boundary segments and build a single ordered coordinate path.

    The boundary data has 464 separate LineString segments. After linemerge,
    we get ~3 nearly-connected lines with tiny gaps (~0.003°). We snap them
    together, re-merge into a single LineString, and return ordered coordinates
    from south (Mediterranean) to north (Arctic).

    Results are cached in the module-level ``_ordered_path`` variable.

    Args:
        boundary: The boundary geometry returned by :func:`load_boundary`.

    Returns:
        An ordered list of ``(lon, lat)`` coordinate tuples running south-to-north.
    """
    global _ordered_path
    if _ordered_path is not None:
        return _ordered_path

    # Step 1: linemerge to connect segments that share exact endpoints
    if boundary.geom_type == "MultiLineString":
        merged = linemerge(boundary)
    else:
        merged = boundary

    if merged.geom_type == "LineString":
        _ordered_path = list(merged.coords)
        return _ordered_path

    # Step 2: We have multiple lines — snap them together and re-merge
    lines: list[LineString] = list(merged.geoms)

    # Sort by southernmost latitude to start building from the south
    lines.sort(key=lambda l: min(c[1] for c in l.coords))

    # Greedy nearest-neighbor: chain lines into a single coordinate path
    ordered_coords: list[tuple[float, float]] = list(lines[0].coords)
    remaining = lines[1:]

    while remaining:
        end_pt = ordered_coords[-1]
        best_idx: int | None = None
        best_dist = float("inf")
        best_reverse = False

        for i, line in enumerate(remaining):
            coords: list[tuple[float, float]] = list(line.coords)
            d_start = _pt_dist(end_pt, coords[0])
            d_end = _pt_dist(end_pt, coords[-1])

            if d_start < best_dist:
                best_dist = d_start
                best_idx = i
                best_reverse = False
            if d_end < best_dist:
                best_dist = d_end
                best_idx = i
                best_reverse = True

        if best_idx is not None and best_dist < 5.0:
            line = remaining.pop(best_idx)
            coords = list(line.coords)
            if best_reverse:
                coords.reverse()
            ordered_coords.extend(coords)
        else:
            break

    # Ensure path goes south-to-north (ascending latitude)
    if ordered_coords[0][1] > ordered_coords[-1][1]:
        ordered_coords.reverse()

    _ordered_path = ordered_coords
    return _ordered_path


def _pt_dist(p1: tuple[float, float], p2: tuple[float, float]) -> float:
    """Euclidean distance between two ``(x, y)`` coordinate tuples.

    Args:
        p1: First point as ``(longitude, latitude)``.
        p2: Second point as ``(longitude, latitude)``.

    Returns:
        Euclidean distance (degrees).
    """
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5


def clip_to_europe(country_geom: Polygon | MultiPolygon) -> Polygon | MultiPolygon:
    """Clip a country geometry to keep only the European part (west of boundary).

    Uses the Trubetskoy boundary line to split the geometry. The European
    part is defined as the portion west of the Urals / north-west of the
    Caucasus / west of the Bosphorus.

    Args:
        country_geom: The full country polygon to clip.

    Returns:
        The European portion of the geometry (falls back to the full geometry
        if the clip produces an empty result).
    """
    boundary = load_boundary()
    return _clip_by_boundary(country_geom, boundary, side="europe")


def clip_to_asia(country_geom: Polygon | MultiPolygon) -> Polygon | MultiPolygon:
    """Clip a country geometry to keep only the Asian part (east of boundary).

    Args:
        country_geom: The full country polygon to clip.

    Returns:
        The Asian portion of the geometry (falls back to the full geometry
        if the clip produces an empty result).
    """
    boundary = load_boundary()
    return _clip_by_boundary(country_geom, boundary, side="asia")


def _clip_by_boundary(
    country_geom: Polygon | MultiPolygon,
    boundary: MultiLineString | LineString,
    side: Literal["europe", "asia"],
) -> Polygon | MultiPolygon:
    """Split country geometry using the Europe-Asia boundary.

    Strategy:
    1. Build ordered boundary path (south-to-north).
    2. Construct Europe clip polygon by closing the path via a far-west
       rectangle.
    3. Intersect with country geometry to get the European part.
    4. For Asia: subtract the European part from the country (avoids
       Aegean-pocket overlap issues with a separate Asia polygon).

    Args:
        country_geom: The full country polygon to clip.
        boundary: The loaded boundary line geometry.
        side: ``"europe"`` to keep the western part; ``"asia"`` to keep the eastern part.

    Returns:
        The clipped geometry for the requested side, or the full ``country_geom``
        if clipping fails or produces an empty result.
    """
    ordered_coords = _build_ordered_path(boundary)

    # Get the bounds of the country (extended)
    minx, miny, maxx, maxy = country_geom.bounds
    pad = 10

    first = ordered_coords[0]
    last = ordered_coords[-1]

    # Always build the Europe polygon (boundary + close via far west).
    # Clamp the western edge to -30° to avoid wrapping past the antimeridian
    # and accidentally capturing far-east Russia (Chukotka at ~-170°).
    west_edge = max(minx - pad, -30)

    closing = [
        (west_edge, last[1]),  # west from north end
        (west_edge, first[1]),  # south along west edge
        first,  # close
    ]
    poly_coords = ordered_coords + closing

    try:
        europe_polygon = Polygon(poly_coords)
        if not europe_polygon.is_valid:
            europe_polygon = europe_polygon.buffer(0)
        europe_result = country_geom.intersection(europe_polygon)
    except Exception:  # noqa: BLE001
        # Fallback: buffer-strip approach with ray-casting classification
        result = _fallback_clip(country_geom, boundary, side)
        if result is None or result.is_empty:
            return country_geom
        clean = _extract_polygons(result)
        if clean is None or clean.is_empty:
            return country_geom
        if not clean.is_valid:
            clean = clean.buffer(0)
        return clean

    europe_result = _extract_polygons(europe_result)

    if side == "europe":
        if europe_result is None or europe_result.is_empty:
            return country_geom
        if not europe_result.is_valid:
            europe_result = europe_result.buffer(0)
        return europe_result
    else:
        # Asia = country minus Europe (avoids overlap from Aegean pocket)
        if europe_result is None or europe_result.is_empty:
            return country_geom
        asia_result = country_geom.difference(europe_result)
        asia_result = _extract_polygons(asia_result)
        if asia_result is None or asia_result.is_empty:
            return country_geom
        if not asia_result.is_valid:
            asia_result = asia_result.buffer(0)
        return asia_result


def _fallback_clip(
    country_geom: Polygon | MultiPolygon,
    boundary: MultiLineString | LineString,
    side: Literal["europe", "asia"],
) -> Polygon | MultiPolygon | None:
    """Fallback clip using buffer strip + ray-casting classification.

    Used when the primary polygon-intersection approach raises an exception.
    Classifies each polygon piece by counting how many times a horizontal ray
    from the far west to the piece's centroid crosses the boundary line.

    Args:
        country_geom: The full country polygon to clip.
        boundary: The loaded boundary line geometry.
        side: ``"europe"`` to keep western pieces; ``"asia"`` to keep eastern pieces.

    Returns:
        Union of the classified pieces, or None if no pieces qualify.
    """
    if boundary.geom_type == "MultiLineString":
        merged = linemerge(boundary)
    else:
        merged = boundary

    strip = merged.buffer(0.005)
    remainder = country_geom.difference(strip)

    if remainder.is_empty:
        return None

    pieces = _collect_polygons(remainder)
    if not pieces:
        return None

    # Classify each piece using horizontal ray-casting against the boundary
    # A point is in Asia if a horizontal ray from far west crosses the
    # boundary an odd number of times
    european: list[Polygon] = []
    asian: list[Polygon] = []
    for piece in pieces:
        cx, cy = piece.centroid.x, piece.centroid.y
        ray = LineString([(-180, cy), (cx, cy)])
        crossings = _count_crossings(ray, merged)
        if crossings % 2 == 0:
            european.append(piece)
        else:
            asian.append(piece)

    selected = european if side == "europe" else asian
    if not selected:
        return None

    return unary_union(selected)


def _count_crossings(ray: LineString, boundary_line: LineString | MultiLineString) -> int:
    """Count the number of times a ray crosses the boundary.

    Args:
        ray: A horizontal ``LineString`` ray from longitude -180 to the centroid.
        boundary_line: The (merged) Europe-Asia boundary line.

    Returns:
        Number of Point intersections between the ray and the boundary.
    """
    inter = ray.intersection(boundary_line)
    if inter.is_empty:
        return 0
    if inter.geom_type == "Point":
        return 1
    if inter.geom_type == "MultiPoint":
        return len(inter.geoms)
    if inter.geom_type == "GeometryCollection":
        return sum(1 for g in inter.geoms if g.geom_type == "Point")
    return 0


def _collect_polygons(geom: object) -> list[Polygon]:
    """Extract all Polygon instances from any geometry type.

    Recurses into ``MultiPolygon`` and ``GeometryCollection`` containers.

    Args:
        geom: Any shapely geometry object.

    Returns:
        Flat list of all ``Polygon`` instances found within ``geom``.
    """
    if isinstance(geom, Polygon):
        return [geom]
    if isinstance(geom, MultiPolygon):
        return list(geom.geoms)
    if isinstance(geom, GeometryCollection):
        result: list[Polygon] = []
        for g in geom.geoms:
            result.extend(_collect_polygons(g))
        return result
    return []


def _extract_polygons(geom: object) -> Polygon | MultiPolygon | None:
    """Extract polygons from a geometry result, discarding points/lines.

    Args:
        geom: Any shapely geometry (e.g. result of ``intersection`` or ``difference``).

    Returns:
        A single ``Polygon``, a ``MultiPolygon``, or ``None`` if no polygons exist.
    """
    polys = _collect_polygons(geom)
    if not polys:
        return None
    if len(polys) == 1:
        return polys[0]
    return MultiPolygon(polys)
