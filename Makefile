PYTHON ?= python3
LATEXMK ?= latexmk
MOOSE_ENV := agent_environment/skills/setup-moose-conda/scripts/moose_conda_env.sh

.PHONY: sync-check sync-pull sync-push build test mandel figures paper provenance validate reproduce

sync-check:
	tools/sync_biot_moose.py check

sync-pull:
	tools/sync_biot_moose.py pull

sync-push:
	tools/sync_biot_moose.py push

build:
	$(MOOSE_ENV) run -- $(MAKE) -C moose_app -j1

test: build
	cd moose_app && ../$(MOOSE_ENV) run -- $(PYTHON) \
		../.agent-runtime/moose/python/run_tests --no-color -j1 --re=mandel_water_q2_q1

mandel: test
	$(PYTHON) validation/scripts/check_mandel_implicit_biot.py

figures:
	MPLCONFIGDIR=.agent-runtime/matplotlib $(PYTHON) scripts/plot_mandel_extended_results.py
	MPLCONFIGDIR=.agent-runtime/matplotlib $(PYTHON) scripts/plot_poroplastic_delta_b.py
	MPLCONFIGDIR=.agent-runtime/matplotlib $(PYTHON) scripts/plot_poroplastic_b_feedback.py
	MPLCONFIGDIR=.agent-runtime/matplotlib $(PYTHON) scripts/plot_poroplastic_load_unload.py
	MPLCONFIGDIR=.agent-runtime/matplotlib $(PYTHON) scripts/plot_tensorial_load_unload.py
	MPLCONFIGDIR=.agent-runtime/matplotlib $(PYTHON) scripts/plot_sandstone_comparison.py

paper:
	$(LATEXMK) -lualatex -interaction=nonstopmode -halt-on-error \
		-outdir=paper/build paper/main.tex

provenance:
	$(PYTHON) scripts/update_validation_provenance.py

validate:
	$(PYTHON) scripts/validate_repository.py

reproduce: sync-check test mandel figures paper provenance validate
