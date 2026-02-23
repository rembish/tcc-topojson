"""Category A: Direct NE feature extraction (~180 destinations).

Matches sovereign nations and territories directly from Natural Earth
admin_0_map_subunits or admin_0_map_units layers.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from shapely.ops import unary_union

from .utils import make_properties, to_feature

if TYPE_CHECKING:
    import geopandas as gpd

    from .types import TccDestination, TccFeature


def _find_geom(
    code: str,
    subunits_gdf: gpd.GeoDataFrame,
    units_gdf: gpd.GeoDataFrame,
) -> Any | None:
    """Find a geometry by A3 code from admin_0 layers.

    Searches both GeoDataFrames across four standard A3 field names.
    Dissolves any multi-row match into a single geometry.

    Args:
        code: Three-letter A3 code to search for.
        subunits_gdf: Natural Earth admin_0_map_subunits GeoDataFrame.
        units_gdf: Natural Earth admin_0_map_units GeoDataFrame.

    Returns:
        A dissolved shapely geometry, or None if not found.
    """
    for gdf in [subunits_gdf, units_gdf]:
        for field in ["SU_A3", "ADM0_A3", "ISO_A3", "GU_A3"]:
            if field not in gdf.columns:
                continue
            matches = gdf[gdf[field] == code]
            if len(matches) >= 1:
                return matches.dissolve().geometry.iloc[0]
    return None


def extract_direct(
    dest: TccDestination,
    subunits_gdf: gpd.GeoDataFrame,
    units_gdf: gpd.GeoDataFrame,
) -> TccFeature | None:
    """Extract a feature directly from NE admin_0 layers.

    Tries map_subunits first, then falls back to map_units.
    Matches on ADM0_A3, SU_A3, GU_A3, or ISO_A3 against dest's iso_a3.
    Also tries NAME match as a last resort.
    If merge_a3 is specified, additional features are dissolved into the result.

    Args:
        dest: Merged destination config dict from ``get_destinations()``.
        subunits_gdf: Natural Earth admin_0_map_subunits GeoDataFrame.
        units_gdf: Natural Earth admin_0_map_units GeoDataFrame.

    Returns:
        A GeoJSON Feature dict, or None if the feature could not be found.
    """
    iso_a3 = dest.get("iso_a3")
    # Override for non-standard NE codes, or explicit adm0_a3 from extraction config
    ne_a3 = dest.get("ne_a3") or dest.get("adm0_a3") or iso_a3
    name = dest["name"]
    merge_a3: list[str] = dest.get("merge_a3", [])

    geom = None

    if ne_a3:
        geom = _find_geom(ne_a3, subunits_gdf, units_gdf)

    # Fallback: try name match
    if geom is None:
        for gdf in [subunits_gdf, units_gdf]:
            if "NAME" in gdf.columns:
                matches = gdf[gdf["NAME"].str.lower() == name.lower()]
                if len(matches) >= 1:
                    geom = matches.dissolve().geometry.iloc[0]
                    break

    if geom is None:
        return None

    # Merge additional features if specified (e.g. Baikonur into Kazakhstan)
    if merge_a3:
        parts = [geom]
        for code in merge_a3:
            extra = _find_geom(code, subunits_gdf, units_gdf)
            if extra is not None:
                parts.append(extra)
        geom = unary_union(parts)

    return to_feature(geom, make_properties(dest))


def extract_subunit(
    dest: TccDestination,
    subunits_gdf: gpd.GeoDataFrame,
) -> TccFeature | None:
    """Extract a specific subunit from NE map_subunits by su_a3 code.

    Used for England, Scotland, Wales, Northern Ireland, Corsica, Srpska, etc.
    Falls back to NAME_EN / NAME match if the SU_A3 lookup fails.

    Args:
        dest: Merged destination config dict from ``get_destinations()``.
        subunits_gdf: Natural Earth admin_0_map_subunits GeoDataFrame.

    Returns:
        A GeoJSON Feature dict, or None if the subunit could not be found.
    """
    su_a3 = dest.get("su_a3")
    ne_name = dest.get("ne_name")
    if not su_a3:
        return None

    matches = subunits_gdf[subunits_gdf["SU_A3"] == su_a3]

    # If ne_name is given, narrow to the specific feature by NAME
    if ne_name and len(matches) > 1:
        named = matches[matches["NAME"] == ne_name]
        if len(named) > 0:
            matches = named

    if len(matches) == 0:
        # Try NAME_EN or NAME
        for field in ["NAME_EN", "NAME"]:
            if field in subunits_gdf.columns:
                matches = subunits_gdf[subunits_gdf[field].str.lower() == dest["name"].lower()]
                if len(matches) >= 1:
                    break

    if len(matches) == 0:
        return None

    geom = matches.dissolve().geometry.iloc[0]
    return to_feature(geom, make_properties(dest))
