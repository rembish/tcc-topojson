"""Main build orchestrator for TCC TopoJSON.

Loads source data, runs all extractors, and outputs merged.geojson.
"""

import json
from pathlib import Path

import geopandas as gpd

from .destinations import get_destinations
from .category_a import extract_direct, extract_subunit
from .category_b import extract_admin1, extract_remainder, extract_disputed_remainder
from .category_c import (
    extract_clip,
    extract_disputed,
    extract_island_bbox,
    extract_group_remainder,
    generate_antarctic_wedge,
    generate_point,
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"


def load_data():
    """Load all source GeoDataFrames."""
    print("Loading source data...")
    subunits = gpd.read_file(DATA_DIR / "ne_10m_admin_0_map_subunits.shp")
    units = gpd.read_file(DATA_DIR / "ne_10m_admin_0_map_units.shp")
    admin1 = gpd.read_file(DATA_DIR / "ne_10m_admin_1_states_provinces.shp")
    disputed = gpd.read_file(DATA_DIR / "ne_10m_admin_0_disputed_areas.shp")

    print(f"  Subunits: {len(subunits)} features")
    print(f"  Units: {len(units)} features")
    print(f"  Admin1: {len(admin1)} features")
    print(f"  Disputed: {len(disputed)} features")

    return subunits, units, admin1, disputed


def build_features(subunits, units, admin1, disputed):
    """Build all 330 TCC features."""
    destinations = get_destinations()
    print(f"\nBuilding {len(destinations)} TCC destinations...")

    # Load Antarctica coastline for clipping wedge sectors
    antarctica_geom = None
    ata = units[units["ADM0_A3"] == "ATA"]
    if len(ata) > 0:
        antarctica_geom = ata.dissolve().geometry.iloc[0]

    built = {}  # tcc_index -> feature
    deferred = []  # destinations that depend on other built features

    # First pass: build all non-dependent features
    for dest in destinations:
        strategy = dest.get("strategy", "direct")

        if strategy == "group_remainder":
            deferred.append(dest)
            continue

        feature = _extract_feature(dest, strategy, subunits, units, admin1, disputed, built, antarctica_geom)

        if feature:
            built[dest["tcc_index"]] = feature
        else:
            print(f"  FAILED: [{dest['tcc_index']}] {dest['name']} (strategy={strategy})")

    # Second pass: build group_remainder features (depend on first pass results)
    for dest in deferred:
        feature = extract_group_remainder(dest, subunits, units, built)
        if feature:
            built[dest["tcc_index"]] = feature
        else:
            print(f"  FAILED: [{dest['tcc_index']}] {dest['name']} (group_remainder)")

    return built


def _extract_feature(dest, strategy, subunits, units, admin1, disputed, built, antarctica_geom=None):
    """Dispatch to the appropriate extraction function based on strategy."""
    idx = dest["tcc_index"]
    name = dest["name"]

    if strategy == "direct":
        return extract_direct(dest, subunits, units)

    elif strategy == "subunit":
        return extract_subunit(dest, subunits)

    elif strategy == "admin1":
        return extract_admin1(dest, admin1, subunits, units)

    elif strategy == "remainder":
        return extract_remainder(dest, admin1, subunits, units, disputed)

    elif strategy in ("disputed_remainder", "disputed_subtract"):
        return extract_disputed_remainder(dest, admin1, subunits, units, disputed)

    elif strategy == "clip":
        return extract_clip(dest, subunits, units, built)

    elif strategy == "disputed":
        return extract_disputed(dest, disputed)

    elif strategy == "island_bbox":
        return extract_island_bbox(dest, subunits, units, admin1)

    elif strategy == "antarctic":
        return generate_antarctic_wedge(dest, antarctica_geom)

    elif strategy == "point":
        return generate_point(dest)

    else:
        print(f"  Unknown strategy '{strategy}' for [{idx}] {name}")
        return None


def write_geojson(features, output_path):
    """Write features dict to a GeoJSON FeatureCollection."""
    # Sort by tcc_index
    sorted_features = [features[i] for i in sorted(features.keys())]

    collection = {
        "type": "FeatureCollection",
        "features": sorted_features,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(collection, f)

    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"\nWrote {len(sorted_features)} features to {output_path} ({size_mb:.1f} MB)")


def main():
    subunits, units, admin1, disputed = load_data()
    features = build_features(subunits, units, admin1, disputed)

    total = len(features)
    missing = 330 - total
    print(f"\nBuilt {total}/330 features ({missing} missing)")

    if missing > 0:
        all_indices = set(range(1, 331))
        built_indices = set(features.keys())
        missing_indices = sorted(all_indices - built_indices)
        destinations = {d["tcc_index"]: d for d in get_destinations()}
        print("Missing destinations:")
        for idx in missing_indices:
            d = destinations.get(idx, {})
            print(f"  [{idx}] {d.get('name', '???')} (strategy={d.get('strategy', '???')})")

    output_path = OUTPUT_DIR / "merged.geojson"
    write_geojson(features, output_path)


if __name__ == "__main__":
    main()
