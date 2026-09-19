# Manuscript plagiarism review

Date: 19 September 2026

Manuscript: *Pressure coupling and the Biot coefficient in finite-strain poroelasticity and poroplasticity*, rooted at `paper/main.tex`.

## Assessment

No substantiated instance of unattributed copying or excessively close paraphrasing was identified in the material checked. The scientific prose shows short matches in conventional technical language. Longer matches occur in acknowledgements and the AI-use declaration shared with the author's other manuscripts. Those matches do not establish appropriation of scientific content.

The principal recommendation concerns the presentation of inherited ideas: make the relationship of the opening contribution statements to Foster–Xu (2025) and Gajo (2010, 2011) immediately clear. The manuscript already credits these sources in detail. This is a recommendation to improve attribution clarity, not a finding of plagiarism or a determination that the present work lacks novelty.

This is a bounded source-comparison review, not an iThenticate or Turnitin report, an originality certificate, or a comprehensive priority audit. No manuscript text was changed.

## Scope and method

- Read the abstract, all nine included section and appendix files, figure captions, acknowledgements, and included AI-use declaration through the canonical root and macro context. Inspected `all.bib` to resolve attribution.
- Ingested 21 locally available, text-extractable PDFs with the repository research-ingestion tool. Deduplicating identical file hashes left 20 comparison documents; these include different versions of some works, so this is not a count of 20 independent publications.
- Compared normalized manuscript prose with those documents using exact contiguous sequences seeded at six words. The comparison folds case, punctuation, ligatures, and line-break hyphenation; excludes displayed mathematics and TeX metadata; and interrupts prose matching at inline mathematics. Counts are normalized alphabetic tokens, not publisher similarity percentages. The bibliography itself was excluded from manuscript prose matching.
- Inspected the resulting matches and relevant source contexts. A supplementary vocabulary-overlap ranking helped locate passages for manual comparison; its scores are retrieval aids, not plagiarism probabilities.
- Compared the important conceptual passages directly with Foster–Xu, Gajo, Drumheller, and Foster's plasticity preprint. Checked attribution of the Mandel solution in the manuscript, but did not obtain its primary source full text.
- Ran targeted web searches for distinctive wording and related concepts, including the abstract's opening, the reversible-coefficient definition, the numerical solution's two levels, plastic-history wording, and the Gajo appendix's opening. Returned results did not establish an external verbatim source for those passages. Search engines can relax quotation constraints, and absence of a result does not establish originality. No full manuscript was submitted to an external similarity service.

Generated comparison files are kept in the ignored `.agent-runtime/research/` directory: `plagiarism_scan.py`, `plagiarism_exact_matches.json`, `manuscript_prose.json`, and `plagiarism_context_candidates.json`.

## Findings

### 1. Clarify the inherited Legendre-transform construction in the opening contribution statement

Locations: `paper/main.tex:38`; `paper/sections/introduction.tex:17`; `paper/sections/introduction.tex:81`; `paper/sections/finite_deformation_biot.tex:110` and `:163`.

The opening contribution paragraphs describe switching from mineral density to pressure and identifying the Biot coefficient through that transformation. Foster–Xu already develops the pressure Legendre transformation, relates the two effective stresses, and identifies the coefficient through the fixed-pressure specific-volume derivative. This is visible in the local source PDF, Section 4, PDF pages 11–12, equations (33)–(39).

The present manuscript explicitly acknowledges the earlier work in the introduction and cites its equations beside the stress definitions and coefficient. The relevant scientific content is therefore attributed. The wording inspected is not a close verbal reproduction of that source.

Action: optionally place a brief statement of inheritance directly in the opening contribution paragraph, for example: “Building on the pressure Legendre formulation of Foster and Xu, we construct the coupled energy for prescribed logarithmic skeleton and mineral laws and evaluate its reversible pressure coupling through a scalar mineral update.” Retain the existing equation-level citations. This proposed wording is an attribution clarification; it does not assert priority for every remaining component.

Source: [Foster and Xu (2025)](https://doi.org/10.1016/j.jmps.2025.106263), local file `references/pdfs/foster-xu-2025-revisiting-finite-deformation-poromechanics.pdf`.

### 2. Preserve the explicit Gajo correspondence when describing the constitutive contribution

Locations: `paper/sections/introduction.tex:44`; `paper/sections/finite_deformation_biot.tex:650` and `:909`; `paper/sections/gajo_equivalence_appendix.tex:5`; `paper/sections/conclusions.tex:16`.

Gajo's finite pressure multiplier is already present in the 2010 paper, equation (3.48), printed page 3077 / PDF page 17. Its rate coupling is developed in equations (5.12)–(5.14), printed page 3083 / PDF page 23. The 2011 paper supplies the corresponding plastic constitutive setting: equations (48) and (51), printed page 1743 / PDF page 6, and the reversible mineral-volume specialization in Appendix C.1, beginning on PDF page 11.

The manuscript explicitly identifies this foundation, gives a variable correspondence, and derives the reduction in an appendix. These are strong attribution practices. The inspected explanatory prose does not reproduce Gajo's distinctive wording. Constitutive equivalence, which the manuscript itself acknowledges, is not evidence of plagiarism.

Action: keep this attribution adjacent to the constitutive results and make the opening contribution statement consistent with it. Describe the contribution in terms of the presented energy construction, reduction, interpretation, and numerical evaluation, without implying that the entire inherited constitutive response first appears here. A complete novelty determination would require a separate literature and derivation audit.

Sources: [Gajo (2010)](https://doi.org/10.1098/rspa.2010.0018), `references/pdfs/gajo-2010-compressible-constituents.pdf`; [Gajo (2011)](https://doi.org/10.1016/j.ijsolstr.2011.02.021), `references/pdfs/gajo-2011-finite-strain-hyperelastoplastic.pdf`.

### 3. Long textual matches are concentrated in administrative statements

Locations: `paper/sections/acknowledgements.tex:4`; `provenance/ai_use_statement.tex:4`.

The acknowledgements contain a 51-token normalized match with Foster's plasticity preprint. The source has the same acknowledgement and grant language on PDF page 12. The declaration also contains matching runs of 27 and 24 normalized tokens concerning responsibility and author review. These were checked against the local PDF, not inferred solely from the matching algorithm. Funding language also overlaps with the locally supplied Foster–Xu and reacting-mixture manuscripts.

Assessment: shared grant names, factual acknowledgements, and disclosure language explain the matches. They should not be interpreted as copied scientific argument or results. No cosmetic rewriting is recommended merely to reduce a similarity score. Any eventual similarity report should identify these passages separately and check that the statements accurately describe this manuscript.

Source: `references/pdfs/foster-2026-apparent-non-associative-plasticity.pdf`, PDF page 12.

### 4. Short scientific matches are conventional terminology or stock prose

Excluding acknowledgements and the declaration, the longest exact normalized runs detected were seven words:

| Manuscript location | Matched wording | Comparison source | Assessment |
| --- | --- | --- | --- |
| `paper/sections/finite_deformation_biot.tex:33` | “the true-deformation gradient of the solid” | Drumheller, local PDF page 18 | Technical terminology, with explicit attribution to Drumheller at line 24. |
| `paper/sections/mandel_verification.tex:68` | “The material parameters are listed in” followed by the rendered table term | Sun–Ostien–Salinger | Stock table-introduction language; no distinctive scientific expression. |

Other matches comprise six-word fragments concerning the Biot coefficient, pore pressure, residual derivatives, and reference-volume terminology. None of the inspected matches warrants a copying allegation or a forced paraphrase. The seven-word maximum is a result of this particular normalized local comparison, not a universal bound on overlap with the literature.

### 5. Attribution of reproduced analytical material is visible; full verification remains limited

Location: `paper/sections/mandel_analytical_appendix.tex:5` and the citations preceding its characteristic equation and solution series.

The manuscript names and repeatedly cites Cheng and Detournay for the analytical solution. The appendix does not present the series as an original solution. That attribution is visible in the manuscript, but the cited 1988 paper was not available in the local comparison set. Accordingly, this review does not certify either exact source fidelity or wording independence against that paper.

## Coverage limits

The comparison set includes local versions of Drumheller; Foster–Xu; Foster's plasticity and reacting-mixture manuscripts; Gajo (2010, 2011); Ingraham and colleagues; Makhnenko–Labuz (2015); Brantut; Dehghani–Zilian; Gaston and colleagues; Lindsay and colleagues; MacMinn and colleagues; Meschke–Grasberger; Miehe; Simo–Taylor; Sun–Ostien–Salinger; Suvorov–Selvadurai; and Kazemian and colleagues. Some are author manuscripts or alternative versions rather than verified copies of the final publication.

The local Biot (1972) PDF has no extractable text and was excluded from automated comparison. Initial ingestion failed at that document; ingestion was then completed for the extractable files. Important cited works absent from the text-comparison set include Biot–Willis (1957), Hong and colleagues (2008), Makhnenko–Labuz (2016), Yamakawa and colleagues (2021), and Cheng–Detournay (1988). Publisher DOI pages for the three central Foster–Xu/Gajo sources could not be fetched during this review; findings about their content rely on the local PDFs.

PDF extraction can reorder columns, disrupt words, and lose symbols. The exact-match scan therefore cannot rule out disguised copying or all close paraphrases. Manual contextual review improves the assessment but does not make it exhaustive. Mathematical equivalence and priority were considered only to assess attribution, not independently re-proved throughout. Figure-image duplication, numerical-data provenance, code copying, unpublished sources, and closed publisher similarity databases were not comprehensively audited.

For submission, the useful next step is an institutional similarity report with passage-level inspection, identifying bibliography and administrative matches separately and reviewing substantive matches in context. No defensible overall plagiarism percentage follows from this review.

## Repository impact

Added this review record and generated ignored local retrieval/comparison files. Manuscript source, bibliography, figures, and implementation were preserved. A LaTeX rebuild was unnecessary because no manuscript source was edited.
