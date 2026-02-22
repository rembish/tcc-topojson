"""Trubetskoy Europe-Asia boundary loading and clipping helpers."""

import json
from pathlib import Path

from shapely.geometry import (
    GeometryCollection,
    LineString,
    MultiLineString,
    MultiPolygon,
    Point,
    Polygon,
    shape,
)
from shapely.ops import linemerge, snap, unary_union

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

_boundary_line = None
_ordered_path = None


def load_boundary():
    """Load the Trubetskoy Europe-Asia boundary as a shapely geometry."""
    global _boundary_line
    if _boundary_line is not None:
        return _boundary_line

    path = DATA_DIR / "europe_asia_boundary.geojson"
    with open(path) as f:
        data = json.load(f)

    lines = []
    for feat in data["features"]:
        geom = shape(feat["geometry"])
        if geom.geom_type == "LineString":
            lines.append(geom)
        elif geom.geom_type == "MultiLineString":
            lines.extend(geom.geoms)

    _boundary_line = MultiLineString(lines) if len(lines) > 1 else lines[0]
    return _boundary_line


def _build_ordered_path(boundary):
    """Merge boundary segments and build a single ordered coordinate path.

    The boundary data has 464 separate LineString segments. After linemerge,
    we get ~3 nearly-connected lines with tiny gaps (~0.003°). We snap them
    together, re-merge into a single LineString, and return ordered coordinates
    from south (Mediterranean) to north (Arctic).
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
    lines = list(merged.geoms)

    # Sort by southernmost latitude to start building from the south
    lines.sort(key=lambda l: min(c[1] for c in l.coords))

    # Greedy nearest-neighbor: chain lines into a single coordinate path
    ordered_coords = list(lines[0].coords)
    remaining = lines[1:]

    while remaining:
        end_pt = ordered_coords[-1]
        best_idx = None
        best_dist = float("inf")
        best_reverse = False

        for i, line in enumerate(remaining):
            coords = list(line.coords)
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


def _pt_dist(p1, p2):
    """Euclidean distance between two (x, y) coordinate tuples."""
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5


def clip_to_europe(country_geom):
    """Clip a country geometry to keep only the European part (west of boundary).

    Uses the Trubetskoy boundary line to split the geometry. The European
    part is defined as the portion west of the Urals / north-west of the
    Caucasus / west of the Bosphorus.
    """
    boundary = load_boundary()
    return _clip_by_boundary(country_geom, boundary, side="europe")


def clip_to_asia(country_geom):
    """Clip a country geometry to keep only the Asian part (east of boundary)."""
    boundary = load_boundary()
    return _clip_by_boundary(country_geom, boundary, side="asia")


def _clip_by_boundary(country_geom, boundary, side):
    """Split country geometry using the Europe-Asia boundary.

    Strategy:
    1. Build ordered boundary path (south-to-north).
    2. Construct Europe clip polygon by closing the path via a far-west
       rectangle.
    3. Intersect with country geometry to get the European part.
    4. For Asia: subtract the European part from the country (avoids
       Aegean-pocket overlap issues with a separate Asia polygon).
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
        (west_edge, last[1]),   # west from north end
        (west_edge, first[1]),  # south along west edge
        first,                  # close
    ]
    poly_coords = ordered_coords + closing

    try:
        europe_polygon = Polygon(poly_coords)
        if not europe_polygon.is_valid:
            europe_polygon = europe_polygon.buffer(0)
        europe_result = country_geom.intersection(europe_polygon)
    except Exception:
        # Fallback: buffer-strip approach with ray-casting classification
        result = _fallback_clip(country_geom, boundary, side)
        if result is None or result.is_empty:
            return country_geom
        result = _extract_polygons(result)
        if result is None or result.is_empty:
            return country_geom
        if not result.is_valid:
            result = result.buffer(0)
        return result

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


def _fallback_clip(country_geom, boundary, side):
    """Fallback clip using buffer strip + ray-casting classification."""
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
    european = []
    asian = []
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


def _count_crossings(ray, boundary_line):
    """Count the number of times a ray crosses the boundary."""
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


def _collect_polygons(geom):
    """Extract all Polygon instances from any geometry type."""
    if isinstance(geom, Polygon):
        return [geom]
    if isinstance(geom, MultiPolygon):
        return list(geom.geoms)
    if isinstance(geom, GeometryCollection):
        result = []
        for g in geom.geoms:
            result.extend(_collect_polygons(g))
        return result
    return []


def _extract_polygons(geom):
    """Extract polygons from a geometry result, discarding points/lines."""
    polys = _collect_polygons(geom)
    if not polys:
        return None
    if len(polys) == 1:
        return polys[0]
    return MultiPolygon(polys)
