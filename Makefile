PYTHON ?= python3
LATEXMK ?= latexmk
BUILD_JOBS ?= 1
export TEXMFVAR := $(CURDIR)/.agent-runtime/tex-cache/var
export TEXMFCACHE := $(CURDIR)/.agent-runtime/tex-cache/cache
export MPLCONFIGDIR := $(CURDIR)/.agent-runtime/matplotlib

MOOSE_ENV := .agent/shared/skills/setup-moose-conda/scripts/moose_conda_env.sh

.NOTPARALLEL: reproduce

.PHONY: sync-check sync-pull sync-push build test derivation mandel plastic plastic-flow stability examples figures paper provenance validate reproduce

sync-check:
	tools/sync_biot_moose.py check

sync-pull:
	tools/sync_biot_moose.py pull

sync-push:
	tools/sync_biot_moose.py push

build:
	$(MOOSE_ENV) run -- $(MAKE) -C moose_app -j$(BUILD_JOBS)

test: build
	cd moose_app && ../$(MOOSE_ENV) run -- $(PYTHON) \
		../.agent-runtime/moose/python/run_tests --no-color -j1

mandel: test
	$(MOOSE_ENV) run -- $(PYTHON) scripts/reproduce_mandel_publication.py --verify-benchmark --curate

derivation:
	$(PYTHON) validation/scripts/check_stress_trace_derivation.py
	$(MOOSE_ENV) run -- $(PYTHON) validation/scripts/check_stress_trace_biot_fraction.py

plastic: build
	$(MOOSE_ENV) run -- $(PYTHON) validation/scripts/check_implicit_poroplastic.py --publication --curate

plastic-flow: build
	$(MOOSE_ENV) run -- $(PYTHON) validation/scripts/check_poroplastic_mandel.py --curate

examples: build
	$(MOOSE_ENV) run -- $(PYTHON) scripts/reproduce_examples.py

figures:
	mkdir -p "$(TEXMFVAR)" "$(TEXMFCACHE)" "$(MPLCONFIGDIR)"
	MPLCONFIGDIR=.agent-runtime/matplotlib $(MOOSE_ENV) run -- $(PYTHON) scripts/plot_poroplastic_mandel.py
	MPLCONFIGDIR=.agent-runtime/matplotlib $(MOOSE_ENV) run -- $(PYTHON) scripts/plot_mandel_extended_results.py
	MPLCONFIGDIR=.agent-runtime/matplotlib $(MOOSE_ENV) run -- $(PYTHON) scripts/plot_implicit_poroplastic.py
	MPLCONFIGDIR=.agent-runtime/matplotlib $(MOOSE_ENV) run -- $(PYTHON) scripts/plot_poroplastic_delta_b.py
	MPLCONFIGDIR=.agent-runtime/matplotlib $(MOOSE_ENV) run -- $(PYTHON) scripts/plot_poroplastic_b_feedback.py
	MPLCONFIGDIR=.agent-runtime/matplotlib $(MOOSE_ENV) run -- $(PYTHON) scripts/plot_poroplastic_load_unload.py
	MPLCONFIGDIR=.agent-runtime/matplotlib $(MOOSE_ENV) run -- $(PYTHON) scripts/plot_tensorial_load_unload.py

paper:
	mkdir -p "$(TEXMFVAR)" "$(TEXMFCACHE)"
	$(LATEXMK) -lualatex -synctex=1 -interaction=nonstopmode -halt-on-error \
		-outdir=paper/build paper/main.tex

provenance:
	$(PYTHON) scripts/update_validation_provenance.py

validate: site
	$(PYTHON) scripts/validate_repository.py

reproduce: sync-check derivation test mandel plastic plastic-flow stability examples figures paper provenance validate

.PHONY: setup site serve stability
setup:
	bash tools/setup_reproduction.sh

site:
	$(PYTHON) scripts/build_site.py

serve: site
	$(PYTHON) -m http.server 8000 --directory .agent-runtime/site

stability: build
	$(MOOSE_ENV) run -- $(PYTHON) validation/scripts/check_poroplastic_spatial_stability.py --run --reuse --curate
