---
name: latex-citation-verifier
description: Verify LaTeX manuscript citations against real scholarly-paper metadata, local or retrieved source evidence, and BibTeX correctness. Use when checking whether a citation exists, whether a cited paper supports a manuscript claim, whether a DOI or BibTeX entry is correct, or before editing citation-backed claims.
---

# LaTeX Citation Verifier

## Overview

Use this skill to audit citation-backed manuscript claims. The goal is not only
to confirm that a BibTeX key compiles, but to verify that the cited work exists,
that `all.bib` is accurate, and that the paper actually supports the claim made
in the manuscript.

## Required Context

In manuscript repositories, follow local instructions first. For the
nonlinear Biot repository, read `AGENTS.md`, `VISION.md`,
`paper/main.tex`, and `paper/defs.tex` before interpreting citation-backed manuscript text.

If the repository has `agent_workflows/checklists/citation_verification.md`,
read and follow it. Treat it as the local audit contract.

## Manuscript formatting requirements

- Every bibliography DOI in the compiled manuscript PDF must be a clickable
  link to `https://dx.doi.org/<doi>`.  This repository implements that with the
  `\doi` macro in `paper/defs.tex`
  (`\providecommand{\doi}[1]{\href{https://dx.doi.org/#1}{#1}}`); verification
  should confirm the links survive a `latexmk` build and flag any plain-text
  DOI that bypasses the macro.

## Workflow

1. Locate the cited claim.
   - Find the sentence, paragraph, equation, or section containing the citation.
   - Record `file:line`.
   - Paraphrase the exact claim being supported.
   - Classify it as background, equation attribution, method comparison,
     historical attribution, empirical result, definition, or related work.

2. Resolve citation keys.
   - Use `scripts/scan_citations.py` when helpful to list citation commands,
     contexts, and BibTeX entries.
   - Locate each key in `all.bib` or the repository bibliography file.
   - Check for missing keys, duplicate keys, and obvious field omissions.

3. Verify paper reality and metadata.
   - Prefer DOI metadata from Crossref, Datacite, publisher pages, arXiv,
     official proceedings, library records, MathSciNet, or ZbMATH.
   - Compare title, authors, year, venue, volume, issue, pages, publisher, and
     DOI with the BibTeX entry.
   - Distinguish preprint metadata from final publication metadata when the
     source or claim differs.
   - If internet access is unavailable, say which metadata checks are pending
     and continue with local PDFs and BibTeX inspection.

4. Verify source support.
   - Prefer a local PDF in `references/pdfs/` or official full text.
   - For equation claims, inspect the cited equation, local definitions, and
     assumptions in the paper.
   - For prose claims, inspect the relevant section or paragraph; abstracts and
     citation snippets are not sufficient for technical support.
   - Record page, section, theorem, table, figure, or equation evidence.

5. Assign a verdict.
   - `supports`: the paper directly supports the manuscript claim.
   - `partially-supports`: it supports a weaker or narrower claim.
   - `related-only`: it is relevant background but does not support the claim as
     written.
   - `contradicts`: it says something materially different.
   - `not-verifiable`: paper text or reliable metadata could not be inspected.

6. Edit only after evidence is clear.
   - If the claim is unsupported, revise the claim or recommend a replacement
     citation.
   - If metadata is wrong, patch `all.bib` without changing manuscript prose
     unless the source evidence also changes the claim.
   - If the PDF is missing and support cannot be verified, report the gap rather
     than guessing.

## Reporting Format

Use this compact audit format:

```text
Claim: <file:line and short paraphrase>
Citation: <key>
Metadata: <pass/fail; DOI or missing DOI>
Evidence: <paper page/section/equation/table, with short paraphrase>
Verdict: <supports|partially-supports|related-only|contradicts|not-verifiable>
Action: <keep|revise claim|fix BibTeX|replace citation|add source|obtain PDF>
```

When multiple citations support one claim, report each key separately and then
state whether the combined citation set supports the claim.
