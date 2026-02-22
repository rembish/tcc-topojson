"""Shared GIS utilities for TCC TopoJSON build."""

from shapely.geometry import MultiPolygon, Polygon, shape, mapping
from shapely.ops import unary_union
import geopandas as gpd


def dissolve_geometries(geometries):
    """Dissolve a list of geometries into a single geometry."""
    return unary_union(geometries)


def extract_polygons_by_bbox(geom, bbox):
    """Extract individual polygons from a Multi/Polygon whose centroid falls within bbox.

    Args:
        geom: A shapely geometry (Polygon or MultiPolygon).
        bbox: (west, south, east, north) bounding box.

    Returns:
        A MultiPolygon or Polygon of matching sub-polygons, or None.
    """
    w, s, e, n = bbox
    bbox_poly = Polygon([(w, s), (e, s), (e, n), (w, n)])

    if isinstance(geom, Polygon):
        polys = [geom]
    elif isinstance(geom, MultiPolygon):
        polys = list(geom.geoms)
    else:
        return None

    matches = [p for p in polys if bbox_poly.contains(p.centroid)]

    if not matches:
        # Fallback: check intersection instead of centroid containment
        matches = [p for p in polys if bbox_poly.intersects(p)]

    if not matches:
        return None
    if len(matches) == 1:
        return matches[0]
    return MultiPolygon(matches)


def subtract_polygons_by_bbox(geom, bbox):
    """Remove polygons whose centroid falls within bbox from a Multi/Polygon.

    Returns the remaining geometry.
    """
    w, s, e, n = bbox
    bbox_poly = Polygon([(w, s), (e, s), (e, n), (w, n)])

    if isinstance(geom, Polygon):
        polys = [geom]
    elif isinstance(geom, MultiPolygon):
        polys = list(geom.geoms)
    else:
        return geom

    remaining = [p for p in polys if not bbox_poly.contains(p.centroid)]

    if not remaining:
        return None
    if len(remaining) == 1:
        return remaining[0]
    return MultiPolygon(remaining)


def load_shapefile(path):
    """Load a shapefile as a GeoDataFrame."""
    return gpd.read_file(path)


def to_feature(geometry, properties):
    """Create a GeoJSON-style feature dict."""
    return {
        "type": "Feature",
        "geometry": mapping(geometry),
        "properties": properties,
    }


def make_properties(dest):
    """Create the standard TCC properties dict from a destination config."""
    return {
        "tcc_index": dest["tcc_index"],
        "name": dest["name"],
        "region": dest["region"],
        "iso_a2": dest.get("iso_a2"),
        "iso_a3": dest.get("iso_a3"),
        "iso_n3": dest.get("iso_n3"),
        "sovereign": dest.get("sovereign"),
        "type": dest.get("type"),
    }
