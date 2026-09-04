---
name: latex-research-ingest
description: Locally ingest research PDFs for LaTeX manuscript repositories, create a repo-local vector store, retrieve relevant chunks, and manage notes without relying on rag-pi or chat-preview. Use when the user wants to ingest, index, rebuild, query, summarize, compare, cite, or edit from PDF research documentation for a paper, article, derivation, literature review, or manuscript.
---

# LaTeX Research Ingest

## Core Rule

Use this skill's bundled scripts for research ingestion and retrieval. Do not rely
on rag-pi, chat-preview, `.ragpi/`, or chat-preview `/ingest` for this workflow
unless the user explicitly asks to use them.

The local store lives in:

```text
.agent-runtime/research/
  manifest.json
  vector-store.json
  text/
```

Treat this store as retrieval infrastructure, not source truth.

## Source Hierarchy

Maintain this hierarchy:

1. Manuscript truth: `paper/main.tex` and included TeX files.
2. Reference truth: original PDFs and extracted text in `.agent-runtime/research/text/`.
3. Human synthesis: notes in `references/notes/`.
4. Retrieval convenience: `.agent-runtime/research/vector-store.json`.

Never treat a retrieved chunk as final evidence for a precise quote, citation,
equation, theorem, or manuscript claim. Verify important claims against the
original PDF, extracted text, or bibliography metadata.

## Repository Layout

Prefer:

```text
references/pdfs/      # original source PDFs, named intentionally
references/notes/     # human notes, summaries, derivation checks
.agent-runtime/research/  # generated local extraction and vector store
```

Keep `.agent-runtime/` ignored by Git; share durable source PDFs and notes, not
the generated index.

## Commands

Ingest all PDFs in the standard location:

```bash
python3 tools/run_python_profile.py research agent_environment/skills/latex-research-ingest/scripts/research_store.py ingest . references/pdfs/*.pdf
```

Ingest specific PDFs:

```bash
python3 tools/run_python_profile.py research agent_environment/skills/latex-research-ingest/scripts/research_store.py ingest . references/pdfs/paper1.pdf references/pdfs/paper2.pdf
```

Retrieve:

```bash
python3 tools/run_python_profile.py research agent_environment/skills/latex-research-ingest/scripts/research_store.py retrieve . "intrinsic density mixture"
```

List indexed sources:

```bash
python3 tools/run_python_profile.py research agent_environment/skills/latex-research-ingest/scripts/research_store.py list .
```

## Ingestion Workflow

1. Place PDFs in `references/pdfs/` unless the repo says otherwise.
2. Use stable filenames: `author-year-short-title.pdf`.
3. Add or confirm BibTeX entries when the paper will be cited.
4. Run the local `research_store.py ingest` command.
5. Create or update a short note in `references/notes/` for important papers.

The script extracts text with `pdftotext` when available and falls back to Python
PDF libraries. It chunks text, builds a local TF-IDF vector store, and records
source metadata. It does not call external services.

## Answering With Retrieved Context

When answering research questions:

1. Run `research_store.py retrieve` for targeted context.
2. Inspect the extracted text or source PDF for exact claims.
3. Distinguish manuscript source from reference source.
4. Cite manuscript claims with TeX `file:line` when possible.
5. Cite reference claims with source PDF name and page/chunk information when
   available.

When retrieval is insufficient, say so and inspect source files instead of
inventing support.

## Editing Manuscripts

Before editing a manuscript based on ingested PDFs:

- identify which reference supports the change
- inspect the relevant manuscript source through the root TeX context
- make narrow edits
- add citation TODOs only when the source is known but citation placement or key
  is not settled

Do not paste long PDF excerpts into the manuscript or chat. Summarize and quote
only short, necessary snippets.
