"""Shared type aliases and TypedDicts for TCC TopoJSON build."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, TypedDict

# ---------------------------------------------------------------------------
# Primitive aliases
# ---------------------------------------------------------------------------

type Bbox = tuple[float, float, float, float]  # (west, south, east, north)
type Coordinate = tuple[float, float]
type CoordList = list[Coordinate]
type GeoJsonProperties = dict[str, str | int | float | None]

# A complete GeoJSON Feature dict as produced by to_feature()
type TccFeature = dict[str, Any]

# A merged destination config dict as returned by get_destinations()
type TccDestination = dict[str, Any]

# ---------------------------------------------------------------------------
# Extraction strategy literals
# ---------------------------------------------------------------------------

type ExtractionStrategy = Literal[
    "direct",
    "subunit",
    "admin1",
    "remainder",
    "group_remainder",
    "clip",
    "disputed",
    "disputed_remainder",
    "disputed_subtract",
    "island_bbox",
    "antarctic",
    "point",
]

# ---------------------------------------------------------------------------
# Feature properties TypedDict
# ---------------------------------------------------------------------------


class TccBaseProps(TypedDict):
    """Standard properties carried by every TCC output feature."""

    tcc_index: int
    name: str
    region: str
    iso_a2: str | None
    iso_a3: str | None
    iso_n3: int | None
    sovereign: str
    type: Literal["country", "territory", "disputed", "subnational", "antarctic"]


# ---------------------------------------------------------------------------
# Conditional imports (type-checking only)
# ---------------------------------------------------------------------------

if TYPE_CHECKING:
    import geopandas as gpd

    GeoDataFrame = gpd.GeoDataFrame
