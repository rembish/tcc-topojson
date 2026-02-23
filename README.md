# TCC TopoJSON

[![npm](https://img.shields.io/npm/v/tcc-topojson)](https://www.npmjs.com/package/tcc-topojson)

TopoJSON world map with **330 polygons** matching the [Travelers' Century Club](https://travelerscenturyclub.org/) destination list. No existing open-source project provides this — NomadMania's regions are proprietary, TCC publishes no polygon data, and `topojson/world-atlas` is countries-only.

## Files

Two files are published, both covering all 330 TCC destinations:

| File | Size | Description |
|------|-----:|-------------|
| `tcc-330.json` | ~248 KB | Full polygons for every destination |
| `tcc-330-markers.json` | ~296 KB | Tiny territories (< 1 000 km²) replaced with centroid point markers; better for world-scale rendering |

In `tcc-330-markers.json` the 83 smallest destinations (Nauru, Liechtenstein, Grenada, most Caribbean islands, etc.) appear as `Point` geometries with `"marker": true` in their properties, while the remaining 247 larger territories keep their polygon shapes. Both geometry types share the same properties schema and tooltip behaviour.

## Usage

### CDN (jsDelivr)

```
https://cdn.jsdelivr.net/npm/tcc-topojson@1.1.0/tcc-330.json
https://cdn.jsdelivr.net/npm/tcc-topojson@1.1.0/tcc-330-markers.json
```

### npm

```sh
npm install tcc-topojson
```

Package page: [npmjs.com/package/tcc-topojson](https://www.npmjs.com/package/tcc-topojson)

### JavaScript

```js
const resp = await fetch(
  "https://cdn.jsdelivr.net/npm/tcc-topojson@1.1.0/tcc-330.json"
);
const topology = await resp.json();
```

### D3.js — polygons only

```js
import { feature } from "topojson-client";

// All objects are merged (handles both single- and multi-object topologies)
const allFeatures = Object.values(topology.objects)
  .flatMap(obj => feature(topology, obj).features);

const projection = d3.geoNaturalEarth1();
const path = d3.geoPath(projection);

svg.selectAll("path")
  .data(allFeatures.filter(f => f.geometry.type !== "Point"))
  .join("path")
  .attr("d", path)
  .attr("fill", d => visited.has(d.properties.tcc_index) ? "#4a9" : "#ccc");
```

### D3.js — markers file (polygons + point circles)

```js
import { feature } from "topojson-client";

const resp = await fetch(
  "https://cdn.jsdelivr.net/npm/tcc-topojson@1.1.0/tcc-330-markers.json"
);
const topology = await resp.json();

const allFeatures = Object.values(topology.objects)
  .flatMap(obj => feature(topology, obj).features);

const polygons = allFeatures.filter(
  f => f.geometry.type === "Polygon" || f.geometry.type === "MultiPolygon"
);
const markers = allFeatures.filter(f => f.geometry.type === "Point");

// Draw polygon features
svg.selectAll("path")
  .data(polygons)
  .join("path")
  .attr("d", path)
  .attr("fill", d => colorByRegion(d.properties.region));

// Draw point markers
svg.selectAll("circle")
  .data(markers)
  .join("circle")
  .attr("r", 3)
  .attr("cx", d => projection(d.geometry.coordinates)[0])
  .attr("cy", d => projection(d.geometry.coordinates)[1])
  .attr("fill", d => colorByRegion(d.properties.region));
```

## Feature properties

All 330 features in both files share this schema:

| Property | Type | Description |
|----------|------|-------------|
| `tcc_index` | `number` | TCC destination number (1–330) |
| `name` | `string` | Destination name |
| `region` | `string` | TCC region |
| `iso_a2` | `string \| null` | ISO 3166-1 alpha-2 code |
| `iso_a3` | `string \| null` | ISO 3166-1 alpha-3 code |
| `iso_n3` | `number \| null` | ISO 3166-1 numeric code |
| `sovereign` | `string` | Sovereign state name |
| `type` | `string` | `"country"`, `"territory"`, `"disputed"`, `"subnational"`, or `"antarctic"` |
| `marker` | `boolean` | `true` if this feature is a Point marker (markers file only) |
| `area_km2` | `number \| null` | Area in km² (markers file only, for classified features) |

## Coverage

| Region | Count | Indices |
|--------|------:|---------|
| Pacific Ocean | 40 | 1–40 |
| North America | 6 | 41–46 |
| Central America | 7 | 47–53 |
| South America | 14 | 54–67 |
| Caribbean | 31 | 68–98 |
| Atlantic Ocean | 14 | 99–112 |
| Europe & Mediterranean | 68 | 113–180 |
| Antarctica | 7 | 181–187 |
| Africa | 55 | 188–242 |
| Middle East | 21 | 243–263 |
| Indian Ocean | 15 | 264–278 |
| Asia | 52 | 279–330 |

## Building from source

Prerequisites: **Python 3.12+**, **Node.js** (for `npx mapshaper`).

```sh
make all
```

Full pipeline:

1. **venv** — creates `.venv` and installs Python dependencies
2. **check** — lint (`ruff`, `black`), type-check (`mypy`), tests (`pytest`, ≥ 80% coverage)
3. **download** — fetches Natural Earth 10m shapefiles and the Trubetskoy Europe–Asia boundary
4. **build** — assembles 330 GeoJSON features via direct matches, admin-1 merges, transcontinental clips, island extractions, and Antarctic wedges → `output/merged.geojson`
5. **simplify** — runs `mapshaper` at **3% vertex retention** → `output/tcc-330.json` (~248 KB)
6. **markers** — replaces polygons < 1 000 km² with centroid point markers → `output/tcc-330-markers.json` (~296 KB)
7. **validate** — checks all 330 indices are present and valid
8. **dist** — copies both files to the repo root

### Tuning simplification

The simplification level defaults to `3%` (vertex retention) and is controlled by the `SIMPLIFY` environment variable:

```sh
# More detail, larger file (~340 KB)
SIMPLIFY=5% make simplify markers

# More aggressive, smaller file (~204 KB)
SIMPLIFY=2% make simplify markers
```

Tip: `3%` was chosen after visual comparison — it matches `world-110m.json` quality at world scale while cutting the original 9% output by more than half.

## Visual testing

A browser-based viewer is included:

```sh
make serve
# → http://localhost:8000/viewer.html
```

The viewer renders all 330 features coloured by TCC region. A **Full / Markers** toggle lets you switch between the two files. Hover any feature for a tooltip with name, region, sovereign state, TCC index, ISO code, and area.

## Data sources & attribution

- [Natural Earth 10m](https://www.naturalearthdata.com/) — public domain
- [Trubetskoy Europe–Asia boundary](https://sashamaps.net/docs/resources/europe-asia-boundary/) — Sasha Trubetskoy, free with attribution

## Changelog

### 1.1.0

- Add `tcc-330-markers.json`: 83 tiny territories (< 1 000 km²) replaced with centroid point markers for cleaner world-scale rendering
- Reduce default simplification from 9% → 3%, cutting file size by ~52% (524 KB → 248 KB) with no visible quality loss at world scale
- `SIMPLIFY` env var for tunable simplification level (`SIMPLIFY=5% make simplify markers`)
- `make serve` for one-command local preview
- Interactive viewer with Full / Markers toggle, per-region colour legend, and file-size display

### 1.0.0

- Initial release: 330 TCC destinations as TopoJSON polygons

## License

[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) — see [LICENSE](LICENSE) for details.
