"""Category C: Custom GIS work (~55 destinations).

Handles transcontinental clips, disputed territories, island extractions,
Antarctic wedges, and point markers.
"""

import math

from shapely.geometry import Point, Polygon, MultiPolygon, mapping
from shapely.ops import unary_union

from .boundary import clip_to_europe, clip_to_asia
from .utils import (
    extract_polygons_by_bbox,
    subtract_polygons_by_bbox,
    to_feature,
    make_properties,
)


def extract_clip(dest, subunits_gdf, units_gdf, built=None):
    """Clip a country polygon with the Europe-Asia boundary.

    Used for Russia and Turkey transcontinental splits.
    Optionally subtracts already-built features listed in subtract_indices.
    """
    adm0 = dest.get("adm0_a3")
    side = dest.get("side")

    if not adm0 or not side:
        return None

    # Get country geometry
    country_geom = _get_country_geom(adm0, subunits_gdf, units_gdf)
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
                result = unary_union([result] + strays)
        else:
            # Asia sheds parts in the lon range (they belong to Europe)
            keep, _ = _split_parts_by_lon(result, lo, hi)
            if keep:
                result = unary_union(keep)
            else:
                result = result

    # Subtract other TCC features if specified
    subtract_indices = dest.get("subtract_indices", [])
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
    subtract_su = dest.get("subtract_su_a3", [])
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


def extract_disputed(dest, disputed_gdf):
    """Extract a feature from NE breakaway_disputed_areas layer."""
    ne_name = dest.get("ne_name", dest["name"])
    also_merge = dest.get("also_merge", [])

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


def _find_disputed_geom(name, disputed_gdf):
    """Find a geometry from the disputed layer by name."""
    for field in ["NAME", "BRK_NAME", "NAME_LONG", "ADMIN"]:
        if field not in disputed_gdf.columns:
            continue
        matches = disputed_gdf[
            disputed_gdf[field].str.lower().str.contains(name.lower(), na=False)
        ]
        if len(matches) > 0:
            return matches.dissolve().geometry.iloc[0]
    return None


def extract_island_bbox(dest, subunits_gdf, units_gdf, admin1_gdf=None):
    """Extract island polygons from a parent feature by bounding box.

    Finds the parent feature, then extracts individual polygon rings
    whose centroids fall within the specified bbox.
    """
    bbox = dest.get("bbox")
    parent_adm0 = dest.get("parent_adm0") or dest.get("parent_adm0_a3")
    parent_admin1 = dest.get("parent_admin1")

    if not bbox:
        return None

    # Get parent geometry
    if parent_admin1 and admin1_gdf is not None:
        parent_geom = _get_admin1_geom(parent_adm0, parent_admin1, admin1_gdf)
    elif parent_adm0:
        parent_geom = _get_country_geom(parent_adm0, subunits_gdf, units_gdf)
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


def extract_group_remainder(dest, subunits_gdf, units_gdf, built_features):
    """Extract a feature that is the remainder after subtracting other TCC destinations.

    Takes the parent admin_0 feature and subtracts geometries of already-built
    TCC destinations specified by subtract_indices.
    """
    adm0 = dest.get("adm0_a3")
    subtract_indices = dest.get("subtract_indices", [])

    if not adm0:
        return None

    country_geom = _get_country_geom(adm0, subunits_gdf, units_gdf)
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


def generate_antarctic_wedge(dest, antarctica_geom=None):
    """Generate an Antarctic sector clipped to the real coastline.

    Creates a wedge polygon between the specified longitudes, then
    intersects it with the actual Antarctica geometry from Natural Earth
    so the result follows the real coastline.
    """
    lat_north = dest.get("lat_north", -60)
    lat_south = -90
    sectors = dest.get("sectors")

    # Multi-sector territories (e.g., Australian Antarctic Territory)
    if sectors:
        parts = []
        for sector in sectors:
            parts.append(_make_wedge(sector["lon_west"], sector["lon_east"], lat_north, lat_south))
        wedge = unary_union(parts) if len(parts) > 1 else parts[0]
    else:
        # Single sector
        lon_west = dest.get("lon_west")
        lon_east = dest.get("lon_east")

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


def generate_point(dest):
    """Generate a Point feature for tiny islands."""
    lat = dest.get("lat")
    lon = dest.get("lon")

    if lat is None or lon is None:
        return None

    point = Point(lon, lat)
    props = make_properties(dest)
    props["is_point"] = True
    return to_feature(point, props)


def _make_wedge(lon_west, lon_east, lat_north, lat_south, n_points=60):
    """Create a wedge polygon from the South Pole to lat_north."""
    coords = []

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


def _collect_parts_in_lon(geom, lo, hi):
    """Return polygon parts whose centroid longitude falls within [lo, hi]."""
    parts = []
    if isinstance(geom, Polygon):
        if lo <= geom.centroid.x <= hi:
            parts.append(geom)
    elif isinstance(geom, MultiPolygon):
        for p in geom.geoms:
            if lo <= p.centroid.x <= hi:
                parts.append(p)
    return parts


def _split_parts_by_lon(geom, lo, hi):
    """Split a geometry into parts outside vs inside a longitude range.

    Returns (keep, shed) where keep has centroids outside [lo, hi]
    and shed has centroids inside [lo, hi].
    """
    keep = []
    shed = []
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


def _get_country_geom(adm0_a3, subunits_gdf, units_gdf):
    """Get the full country geometry from admin_0 layers."""
    for gdf in [subunits_gdf, units_gdf]:
        for field in ["ADM0_A3", "SU_A3", "GU_A3", "ISO_A3"]:
            if field not in gdf.columns:
                continue
            matches = gdf[gdf[field] == adm0_a3]
            if len(matches) > 0:
                return matches.dissolve().geometry.iloc[0]
    return None


def _get_admin1_geom(adm0_a3, admin1_name, admin1_gdf):
    """Get an admin1 geometry by country code and province name."""
    country = admin1_gdf[admin1_gdf["adm0_a3"] == adm0_a3]

    for field in ["name", "name_en", "NAME", "NAME_EN"]:
        if field not in country.columns:
            continue
        matches = country[country[field].str.lower() == admin1_name.lower()]
        if len(matches) > 0:
            return matches.dissolve().geometry.iloc[0]

    return None
