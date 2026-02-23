SHELL := /bin/bash
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

.PHONY: all venv download build simplify validate dist clean format lint typecheck test check help

all: venv download build simplify validate dist

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
		-simplify 9% weighted keep-shapes \
		-o format=topojson output/tcc-330.json quantization=1e5

validate: venv
	$(PYTHON) validate.py

dist: output/tcc-330.json
	cp output/tcc-330.json tcc-330.json

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
	@echo "    all          Run the full pipeline: venv download build simplify validate dist"
	@echo "    venv         Create .venv and install all dependencies (incl. dev)"
	@echo "    download     Download Natural Earth shapefiles and Europe-Asia boundary"
	@echo "    build        Run Python build script → output/merged.geojson"
	@echo "    simplify     Run mapshaper simplification → output/tcc-330.json"
	@echo "    validate     Validate merged.geojson and tcc-330.json"
	@echo "    dist         Copy tcc-330.json to project root"
	@echo ""
	@echo "  Code quality:"
	@echo "    format       Auto-format with Black + Ruff (--fix)"
	@echo "    lint         Check style with Ruff + Black (read-only)"
	@echo "    typecheck    Run mypy strict type checking"
	@echo "    test         Run pytest with coverage (≥80% required)"
	@echo "    check        Run lint + typecheck + test"
	@echo ""
	@echo "  Misc:"
	@echo "    clean        Remove data/, output/, .venv/, node_modules/"
	@echo "    help         Show this help message"
