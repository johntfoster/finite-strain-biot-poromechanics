---
name: canonical-reference-finder
description: Audit citations in scholarly manuscripts by reading the cited full text, testing whether each source supports the exact local claim, tracing the source's own references to foundational literature, and comparing candidate canonical works using date-stamped Google Scholar citation counts plus field-aware evidence. Use when reviewing manuscript references, validating citation relevance beyond abstracts, finding foundational or canonical references for a topic, replacing weak citations, or distinguishing an original source from a popular review.
---

# Canonical Reference Finder

## Purpose

Determine two things separately:

1. whether a cited source supports the manuscript claim in its actual context; and
2. whether it is the best canonical reference for that claim.

Treat “canonical” as a documented judgment, not as a synonym for “most cited.”

## Required setup

Follow repository instructions first. In a LaTeX manuscript, identify the root
document, bibliography, local macros, and exact citation context. Use an
available citation-verification or research-ingest skill for metadata, PDF
ingestion, and targeted retrieval when applicable.

For the nonlinear Biot repository, read `AGENTS.md`, `VISION.md`,
`paper/main.tex`, `paper/defs.tex`, and
`agent_workflows/checklists/citation_verification.md`.

Read [canonicality-criteria.md](references/canonicality-criteria.md) before
ranking candidates.

## Workflow

### 1. Define the claim and topic narrowly

- Record the cited sentence or equation and its `file:line`.
- State the exact proposition the citation must support.
- Classify the citation's role: origin, governing equation, definition,
  method, evidence, review, comparison, or general background.
- Define the topic narrowly enough that candidate papers are comparable.
- Audit citation clusters one key at a time, then assess their combined support.

### 2. Resolve and acquire the cited work

- Verify title, authors, year, venue, DOI, and publication version.
- Prefer, in order: a locally ingested full text or repository PDF; an
  author-hosted or institutional copy; an official publisher or preprint full
  text; another lawful full-text source.
- Search by exact title, DOI, and author/title variants when necessary.
- Do not use an abstract, search snippet, AI summary, metadata record, or
  citation context alone as evidence of technical support.
- If the relevant full text cannot be inspected, assign `not-verifiable` and
  ask the user to provide the paper. State the exact title, DOI, and citation
  key needed. Do not guess a support verdict.

### 3. Read for claim support

- Read the relevant section and enough surrounding definitions, assumptions,
  methods, results, and limitations to interpret it correctly.
- For mathematical claims, inspect the equation, symbol definitions,
  hypotheses, and nearby derivation.
- Record page and section plus equation, theorem, figure, or table where useful.
- Assign `supports`, `partially-supports`, `related-only`, `contradicts`, or
  `not-verifiable`.
- Prefer revising an overstated claim over forcing a merely related paper to
  support it.

### 4. Build the canonical-candidate set

- Inspect the cited work's introduction, background, method provenance, and
  bibliography for sources it identifies as original, foundational, standard,
  or definitive.
- Follow the reference chain far enough to locate the originating contribution,
  not merely the oldest citation.
- Add major reviews, monographs, standards, or later definitive formulations
  when they serve a different citation role.
- Use targeted searches for the topic plus terms such as `original`,
  `foundational`, `review`, `standard`, and key method names.
- Where practical, inspect influential papers that cite the candidate to learn
  how the field attributes the result.
- Require full-text support from any proposed replacement before recommending
  it for the manuscript claim. If unavailable, mark it `candidate-unverified`
  and ask for the paper rather than recommending it as a settled replacement.

### 5. Collect citation evidence

- Look up each serious candidate in Google Scholar using exact-title matching.
- Record the visible `Cited by` count and access date. Disambiguate versions
  and avoid silently adding duplicate records.
- If Scholar is blocked or ambiguous, report that limitation. Use OpenAlex,
  Semantic Scholar, Crossref, or publisher metrics only as separately labeled
  corroboration; do not present those values as Google Scholar counts.
- Compare papers of similar topic and citation role. Note publication year,
  field age, title variants, editions, and whether a book, review, or standard
  naturally accumulates citations differently.
- Never infer claim support, correctness, priority, or canonical status from
  citation count alone.

### 6. Decide canonicality by role

Use the criteria in the reference file. A topic may legitimately need:

- an original source for priority;
- a definitive source for the formulation actually used;
- a review or monograph for broad background; and
- a modern source for the present implementation or evidence.

Prefer the smallest citation set that accurately covers those roles. Do not add
prestige citations that do not support the local text.

### 7. Report before editing

For each citation, report:

```text
Claim: <file:line and exact proposition>
Cited source: <key; full citation; DOI>
Full text: <source inspected, version, access status>
Support evidence: <page/section/equation/table and concise paraphrase>
Support verdict: <supports|partially-supports|related-only|contradicts|not-verifiable>
Candidate ancestry: <key references followed and why>
Citation evidence: <candidate — Google Scholar count — access date; limitations>
Canonical judgment: <keep|supplement|replace|remove|unresolved>
Role: <original|definitive|review|standard|modern application>
Reason: <claim fit, priority, field recognition, authority, and limitations>
Action: <specific manuscript/BibTeX action or paper needed from user>
```

Include a compact candidate table when comparing multiple works. Clearly label
inferences and uncertainties. Link to lawful full text or authoritative
metadata where available.

Do not edit manuscript prose or bibliography unless the user requested edits.
After an authorized edit, follow the repository's required validation and
rebuild workflow.

## Stop conditions

- Missing cited full text: ask the user to provide the paper and leave support
  as `not-verifiable`.
- Missing replacement full text: label it `candidate-unverified`; do not call it
  a verified replacement.
- Ambiguous Scholar record or inaccessible Scholar: report the unresolved
  metric and continue with non-metric canonicality evidence.
- Topic too broad for a meaningful ranking: narrow it from the local claim
  before comparing candidates.
