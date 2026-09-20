FROM mcr.microsoft.com/devcontainers/base@sha256:d94c97dd9cacf183d0a6fd12a8e87b526e9e928307674ae9c94139139c0c6eae # ubuntu-24.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gfortran git curl ca-certificates python3 python3-venv \
    latexmk texlive-luatex texlive-latex-extra texlive-bibtex-extra \
    texlive-fonts-recommended poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Fixed container paths preserve compiled library and Conda prefixes when the
# editable checkout is mounted elsewhere by Codespaces.
RUN mkdir -p /opt/biot && chown vscode:vscode /opt/biot
USER vscode
WORKDIR /opt/biot
COPY --chown=vscode:vscode .agent/shared/ .agent/shared/
COPY --chown=vscode:vscode tools/setup_reproduction.sh tools/provision_latex.py tools/
COPY --chown=vscode:vscode moose_app/patches/ moose_app/patches/
RUN git init -q && bash tools/setup_reproduction.sh \
    && .agent-runtime/miniforge/bin/conda clean --all --yes
ENV PATH="/opt/biot/.agent-runtime/miniforge/bin:${PATH}"

# Manuscript and data changes reuse this compiled framework layer.
COPY --chown=vscode:vscode moose_app/ moose_app/
ARG BUILD_JOBS=2
RUN .agent/shared/skills/setup-moose-conda/scripts/moose_conda_env.sh run -- \
    make -C moose_app -j${BUILD_JOBS}

COPY --chown=vscode:vscode . .
ARG SOURCE_REVISION
LABEL org.opencontainers.image.source="https://github.com/johntfoster/finite-strain-biot-poromechanics"
LABEL org.opencontainers.image.revision="${SOURCE_REVISION}"
# Fetch public commit metadata; never copy local Git configuration or credentials.
RUN test -n "${SOURCE_REVISION}" \
    && git remote add origin https://github.com/johntfoster/finite-strain-biot-poromechanics.git \
    && git fetch --depth=1 origin "${SOURCE_REVISION}" \
    && git reset --mixed FETCH_HEAD \
    && shared_revision="$(git ls-tree HEAD .agent/shared | awk '{print $3}')" \
    && git -C .agent/shared init -q \
    && git -C .agent/shared remote add origin https://github.com/johntfoster/research-agent-workflows.git \
    && git -C .agent/shared fetch --depth=1 origin "${shared_revision}" \
    && git -C .agent/shared reset --mixed FETCH_HEAD \
    && python3 tools/prebuilt_app.py record
ENV BIOT_IMAGE_ROOT=/opt/biot
USER vscode
