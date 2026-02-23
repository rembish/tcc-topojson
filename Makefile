SHELL := /bin/bash
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
SIMPLIFY ?= 3%

.PHONY: all venv download build simplify markers validate dist serve clean format lint typecheck test check help

all: venv check download build simplify markers validate dist

venv: $(VENV)/bin/activate

$(VENV)/bin/activate: pyproject.toml
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"
	touch $(VENV)/bin/activate

download: venv
	$(PYTHON) -m src.download

build: venv
	$(PYTHON) -m src.build

simplify: output/merged.geojson
	npx mapshaper output/merged.geojson \
		-simplify $(SIMPLIFY) weighted keep-shapes \
		-o format=topojson output/tcc-330.json quantization=1e5

markers: output/merged.geojson
	SIMPLIFY=$(SIMPLIFY) $(PYTHON) -m src.markers

validate: venv
	$(PYTHON) validate.py

dist: output/tcc-330.json output/tcc-330-markers.json
	cp output/tcc-330.json tcc-330.json
	cp output/tcc-330-markers.json tcc-330-markers.json

serve:
	@echo "Serving viewer at http://localhost:8000/viewer.html"
	python3 -m http.server 8000

format:
	$(VENV)/bin/black src/ validate.py tests/
	$(VENV)/bin/ruff check --fix src/ validate.py tests/

lint:
	$(VENV)/bin/ruff check src/ validate.py
	$(VENV)/bin/black --check src/ validate.py

typecheck:
	$(VENV)/bin/mypy src/ validate.py

test:
	$(VENV)/bin/pytest tests/

check: lint typecheck test

clean:
	rm -rf data/ output/ $(VENV) node_modules/

help:
	@echo "TCC TopoJSON — available targets:"
	@echo ""
	@echo "  Pipeline:"
	@echo "    all          Run full pipeline with checks: venv check download build simplify markers validate dist"
	@echo "    venv         Create .venv and install all dependencies (incl. dev)"
	@echo "    download     Download Natural Earth shapefiles and Europe-Asia boundary"
	@echo "    build        Run Python build script → output/merged.geojson"
	@echo "    simplify     Run mapshaper simplification → output/tcc-330.json  (SIMPLIFY=3%)"
	@echo "    markers      Replace tiny polygons with centroid points → output/tcc-330-markers.json  (SIMPLIFY=3%)"
	@echo "    validate     Validate merged.geojson and tcc-330.json"
	@echo "    dist         Copy tcc-330.json and tcc-330-markers.json to project root"
	@echo ""
	@echo "  Code quality:"
	@echo "    format       Auto-format with Black + Ruff (--fix)"
	@echo "    lint         Check style with Ruff + Black (read-only)"
	@echo "    typecheck    Run mypy strict type checking"
	@echo "    test         Run pytest with coverage (≥80% required)"
	@echo "    check        Run lint + typecheck + test"
	@echo ""
	@echo "  Misc:"
	@echo "    serve        Serve viewer.html at http://localhost:8000/viewer.html"
	@echo "    clean        Remove data/, output/, .venv/, node_modules/"
	@echo "    help         Show this help message"
