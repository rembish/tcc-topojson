# TCC TopoJSON

TopoJSON world map with **330 polygons** matching the [Travelers' Century Club](https://travelerscenturyclub.org/) destination list.

## Usage

Fetch from a CDN:

```
https://cdn.jsdelivr.net/gh/rembish/tcc-topojson@master/tcc-330.json
```

Or install via npm:

```sh
npm install rembish/tcc-topojson
```

### JavaScript

```js
const response = await fetch(
  "https://cdn.jsdelivr.net/gh/rembish/tcc-topojson@master/tcc-330.json"
);
const topology = await response.json();
```

### D3.js

```js
import { feature } from "topojson-client";

const geojson = feature(topology, topology.objects.tcc);

// Render with D3
const projection = d3.geoNaturalEarth1();
const path = d3.geoPath(projection);

svg
  .selectAll("path")
  .data(geojson.features)
  .join("path")
  .attr("d", path)
  .attr("fill", (d) => (visited.has(d.properties.tcc_index) ? "#4a9" : "#ccc"));
```

## Feature properties

Each of the 330 features includes:

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

Prerequisites: **Python 3.10+**, **Node.js** (for `npx mapshaper`).

```sh
make all
```

This runs the full pipeline:

1. **venv** — creates a Python virtualenv and installs dependencies (`shapely`, `geopandas`, `fiona`, `pyproj`)
2. **download** — fetches Natural Earth 10m shapefiles and the Trubetskoy Europe–Asia boundary
3. **build** — assembles 330 GeoJSON features (direct matches, admin-1 merges, transcontinental clips, island extractions, Antarctic wedges)
4. **simplify** — runs `npx mapshaper` to simplify geometries (9% weighted) and convert to TopoJSON
5. **validate** — checks all 330 indices are present
6. **dist** — copies `output/tcc-330.json` to the repo root

## Data sources & attribution

- [Natural Earth 10m](https://www.naturalearthdata.com/) — public domain
- [Trubetskoy Europe–Asia boundary](https://sashamaps.net/docs/resources/europe-asia-boundary/) — Sasha Trubetskoy, free with attribution

## License

[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) — see [LICENSE](LICENSE) for details.
