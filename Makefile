ifeq ($(OS),Windows_NT)
VENV_PYTHON := .venv/Scripts/python.exe
CREATE_VENV := py -3.14 -m venv .venv
else
VENV_PYTHON := .venv/bin/python
CREATE_VENV := python3.14 -m venv .venv
endif

.PHONY: install run test

install:
	$(CREATE_VENV)
	$(VENV_PYTHON) -m pip install -r requirements.txt

run:
	$(VENV_PYTHON) -m uvicorn app.main:app --reload

test:
	$(VENV_PYTHON) -m pytest
