PYTHON ?= python3
LATEXMK ?= latexmk

.PHONY: data fit moose figures paper validate reproduce

data:
	$(PYTHON) scripts/extract_lawal_kim_figure3c.py \
		data/raw/GRL_Poromechanical_Measurements.xlsx \
		data/processed/lawal_kim_figure3c.csv
	$(PYTHON) scripts/verify_lawal_kim_figure3c.py \
		data/processed/lawal_kim_figure3c.csv

fit: data
	$(PYTHON) scripts/fit_pressure_dependent_biot.py \
		data/processed/lawal_kim_figure3c.csv \
		data/processed/crack_closure_fit.json \
		data/processed/crack_closure_predictions.csv \
		figures/lawal_kim_biot_replication.png

moose: fit
	$(PYTHON) scripts/run_moose_pressure_paths.py

figures: moose
	$(PYTHON) scripts/plot_moose_replication.py

paper: figures
	$(LATEXMK) -lualatex -interaction=nonstopmode -halt-on-error \
		-outdir=paper/build paper/main.tex

validate:
	$(PYTHON) scripts/validate_repository.py

reproduce: paper validate
