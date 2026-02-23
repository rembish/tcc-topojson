"""Category C: Custom GIS work (~55 destinations).

Handles transcontinental clips, disputed territories, island extractions,
Antarctic wedges, and point markers.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from shapely.geometry import MultiPolygon, Point, Polygon
from shapely.ops import unary_union

from .boundary import clip_to_asia, clip_to_europe
from .utils import (
    extract_polygons_by_bbox,
    get_country_geom,
    make_properties,
    to_feature,
)

if TYPE_CHECKING:
    import geopandas as gpd

    from .types import Bbox, TccDestination, TccFeature


def extract_clip(
    dest: TccDestination,
    subunits_gdf: gpd.GeoDataFrame,
    units_gdf: gpd.GeoDataFrame,
    built: dict[int, TccFeature] | None = None,
) -> TccFeature | None:
    """Clip a country polygon with the Europe-Asia boundary.

    Used for Russia and Turkey transcontinental splits.
    Optionally subtracts already-built features listed in subtract_indices.

    Args:
        dest: Merged destination config dict from ``get_destinations()``.
        subunits_gdf: Natural Earth admin_0_map_subunits GeoDataFrame.
        units_gdf: Natural Earth admin_0_map_units GeoDataFrame.
        built: Dict of already-built features keyed by tcc_index; used to
            subtract other TCC destinations from the clip result.

    Returns:
        A GeoJSON Feature dict, or None if clipping fails or produces an empty result.
    """
    adm0 = dest.get("adm0_a3")
    side = dest.get("side")

    if not adm0 or not side:
        return None

    # Get country geometry
    country_geom = get_country_geom(adm0, subunits_gdf, units_gdf)
    if country_geom is None:
        print(f"  WARNING: Could not find {adm0} for clip")
        return None

    if side == "europe":
        result = clip_to_europe(country_geom)
    elif side == "asia":
        result = clip_to_asia(country_geom)
    else:
        return None

    if result is None or result.is_empty:
        print(f"  WARNING: Clip result empty for {dest['name']}")
        return None

    # Absorb stray polygon parts from the opposite side within a longitude
    # range.  Fixes Caucasus ridge slivers that end up on the wrong side.
    absorb_lon = dest.get("absorb_lon_range")
    if absorb_lon and isinstance(result, (Polygon, MultiPolygon)):
        lo, hi = absorb_lon
        if side == "europe":
            # Europe absorbs stray Asia parts in the lon range
            asia_result = country_geom.difference(result)
            strays = _collect_parts_in_lon(asia_result, lo, hi)
            if strays:
                result = unary_union([result, *strays])
        else:
            # Asia sheds parts in the lon range (they belong to Europe)
            keep, _ = _split_parts_by_lon(result, lo, hi)
            if keep:
                result = unary_union(keep)

    # Subtract other TCC features if specified
    subtract_indices: list[int] = dest.get("subtract_indices", [])
    if subtract_indices and built:
        from shapely.geometry import shape as shp

        subtract_geoms = []
        for idx in subtract_indices:
            feat = built.get(idx)
            if feat:
                subtract_geoms.append(shp(feat["geometry"]))
        if subtract_geoms:
            subtract_union = unary_union(subtract_geoms)
            result = result.difference(subtract_union.buffer(0))
            if result.is_empty:
                print(f"  WARNING: Clip-subtract result empty for {dest['name']}")
                return None
            if not result.is_valid:
                result = result.buffer(0)

    # Subtract NE subunits by SU_A3 code (e.g. Crimea from Russia)
    subtract_su: list[str] = dest.get("subtract_su_a3", [])
    if subtract_su:
        subtract_geoms = []
        for su_code in subtract_su:
            if "SU_A3" in subunits_gdf.columns:
                matches = subunits_gdf[subunits_gdf["SU_A3"] == su_code]
                if len(matches) > 0:
                    subtract_geoms.append(matches.dissolve().geometry.iloc[0])
        if subtract_geoms:
            subtract_union = unary_union(subtract_geoms)
            result = result.difference(subtract_union.buffer(0))
            if result.is_empty:
                print(f"  WARNING: Clip-subtract-su result empty for {dest['name']}")
                return None
            if not result.is_valid:
                result = result.buffer(0)

    return to_feature(result, make_properties(dest))


def extract_disputed(
    dest: TccDestination,
    disputed_gdf: gpd.GeoDataFrame,
) -> TccFeature | None:
    """Extract a feature from NE breakaway_disputed_areas layer.

    Args:
        dest: Merged destination config dict from ``get_destinations()``.
        disputed_gdf: Natural Earth breakaway_disputed_areas GeoDataFrame.

    Returns:
        A GeoJSON Feature dict, or None if the disputed feature is not found.
    """
    ne_name: str = str(dest.get("ne_name", dest["name"]))
    also_merge: list[str] = dest.get("also_merge", [])

    geom = _find_disputed_geom(ne_name, disputed_gdf)
    if geom is None:
        print(f"  WARNING: Disputed feature not found: {ne_name}")
        return None

    # Merge additional disputed features if specified
    for extra_name in also_merge:
        extra = _find_disputed_geom(extra_name, disputed_gdf)
        if extra is not None:
            geom = unary_union([geom, extra])

    return to_feature(geom, make_properties(dest))


def _find_disputed_geom(name: str, disputed_gdf: gpd.GeoDataFrame) -> Any | None:
    """Find a geometry from the disputed layer by name.

    Searches across NAME, BRK_NAME, NAME_LONG, and ADMIN fields using a
    case-insensitive substring match.

    Args:
        name: Name (or partial name) to search for.
        disputed_gdf: Natural Earth breakaway_disputed_areas GeoDataFrame.

    Returns:
        A dissolved shapely geometry, or None if not found.
    """
    for field in ["NAME", "BRK_NAME", "NAME_LONG", "ADMIN"]:
        if field not in disputed_gdf.columns:
            continue
        matches = disputed_gdf[disputed_gdf[field].str.lower().str.contains(name.lower(), na=False)]
        if len(matches) > 0:
            return matches.dissolve().geometry.iloc[0]
    return None


def extract_island_bbox(
    dest: TccDestination,
    subunits_gdf: gpd.GeoDataFrame,
    units_gdf: gpd.GeoDataFrame,
    admin1_gdf: gpd.GeoDataFrame | None = None,
) -> TccFeature | None:
    """Extract island polygons from a parent feature by bounding box.

    Finds the parent feature, then extracts individual polygon rings
    whose centroids fall within the specified bbox.

    Args:
        dest: Merged destination config dict from ``get_destinations()``.
        subunits_gdf: Natural Earth admin_0_map_subunits GeoDataFrame.
        units_gdf: Natural Earth admin_0_map_units GeoDataFrame.
        admin1_gdf: Natural Earth admin_1_states_provinces GeoDataFrame, or None.

    Returns:
        A GeoJSON Feature dict, or None if the parent or bbox polygons are not found.
    """
    bbox: Bbox | None = dest.get("bbox")
    parent_adm0: str | None = dest.get("parent_adm0") or dest.get("parent_adm0_a3")
    parent_admin1: str | None = dest.get("parent_admin1")

    if not bbox:
        return None

    # Get parent geometry
    if parent_admin1 and admin1_gdf is not None:
        parent_geom = _get_admin1_geom(parent_adm0, parent_admin1, admin1_gdf)
    elif parent_adm0:
        parent_geom = get_country_geom(parent_adm0, subunits_gdf, units_gdf)
    else:
        return None

    if parent_geom is None:
        print(f"  WARNING: Parent feature not found for {dest['name']}")
        return None

    result = extract_polygons_by_bbox(parent_geom, bbox)
    if result is None:
        print(f"  WARNING: No polygons in bbox for {dest['name']}")
        return None

    return to_feature(result, make_properties(dest))


def extract_group_remainder(
    dest: TccDestination,
    subunits_gdf: gpd.GeoDataFrame,
    units_gdf: gpd.GeoDataFrame,
    built_features: dict[int, TccFeature],
) -> TccFeature | None:
    """Extract a feature that is the remainder after subtracting other TCC destinations.

    Takes the parent admin_0 feature and subtracts geometries of already-built
    TCC destinations specified by subtract_indices.

    Args:
        dest: Merged destination config dict from ``get_destinations()``.
        subunits_gdf: Natural Earth admin_0_map_subunits GeoDataFrame.
        units_gdf: Natural Earth admin_0_map_units GeoDataFrame.
        built_features: Dict of already-built features keyed by tcc_index.

    Returns:
        A GeoJSON Feature dict, or None if the country geometry is not found
        or the remainder is empty.
    """
    adm0 = dest.get("adm0_a3")
    subtract_indices: list[int] = dest.get("subtract_indices", [])

    if not adm0:
        return None

    country_geom = get_country_geom(adm0, subunits_gdf, units_gdf)
    if country_geom is None:
        return None

    if not subtract_indices:
        return to_feature(country_geom, make_properties(dest))

    subtract_geoms = []
    for idx in subtract_indices:
        feat = built_features.get(idx)
        if feat:
            from shapely.geometry import shape

            subtract_geoms.append(shape(feat["geometry"]))

    if subtract_geoms:
        subtract_union = unary_union(subtract_geoms)
        result = country_geom.difference(subtract_union.buffer(0))
        if not result.is_valid:
            result = result.buffer(0)
        if result.is_empty:
            print(f"  WARNING: Group remainder empty for {dest['name']}")
            return None
        return to_feature(result, make_properties(dest))

    return to_feature(country_geom, make_properties(dest))


def generate_antarctic_wedge(
    dest: TccDestination,
    antarctica_geom: Any | None = None,
) -> TccFeature | None:
    """Generate an Antarctic sector clipped to the real coastline.

    Creates a wedge polygon between the specified longitudes, then
    intersects it with the actual Antarctica geometry from Natural Earth
    so the result follows the real coastline.

    Args:
        dest: Merged destination config dict.  Must contain ``lon_west`` and
            ``lon_east``, or a ``sectors`` list of ``{lon_west, lon_east}`` dicts.
            Optional ``lat_north`` defaults to -60.
        antarctica_geom: Shapely geometry for Antarctica (from NE units layer),
            used to clip the generated wedge to the real coastline.  If None,
            the raw wedge polygon is returned.

    Returns:
        A GeoJSON Feature dict, or None if no sector geometry could be generated.
    """
    lat_north: float = dest.get("lat_north", -60)
    lat_south = -90.0
    sectors: list[dict[str, float]] | None = dest.get("sectors")

    # Multi-sector territories (e.g., Australian Antarctic Territory)
    if sectors:
        parts = [_make_wedge(s["lon_west"], s["lon_east"], lat_north, lat_south) for s in sectors]
        wedge = unary_union(parts) if len(parts) > 1 else parts[0]
    else:
        # Single sector
        lon_west: float | None = dest.get("lon_west")
        lon_east: float | None = dest.get("lon_east")

        if lon_west is None or lon_east is None:
            return None

        # Handle sectors that cross the antimeridian (e.g., Ross Dependency: 160°E to 150°W)
        if lon_west > lon_east:
            wedge1 = _make_wedge(lon_west, 180, lat_north, lat_south)
            wedge2 = _make_wedge(-180, lon_east, lat_north, lat_south)
            wedge = unary_union([wedge1, wedge2])
        else:
            wedge = _make_wedge(lon_west, lon_east, lat_north, lat_south)

    # Clip wedge with actual Antarctica coastline
    if antarctica_geom is not None:
        result = antarctica_geom.intersection(wedge)
        if result.is_empty:
            print(f"  WARNING: Antarctic clip empty for {dest['name']}, using wedge")
            result = wedge
        elif not result.is_valid:
            result = result.buffer(0)
    else:
        result = wedge

    return to_feature(result, make_properties(dest))


def generate_point(dest: TccDestination) -> TccFeature | None:
    """Generate a Point feature for tiny islands.

    Used for destinations too small for meaningful polygons at web scale
    (e.g., Midway, Wake Island, Tokelau, Niue, Nauru, Tuvalu).

    Args:
        dest: Merged destination config dict.  Must contain ``lat`` and ``lon`` keys.

    Returns:
        A GeoJSON Feature dict with ``is_point=True`` in its properties,
        or None if ``lat`` or ``lon`` are missing.
    """
    lat: float | None = dest.get("lat")
    lon: float | None = dest.get("lon")

    if lat is None or lon is None:
        return None

    point = Point(lon, lat)
    props = make_properties(dest)
    props["is_point"] = True
    return to_feature(point, props)


def _make_wedge(
    lon_west: float,
    lon_east: float,
    lat_north: float,
    lat_south: float,
    n_points: int = 60,
) -> Polygon:
    """Create a wedge polygon from the South Pole to lat_north.

    Args:
        lon_west: Western longitude bound (degrees).
        lon_east: Eastern longitude bound (degrees).
        lat_north: Northern latitude bound (degrees, e.g. -60).
        lat_south: Southern latitude bound (degrees, e.g. -90).
        n_points: Number of points along the northern arc for smoothness.

    Returns:
        A ``Polygon`` wedge from ``lat_south`` to ``lat_north`` between the
        two longitudes.
    """
    coords: list[tuple[float, float]] = []

    # Northern arc from west to east
    for i in range(n_points + 1):
        lon = lon_west + (lon_east - lon_west) * i / n_points
        coords.append((lon, lat_north))

    # South pole (or near it)
    coords.append((lon_east, lat_south))
    coords.append((lon_west, lat_south))

    # Close
    coords.append(coords[0])

    return Polygon(coords)


def _collect_parts_in_lon(geom: Polygon | MultiPolygon, lo: float, hi: float) -> list[Polygon]:
    """Return polygon parts whose centroid longitude falls within ``[lo, hi]``.

    Args:
        geom: A ``Polygon`` or ``MultiPolygon`` to inspect.
        lo: Western longitude bound (inclusive).
        hi: Eastern longitude bound (inclusive).

    Returns:
        List of polygon parts whose centroid.x is in ``[lo, hi]``.
    """
    parts: list[Polygon] = []
    if isinstance(geom, Polygon):
        if lo <= geom.centroid.x <= hi:
            parts.append(geom)
    elif isinstance(geom, MultiPolygon):
        for p in geom.geoms:
            if lo <= p.centroid.x <= hi:
                parts.append(p)
    return parts


def _split_parts_by_lon(
    geom: Polygon | MultiPolygon,
    lo: float,
    hi: float,
) -> tuple[list[Polygon], list[Polygon]]:
    """Split a geometry into parts outside vs inside a longitude range.

    Args:
        geom: A ``Polygon`` or ``MultiPolygon`` to split.
        lo: Western longitude bound (inclusive).
        hi: Eastern longitude bound (inclusive).

    Returns:
        A ``(keep, shed)`` tuple where ``keep`` contains parts whose centroid.x
        is outside ``[lo, hi]`` and ``shed`` contains parts inside ``[lo, hi]``.
    """
    keep: list[Polygon] = []
    shed: list[Polygon] = []
    if isinstance(geom, Polygon):
        if lo <= geom.centroid.x <= hi:
            shed.append(geom)
        else:
            keep.append(geom)
    elif isinstance(geom, MultiPolygon):
        for p in geom.geoms:
            if lo <= p.centroid.x <= hi:
                shed.append(p)
            else:
                keep.append(p)
    return keep, shed


def _get_admin1_geom(
    adm0_a3: str | None,
    admin1_name: str,
    admin1_gdf: gpd.GeoDataFrame,
) -> Any | None:
    """Get an admin1 geometry by country code and province name.

    Args:
        adm0_a3: Three-letter country A3 code to filter on, or None to skip filtering.
        admin1_name: Province name to match (case-insensitive exact match).
        admin1_gdf: Natural Earth admin_1_states_provinces GeoDataFrame.

    Returns:
        A dissolved shapely geometry, or None if not found.
    """
    country = admin1_gdf[admin1_gdf["adm0_a3"] == adm0_a3] if adm0_a3 else admin1_gdf

    for field in ["name", "name_en", "NAME", "NAME_EN"]:
        if field not in country.columns:
            continue
        matches = country[country[field].str.lower() == admin1_name.lower()]
        if len(matches) > 0:
            return matches.dissolve().geometry.iloc[0]

    return None
