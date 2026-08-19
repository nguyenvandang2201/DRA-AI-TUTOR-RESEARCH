# Cac tac vu thuong dung cua kho DRA AI Tutor Research.
# Tren Windows PowerShell, dung ./tasks.ps1 <ten-tac-vu> thay cho make.

PYTHON ?= python

.PHONY: help validate stats splits export test baseline report all check clean

help:  ## Liet ke cac tac vu
	@grep -E '^[a-z-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-10s %s\n", $$1, $$2}'

validate:  ## Kiem dinh schema va quy uoc du lieu
	$(PYTHON) tools/validate_datasets.py --strict

stats:  ## Sinh lai docs/dataset_stats.md
	$(PYTHON) tools/dataset_stats.py

splits:  ## Sinh lai datasets/splits/
	$(PYTHON) tools/make_splits.py

export:  ## Sinh lai datasets/exports/
	$(PYTHON) tools/export_dataset.py

test:  ## Chay toan bo test
	$(PYTHON) -m unittest discover -s tests -v

baseline:  ## Chay danh gia baseline dinh tuyen
	$(PYTHON) tools/baseline_router.py

report:  ## Sinh lai docs/baseline_results.md
	$(PYTHON) tools/baseline_router.py --report

all: validate splits stats export test  ## Sinh lai moi thu roi chay test

check:  ## Kiem tra moi file sinh tu dong da cap nhat (dung cho CI)
	$(PYTHON) tools/validate_datasets.py --strict
	$(PYTHON) tools/make_splits.py --check
	$(PYTHON) tools/dataset_stats.py --check
	$(PYTHON) tools/export_dataset.py --check
	$(PYTHON) -m unittest discover -s tests

clean:  ## Xoa cache Python
	rm -rf tools/__pycache__ tests/__pycache__
