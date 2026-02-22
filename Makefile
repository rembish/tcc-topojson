SHELL := /bin/bash
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

.PHONY: all venv download build simplify validate dist clean

all: venv download build simplify validate dist

venv: $(VENV)/bin/activate

$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
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

clean:
	rm -rf data/ output/ $(VENV) node_modules/
