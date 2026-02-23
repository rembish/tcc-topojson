"""Validation script for TCC TopoJSON output."""

from __future__ import annotations

import json
import sys
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent / "output"

REQUIRED_PROPS = ["tcc_index", "name", "region", "sovereign", "type"]


def validate_geojson(path: Path) -> bool:
    """Validate the merged GeoJSON file.

    Checks:
    - Exactly 330 features present.
    - All tcc_index values are unique and span 1–330.
    - All required properties are non-null on every feature.
    - Every feature has a geometry.

    Args:
        path: Path to the ``merged.geojson`` file to validate.

    Returns:
        ``True`` if all checks pass, ``False`` otherwise.
    """
    print(f"Validating {path}...")

    with open(path) as f:
        data = json.load(f)

    features = data.get("features", [])
    print(f"  Features: {len(features)}")

    # Check count
    if len(features) != 330:
        print(f"  ERROR: Expected 330 features, got {len(features)}")

    # Check indices
    indices: set[int] = set()
    errors: list[str] = []
    for feat in features:
        props = feat.get("properties", {})
        idx = props.get("tcc_index")

        if idx is None:
            errors.append(f"Feature missing tcc_index: {props.get('name', '???')}")
            continue

        if idx in indices:
            errors.append(f"Duplicate tcc_index: {idx}")
        indices.add(idx)

        # Check required properties
        for prop in REQUIRED_PROPS:
            if props.get(prop) is None:
                errors.append(f"[{idx}] {props.get('name', '???')}: missing '{prop}'")

        # Check geometry exists
        geom = feat.get("geometry")
        if geom is None:
            errors.append(f"[{idx}] {props.get('name', '???')}: missing geometry")

    # Check all indices 1-330 present
    expected = set(range(1, 331))
    missing = sorted(expected - indices)
    extra = sorted(indices - expected)

    if missing:
        print(
            f"  Missing indices ({len(missing)}): {missing[:20]}{'...' if len(missing) > 20 else ''}"
        )
    if extra:
        print(f"  Extra indices: {extra}")

    for err in errors[:20]:
        print(f"  ERROR: {err}")
    if len(errors) > 20:
        print(f"  ... and {len(errors) - 20} more errors")

    # File size
    size_kb = path.stat().st_size / 1024
    print(f"  File size: {size_kb:.0f} KB")

    print(f"\n  Summary: {len(features)} features, {len(missing)} missing, {len(errors)} errors")
    return len(errors) == 0 and len(missing) == 0


def validate_topojson(path: Path) -> bool:
    """Validate the final TopoJSON file.

    Checks:
    - Total geometry count across all objects equals 330.
    - File size is within the 600 KB target (warns if exceeded).

    Args:
        path: Path to the ``tcc-330.json`` TopoJSON file to validate.

    Returns:
        ``True`` if the geometry count is exactly 330, ``False`` otherwise.
    """
    print(f"\nValidating {path}...")

    with open(path) as f:
        data = json.load(f)

    # TopoJSON has objects with geometries
    objects = data.get("objects", {})
    total_features = 0
    for name, obj in objects.items():
        geoms = obj.get("geometries", [])
        total_features += len(geoms)
        print(f"  Object '{name}': {len(geoms)} geometries")

    print(f"  Total features: {total_features}")

    size_kb = path.stat().st_size / 1024
    print(f"  File size: {size_kb:.0f} KB")

    if size_kb > 600:
        print("  WARNING: File exceeds 600 KB target")

    return total_features == 330


def main() -> None:
    """Validate both merged.geojson and tcc-330.json if present.

    Exits with code 1 if any check fails, code 0 if all pass.
    """
    ok = True

    geojson_path = OUTPUT_DIR / "merged.geojson"
    if geojson_path.exists():
        if not validate_geojson(geojson_path):
            ok = False
    else:
        print(f"GeoJSON not found: {geojson_path}")
        ok = False

    topojson_path = OUTPUT_DIR / "tcc-330.json"
    if topojson_path.exists():
        if not validate_topojson(topojson_path):
            ok = False
    else:
        print(f"TopoJSON not found: {topojson_path}")

    if not ok:
        print("\nValidation FAILED")
        sys.exit(1)
    else:
        print("\nValidation PASSED")


if __name__ == "__main__":
    main()
