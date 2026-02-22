"""Category B: admin_1 extraction, merge, and remainder (~80 destinations).

Selects admin_1 provinces, dissolves them, and optionally subtracts
from a parent country polygon.
"""

import geopandas as gpd
from shapely.ops import unary_union

from .utils import to_feature, make_properties


def extract_admin1(dest, admin1_gdf, subunits_gdf=None, units_gdf=None):
    """Select and dissolve admin_1 provinces into a single feature.

    Uses adm0_a3 to filter the country, then matches province names
    from the admin1 list.
    """
    adm0 = dest.get("adm0_a3")
    admin1_names = dest.get("admin1", [])

    if not adm0 or not admin1_names:
        return None

    # Filter admin1 to the target country
    country_admin1 = admin1_gdf[admin1_gdf["adm0_a3"] == adm0]
    if len(country_admin1) == 0:
        # Try iso_a3
        country_admin1 = admin1_gdf[admin1_gdf["iso_a2"] == dest.get("iso_a2", "")]

    # Match province names (case-insensitive, partial match)
    matched = _match_provinces(country_admin1, admin1_names)

    if len(matched) == 0:
        print(f"  WARNING: No admin1 matches for {dest['name']} "
              f"(adm0={adm0}, names={admin1_names})")
        return None

    geom = matched.dissolve().geometry.iloc[0]
    return to_feature(geom, make_properties(dest))


def extract_remainder(dest, admin1_gdf, subunits_gdf, units_gdf, disputed_gdf=None):
    """Extract a country polygon minus specified admin_1 provinces.

    Gets the full country geometry from admin_0, then subtracts the
    dissolved geometry of specified admin1 provinces.  Also subtracts
    disputed areas listed in subtract_disputed, if present.
    """
    adm0 = dest.get("adm0_a3")
    subtract_names = dest.get("subtract_admin1", [])
    subtract_disputed = dest.get("subtract_disputed", [])

    if not adm0:
        return None

    # Get the full country geometry from admin_0
    country_geom = _get_country_geom(adm0, subunits_gdf, units_gdf)
    if country_geom is None:
        print(f"  WARNING: Could not find country {adm0} for remainder")
        return None

    result = country_geom

    # Subtract admin1 provinces
    if subtract_names:
        country_admin1 = admin1_gdf[admin1_gdf["adm0_a3"] == adm0]
        matched = _match_provinces(country_admin1, subtract_names)

        if len(matched) == 0:
            print(f"  WARNING: No admin1 to subtract for {dest['name']}")
        else:
            subtract_geom = matched.dissolve().geometry.iloc[0]
            result = result.difference(subtract_geom.buffer(0))

    # Subtract disputed areas
    if subtract_disputed and disputed_gdf is not None:
        for disp_name in subtract_disputed:
            for field in ["NAME", "BRK_NAME", "NAME_LONG"]:
                if field not in disputed_gdf.columns:
                    continue
                matches = disputed_gdf[
                    disputed_gdf[field].str.lower().str.contains(disp_name.lower(), na=False)
                ]
                if len(matches) > 0:
                    disp_geom = matches.dissolve().geometry.iloc[0]
                    result = result.difference(disp_geom.buffer(0))
                    break

    # Merge disputed areas into result
    merge_disputed = dest.get("merge_disputed", [])
    if merge_disputed and disputed_gdf is not None:
        for disp_name in merge_disputed:
            for field in ["NAME", "BRK_NAME", "NAME_LONG"]:
                if field not in disputed_gdf.columns:
                    continue
                matches = disputed_gdf[
                    disputed_gdf[field].str.lower().str.contains(disp_name.lower(), na=False)
                ]
                if len(matches) > 0:
                    result = unary_union([result, matches.dissolve().geometry.iloc[0]])
                    break

    if result.is_empty:
        print(f"  WARNING: Remainder is empty for {dest['name']}")
        return None

    if not result.is_valid:
        result = result.buffer(0)

    return to_feature(result, make_properties(dest))


def extract_disputed_remainder(dest, admin1_gdf, subunits_gdf, units_gdf, disputed_gdf):
    """Extract a country polygon minus disputed territories.

    Like extract_remainder but subtracts features from the disputed layer.
    """
    adm0 = dest.get("adm0_a3")
    subtract_disputed = dest.get("subtract_disputed", [])

    if not adm0:
        return None

    country_geom = _get_country_geom(adm0, subunits_gdf, units_gdf)
    if country_geom is None:
        return None

    if not subtract_disputed:
        return to_feature(country_geom, make_properties(dest))

    # Find disputed features to subtract
    subtract_geoms = []
    for disp_name in subtract_disputed:
        for field in ["NAME", "BRK_NAME", "NAME_LONG"]:
            if field in disputed_gdf.columns:
                matches = disputed_gdf[
                    disputed_gdf[field].str.lower().str.contains(disp_name.lower(), na=False)
                ]
                if len(matches) > 0:
                    subtract_geoms.append(matches.dissolve().geometry.iloc[0])
                    break

    if subtract_geoms:
        subtract_union = unary_union(subtract_geoms)
        result = country_geom.difference(subtract_union.buffer(0))
        if not result.is_valid:
            result = result.buffer(0)
        return to_feature(result, make_properties(dest))

    return to_feature(country_geom, make_properties(dest))


def _match_provinces(admin1_gdf, names):
    """Match admin1 provinces by name (case-insensitive, with fallbacks).

    Accumulates matches across multiple name fields so that provinces
    whose names contain diacritics can be found via whichever field
    stores the unaccented variant.
    """
    name_lower = [n.lower() for n in names]
    matched_idx = set()

    # Exact match — accumulate across all name fields
    for field in ["name", "name_en", "NAME", "NAME_EN"]:
        if field not in admin1_gdf.columns:
            continue
        mask = admin1_gdf[field].str.lower().isin(name_lower)
        matched_idx.update(admin1_gdf.index[mask])

    if matched_idx:
        return admin1_gdf.loc[list(matched_idx)]

    # Try contains match — accumulate across all name fields
    for field in ["name", "name_en", "NAME", "NAME_EN"]:
        if field not in admin1_gdf.columns:
            continue
        mask = admin1_gdf[field].str.lower().apply(
            lambda x: any(n in str(x) for n in name_lower) if x else False
        )
        matched_idx.update(admin1_gdf.index[mask])

    if matched_idx:
        return admin1_gdf.loc[list(matched_idx)]

    return admin1_gdf.iloc[0:0]  # empty


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
