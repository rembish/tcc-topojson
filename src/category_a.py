"""Category A: Direct NE feature extraction (~180 destinations).

Matches sovereign nations and territories directly from Natural Earth
admin_0_map_subunits or admin_0_map_units layers.
"""

from shapely.geometry import shape
from shapely.ops import unary_union

from .utils import to_feature, make_properties


def _find_geom(code, subunits_gdf, units_gdf):
    """Find a geometry by A3 code from admin_0 layers."""
    for gdf in [subunits_gdf, units_gdf]:
        for field in ["SU_A3", "ADM0_A3", "ISO_A3", "GU_A3"]:
            if field not in gdf.columns:
                continue
            matches = gdf[gdf[field] == code]
            if len(matches) >= 1:
                return matches.dissolve().geometry.iloc[0]
    return None


def extract_direct(dest, subunits_gdf, units_gdf):
    """Extract a feature directly from NE admin_0 layers.

    Tries map_subunits first, then falls back to map_units.
    Matches on ADM0_A3, SU_A3, GU_A3, or ISO_A3 against dest's iso_a3.
    Also tries NAME match as a last resort.
    If merge_a3 is specified, additional features are dissolved into the result.
    """
    iso_a3 = dest.get("iso_a3")
    # Override for non-standard NE codes, or explicit adm0_a3 from extraction config
    ne_a3 = dest.get("ne_a3") or dest.get("adm0_a3") or iso_a3
    name = dest["name"]
    merge_a3 = dest.get("merge_a3", [])

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


def extract_subunit(dest, subunits_gdf):
    """Extract a specific subunit from NE map_subunits by su_a3 code."""
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
