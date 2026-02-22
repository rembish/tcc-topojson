# TCC TopoJSON — Open-Source TCC-Compatible World Map

## Goal

Build a public-domain TopoJSON world map with **330 polygons** matching the [Travelers' Century Club](https://travelerscenturyclub.org/) destination list. No existing open-source project provides this — NomadMania's 1,301 regions are proprietary, TCC has no polygon data, `topojson/world-atlas` is countries-only and archived, GADM is non-redistributable.

## TCC Destination List

330 destinations across 10 regions: Pacific Ocean (40), North America (6), Central America (7), South America (14), Caribbean (31), Atlantic Ocean (14), Europe & Mediterranean (68), Antarctica (7), Africa (55), Middle East (21), Indian Ocean (15), Asia (52).

The full list with indices is maintained by TCC at https://travelerscenturyclub.org/countries-and-territories/alphabetical-list/

## Source Data

All sources must be compatible with public-domain or permissive licensing:

| Source | License | What it provides |
|--------|---------|-----------------|
| [Natural Earth 10m](https://github.com/nvkelso/natural-earth-vector) | **Public domain** | Base polygons: countries, territories, admin_1 subdivisions |
| [Trubetskoy Europe-Asia boundary](https://sashamaps.net/docs/resources/europe-asia-boundary/) | Free w/ attribution | High-precision boundary along Urals, Caucasus, Bosphorus for transcontinental splits |
| [geoBoundaries](https://www.geoboundaries.org/) | CC-BY | Supplementary admin_1/admin_2 where NE is insufficient |
| [OpenStreetMap](https://www.openstreetmap.org/) | ODbL | Supplementary coastlines, island boundaries |

**Do NOT use GADM** — its license prohibits redistribution.

## Natural Earth 10m Layers

| Layer | Features | Use |
|-------|----------|-----|
| `ne_10m_admin_0_map_subunits` | ~360 | Base: countries + overseas territories + England/Scotland/Wales/NI/Corsica/Alaska |
| `ne_10m_admin_0_map_units` | ~298 | Fallback for territories not in subunits |
| `ne_10m_admin_1_states_provinces` | ~4,500 | Sub-national splits: UAE emirates, Indonesian islands, Greek/Spanish/Italian islands, Hainan, Tibet, Zanzibar, Kaliningrad, etc. |
| `ne_10m_admin_0_breakaway_disputed_areas` | ~30 | Abkhazia, South Ossetia, Transnistria, Northern Cyprus, Kashmir, Somaliland |

Key NE properties per feature: `SOV_A3`, `ADM0_A3`, `GU_A3`, `SU_A3`, `ISO_A2`, `ISO_A3`, `ISO_N3`, `NAME`, `TYPE`, `SOVEREIGNT`, `ADMIN`, `CONTINENT`, `SUBREGION`.

## Coverage Breakdown

### Category A: Direct NE feature (~180 destinations)

Sovereign nations and already-separated territories. Just filter from `admin_0_map_units` or `admin_0_map_subunits`.

### Category B: admin_1 extraction/merge (~80 destinations)

Select and dissolve admin_1 provinces into TCC regions:

| TCC Destination | admin_1 Strategy |
|----------------|-----------------|
| England, Scotland, Wales, NI | `map_subunits` has these directly |
| Alaska, Hawaiian Islands | US admin_1 or `map_subunits` |
| Corsica | `map_subunits` has this directly |
| Sardinia, Sicily | Italy admin_1 (Sardegna, Sicilia regions) |
| Balearic Islands, Canary Islands | Spain admin_1 (Illes Balears, Canarias) |
| Crete, Ionian Islands | Greece admin_1 (Kriti, Ionia Nisia peripheries) |
| Greek Aegean Islands | Merge Greece admin_1: North Aegean + South Aegean |
| Abu Dhabi, Dubai, Sharjah, Ajman, Fujairah, Ras Al Khaimah, Umm Al Qaiwain | UAE admin_1 (7 emirates) |
| Java | Merge Indonesia admin_1: Jakarta, Banten, West Java, Central Java, East Java, Yogyakarta |
| Kalimantan | Merge 5 Kalimantan provinces |
| Sulawesi | Merge 6 Sulawesi provinces |
| Sumatra | Merge ~10 Sumatran provinces |
| Maluku Islands | Merge Maluku + North Maluku |
| Lesser Sunda Islands | Merge Bali, NTB, NTT |
| Papua (Irian Jaya) | Merge Papua provinces |
| Hainan Island, Tibet | China admin_1 |
| Sabah, Sarawak | Malaysia admin_1 |
| Kaliningrad | Russia admin_1 (Kaliningrad Oblast) |
| Nakhchivan | Azerbaijan admin_1 |
| Zanzibar | Tanzania admin_1 |
| Tasmania | Australia admin_1 |
| Prince Edward Island | Canada admin_1 |
| Aland Islands | Finland admin_1 |
| Madeira, Azores | Portugal admin_1 |
| Jeju Island | South Korea admin_1 |
| Sikkim, Andaman-Nicobar, Lakshadweep | India admin_1 |
| Ryukyu Islands (Okinawa) | Japan admin_1 |
| San Andres & Providencia | Colombia admin_1 |
| Galapagos Islands | Ecuador admin_1 |
| Nueva Esparta (Margarita) | Venezuela admin_1 |
| Srpska | Bosnia admin_1 |
| Ceuta & Melilla | Spain admin_1 |
| Cabinda | Angola admin_1 |
| Spitsbergen (Svalbard) | NE map_units (Norwegian dependency) |
| Equatorial Guinea (Bioko vs Rio Muni) | Split via admin_1 |

### Category C: Custom GIS work (~55 destinations)

#### Transcontinental splits

| Split | Approach |
|-------|----------|
| **Russia → Europe + Asia** | Clip with Trubetskoy Europe-Asia boundary. The boundary cuts through several oblasts (Chelyabinsk, Sverdlovsk), so a line clip on the country polygon is cleaner than merging admin_1. |
| **Turkey → Europe + Asia** | Same boundary line. East Thrace = European part (~3% of area). Istanbul province spans both sides — needs clip, not admin_1 selection. |
| **Egypt → Africa + Sinai** | Select North Sinai + South Sinai governorates from admin_1 (cleaner than Suez Canal clip). |

#### Disputed/breakaway territories

Use `ne_10m_admin_0_breakaway_disputed_areas` overlay where available, otherwise extract from admin_1:
- Abkhazia, South Ossetia (from Georgia)
- Transnistria (from Moldova)
- Somaliland (from Somalia)
- Northern Cyprus (from Cyprus)
- Kashmir (NE disputed layer)
- Western Sahara (already separate in NE)
- Kosovo (already separate in NE)
- Palestine (already in NE)

#### Island extractions from MultiPolygon

These require identifying specific polygon rings within a parent feature by coordinates:
- Lampedusa (from Italy/Sicilia)
- Socotra (from Yemen)
- Ogasawara/Bonin Islands (from Japan/Tokyo)
- Easter Island, Juan Fernandez (from Chile)
- Fernando de Noronha (from Brazil)
- Chatham Islands, Lord Howe Island (from NZ/Australia)
- St. Helena / Ascension / Tristan da Cunha (split NE's single feature into 3)
- Rodrigues Island (from Mauritius)
- Zil Elwannyen Sesel / outer Seychelles (from Seychelles)
- Line/Phoenix Islands (from Kiribati)
- Bismarck Archipelago (from PNG)

#### Antarctic claim sectors (7)

Generate as GeoJSON wedge polygons from South Pole to 60°S:
- Argentine Antarctica, Australian Antarctic Territory, British Antarctic Territory, Chilean Antarctic Territory, French Antarctica (Adélie + Kerguelen), New Zealand Antarctica (Ross Dependency), Norwegian Dependencies (Bouvet + Peter I + Queen Maud Land)

#### Tiny islands — point markers, not polygons

Some TCC destinations are too small for meaningful polygons at web scale. These should be represented as point features with a flag for marker rendering:
- Midway Island, Wake Island, Tokelau, Niue, Nauru, Tuvalu, and similar

## Build Pipeline

```
# 1. Download Natural Earth 10m shapefiles
#    admin_0_map_subunits, admin_0_map_units, admin_1_states_provinces,
#    breakaway_disputed_areas

# 2. Convert shapefiles to GeoJSON
ogr2ogr -f GeoJSON subunits.geojson ne_10m_admin_0_map_subunits.shp
ogr2ogr -f GeoJSON admin1.geojson ne_10m_admin_1_states_provinces.shp
ogr2ogr -f GeoJSON disputed.geojson ne_10m_admin_0_breakaway_disputed_areas.shp

# 3. Build TCC features via a script that:
#    - Selects Category A features from subunits/map_units
#    - Selects and dissolves Category B admin_1 provinces
#    - Clips transcontinental countries with boundary line
#    - Extracts island polygons from MultiPolygons
#    - Generates Antarctic wedges
#    - Assigns TCC index (1-330) and metadata to each feature

# 4. Merge all features into one GeoJSON collection

# 5. Simplify and convert to TopoJSON
mapshaper merged.geojson \
  -simplify 15% weighted keep-shapes \
  -o format=topojson tcc-330.json quantization=1e5
```

Target output: **`tcc-330.json`** (~300-600 KB), one TopoJSON with 330 features.

### Feature properties

Each feature in the output should have:
- `tcc_index` (1-330) — TCC destination number
- `name` — TCC destination name
- `region` — TCC region (Pacific Ocean, Europe & Mediterranean, etc.)
- `iso_a2` — ISO alpha-2 where applicable (null for sub-national)
- `iso_a3` — ISO alpha-3 where applicable
- `iso_n3` — ISO numeric where applicable
- `sovereign` — Sovereign state name
- `type` — "country", "territory", "disputed", "subnational", "antarctic"

## Tools Required

- `ogr2ogr` (GDAL) — shapefile/GeoJSON conversion and filtering
- `mapshaper` — simplification, dissolve, clip, merge operations
- `topojson` CLI (`topojson-server`, `topojson-client`) — TopoJSON encoding
- Python or Node.js — build script for the assembly logic
- Optional: `turf.js` for geometric operations (clip, boolean difference)

## Testing

- Verify all 330 TCC indices present in output
- Verify no overlapping polygons (topology should handle shared borders)
- Verify transcontinental splits don't leave gaps or slivers
- Visual check: render in browser with D3 or react-simple-maps
- File size check: target < 600 KB

## Related

- **Consumer:** `rembish_org` project uses the TopoJSON for its travel map (`/travels` page)
- Current map: `rembish_org/app/frontend/public/world-110m.json` (173 features, Visionscarto NE 110m)
- Current mapping: `un_countries.map_region_codes` → TopoJSON `geo.id` (ISO numeric)
- The output `tcc-330.json` will need a different ID scheme (TCC index or a composite key) since many features won't have ISO numeric codes
