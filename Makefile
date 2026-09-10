PYTHON ?= python3
LATEXMK ?= latexmk
MOOSE_ENV := agent_environment/skills/setup-moose-conda/scripts/moose_conda_env.sh

.PHONY: sync-check sync-pull sync-push build test derivation mandel plastic figures paper provenance validate reproduce

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
		../.agent-runtime/moose/python/run_tests --no-color -j1

mandel: test
	$(MOOSE_ENV) run -- $(PYTHON) scripts/reproduce_mandel_publication.py --verify-benchmark --curate

derivation:
	$(PYTHON) validation/scripts/check_stress_trace_derivation.py
	$(MOOSE_ENV) run -- $(PYTHON) validation/scripts/check_stress_trace_biot_fraction.py

plastic:
	$(MOOSE_ENV) run -- $(PYTHON) validation/scripts/check_implicit_poroplastic.py --curate

figures:
	MPLCONFIGDIR=.agent-runtime/matplotlib $(MOOSE_ENV) run -- $(PYTHON) scripts/plot_mandel_extended_results.py
	MPLCONFIGDIR=.agent-runtime/matplotlib $(MOOSE_ENV) run -- $(PYTHON) scripts/plot_implicit_poroplastic.py

paper:
	$(LATEXMK) -lualatex -interaction=nonstopmode -halt-on-error \
		-outdir=paper/build paper/main.tex

provenance:
	$(PYTHON) scripts/update_validation_provenance.py

validate:
	$(PYTHON) scripts/validate_repository.py

reproduce: sync-check derivation test mandel plastic figures paper provenance validate
