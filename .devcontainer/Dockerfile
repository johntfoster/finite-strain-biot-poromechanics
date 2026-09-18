FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gfortran git curl ca-certificates python3 python3-venv \
    latexmk texlive-luatex texlive-latex-extra texlive-bibtex-extra \
    texlive-fonts-recommended poppler-utils \
    && rm -rf /var/lib/apt/lists/*
