"""Tests for src/destinations.py — data integrity and structure."""

from __future__ import annotations

import pytest

from src.destinations import DESTINATIONS, EXTRACTIONS, get_destinations

EXPECTED_COUNT = 330
VALID_TYPES = {"country", "territory", "disputed", "subnational", "antarctic"}
VALID_REGIONS = {
    "Pacific Ocean",
    "North America",
    "Central America",
    "South America",
    "Caribbean",
    "Atlantic Ocean",
    "Europe & Mediterranean",
    "Antarctica",
    "Africa",
    "Middle East",
    "Indian Ocean",
    "Asia",
}


class TestDestinationsData:
    """Tests for the DESTINATIONS constant."""

    def test_count(self):
        assert len(DESTINATIONS) == EXPECTED_COUNT

    def test_indices_unique(self):
        indices = [d[0] for d in DESTINATIONS]
        assert len(indices) == len(set(indices)), "Duplicate tcc_index values found"

    def test_indices_sequential(self):
        indices = sorted(d[0] for d in DESTINATIONS)
        assert indices == list(range(1, EXPECTED_COUNT + 1))

    def test_name_nonempty(self):
        for row in DESTINATIONS:
            idx, name = row[0], row[1]
            assert name, f"Empty name at tcc_index={idx}"

    def test_region_valid(self):
        for row in DESTINATIONS:
            idx, region = row[0], row[2]
            assert region in VALID_REGIONS, f"Unknown region '{region}' at tcc_index={idx}"

    def test_type_valid(self):
        for row in DESTINATIONS:
            idx, dtype = row[0], row[7]
            assert dtype in VALID_TYPES, f"Unknown type '{dtype}' at tcc_index={idx}"

    def test_sovereign_nonempty(self):
        for row in DESTINATIONS:
            idx, sovereign = row[0], row[6]
            assert sovereign, f"Empty sovereign at tcc_index={idx}"

    def test_iso_n3_is_int_or_none(self):
        for row in DESTINATIONS:
            idx, iso_n3 = row[0], row[5]
            assert iso_n3 is None or isinstance(
                iso_n3, int
            ), f"iso_n3 must be int or None at tcc_index={idx}, got {type(iso_n3)}"

    def test_iso_a2_length(self):
        for row in DESTINATIONS:
            idx, iso_a2 = row[0], row[3]
            if iso_a2 is not None:
                assert len(iso_a2) == 2, f"iso_a2 must be 2 chars at tcc_index={idx}"

    def test_iso_a3_length(self):
        for row in DESTINATIONS:
            idx, iso_a3 = row[0], row[4]
            if iso_a3 is not None:
                assert len(iso_a3) == 3, f"iso_a3 must be 3 chars at tcc_index={idx}"


class TestExtractionsData:
    """Tests for the EXTRACTIONS constant."""

    VALID_STRATEGIES = {
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
    }

    def test_all_indices_in_range(self):
        for idx in EXTRACTIONS:
            assert 1 <= idx <= 330, f"EXTRACTIONS key {idx} out of range"

    def test_strategies_valid(self):
        for idx, cfg in EXTRACTIONS.items():
            strat = cfg.get("strategy")
            assert strat in self.VALID_STRATEGIES, f"Unknown strategy '{strat}' at tcc_index={idx}"

    def test_admin1_entries_have_admin1_list(self):
        for idx, cfg in EXTRACTIONS.items():
            if cfg.get("strategy") == "admin1":
                assert "admin1" in cfg, f"admin1 strategy missing 'admin1' key at tcc_index={idx}"
                assert isinstance(cfg["admin1"], list)
                assert len(cfg["admin1"]) > 0

    def test_island_bbox_have_bbox(self):
        for idx, cfg in EXTRACTIONS.items():
            if cfg.get("strategy") == "island_bbox":
                assert "bbox" in cfg, f"island_bbox missing 'bbox' at tcc_index={idx}"
                bbox = cfg["bbox"]
                assert len(bbox) == 4

    def test_clip_have_side(self):
        for idx, cfg in EXTRACTIONS.items():
            if cfg.get("strategy") == "clip":
                assert "side" in cfg, f"clip strategy missing 'side' at tcc_index={idx}"
                assert cfg["side"] in ("europe", "asia")

    def test_point_have_coords(self):
        for idx, cfg in EXTRACTIONS.items():
            if cfg.get("strategy") == "point":
                assert "lat" in cfg, f"point strategy missing 'lat' at tcc_index={idx}"
                assert "lon" in cfg, f"point strategy missing 'lon' at tcc_index={idx}"

    def test_antarctic_have_lon_or_sectors(self):
        for idx, cfg in EXTRACTIONS.items():
            if cfg.get("strategy") == "antarctic":
                has_single = "lon_west" in cfg and "lon_east" in cfg
                has_sectors = "sectors" in cfg
                assert (
                    has_single or has_sectors
                ), f"antarctic missing lon_west/lon_east or sectors at tcc_index={idx}"


class TestGetDestinations:
    """Tests for the get_destinations() function."""

    def test_returns_330(self):
        dests = get_destinations()
        assert len(dests) == EXPECTED_COUNT

    def test_all_have_strategy(self):
        for d in get_destinations():
            assert "strategy" in d, f"Missing strategy at tcc_index={d['tcc_index']}"

    def test_default_strategy_is_direct(self):
        # tcc_index 4 (Cook Islands) has no entry in EXTRACTIONS → should default to "direct"
        dests = {d["tcc_index"]: d for d in get_destinations()}
        assert 4 in dests
        assert dests[4]["strategy"] == "direct"

    def test_extraction_config_merged(self):
        # tcc_index 1 (Austral Islands) has island_bbox strategy in EXTRACTIONS
        dests = {d["tcc_index"]: d for d in get_destinations()}
        assert dests[1]["strategy"] == "island_bbox"
        assert "bbox" in dests[1]

    def test_base_fields_present(self):
        required = {"tcc_index", "name", "region", "sovereign", "type"}
        for d in get_destinations():
            assert required <= d.keys(), f"Missing base fields at tcc_index={d['tcc_index']}"

    def test_indices_1_to_330(self):
        indices = {d["tcc_index"] for d in get_destinations()}
        assert indices == set(range(1, 331))
