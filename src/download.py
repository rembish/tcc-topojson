"""Download Natural Earth 10m shapefiles and Trubetskoy Europe-Asia boundary."""

import io
import zipfile
from pathlib import Path

import requests

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

NE_BASE = "https://naciscdn.org/naturalearth/10m/cultural"

NE_DATASETS = [
    "ne_10m_admin_0_map_subunits",
    "ne_10m_admin_0_map_units",
    "ne_10m_admin_1_states_provinces",
    "ne_10m_admin_0_disputed_areas",
]

TRUBETSKOY_URL = (
    "https://raw.githubusercontent.com/sashatrubetskoy/asia_europe_border/"
    "master/asia_europe_border.geojson"
)


def download_ne_dataset(name: str) -> None:
    """Download and extract a Natural Earth shapefile zip."""
    target = DATA_DIR / f"{name}.shp"
    if target.exists():
        print(f"  {name} — already exists, skipping")
        return

    url = f"{NE_BASE}/{name}.zip"
    print(f"  Downloading {name}...")
    resp = requests.get(url, timeout=120)
    resp.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        zf.extractall(DATA_DIR)
    print(f"  {name} — done")


def download_boundary() -> None:
    """Download the Trubetskoy Europe-Asia boundary GeoJSON."""
    target = DATA_DIR / "europe_asia_boundary.geojson"
    if target.exists():
        print("  Europe-Asia boundary — already exists, skipping")
        return

    print("  Downloading Europe-Asia boundary...")
    resp = requests.get(TRUBETSKOY_URL, timeout=60)
    resp.raise_for_status()
    target.write_text(resp.text)
    print("  Europe-Asia boundary — done")


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print("Downloading source data...")

    for name in NE_DATASETS:
        download_ne_dataset(name)

    download_boundary()
    print("All downloads complete.")


if __name__ == "__main__":
    main()
