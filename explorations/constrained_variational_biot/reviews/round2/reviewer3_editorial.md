# Reviewer 3, Round 2: editorial and technical-note assessment

## Recommendation: accept

I recommend **acceptance as an exploratory technical note**.  The revision
now states a self-contained, appropriately limited argument: the scalar
mineral relation is a local stationary condition, whereas the actual
continuum field reduction follows separately from source-free solid mass
conservation with compatible referential mass.  It does not claim that a
multiplier on the mineral equation removes a global degree of freedom.

The prior review's central concerns have been resolved.  In particular, the
note now displays the matched energy and proves the residual identity
(9), distinguishes the positive-curvature local branch from a global
minimum, derives the fixed-pressure chain rule in (13)--(14), and uses the
envelope derivative in (15).  The reduced mechanics and water residuals
(21)--(22) now contain mutually consistent body, traction, and normal-flux
terms.  The Darcy argument supplies a mass-flux Onsager potential, its
chemical-potential force pairing, and the stationarity equation (26), which
recovers the stated referential Darcy flux.  The scope is explicitly elastic
at the coupled-PDE level, and the text correctly separates continuum
elimination from discrete equivalence.

## Checks performed

- Equations (15) and (22) resolve uniquely to
  `eq:mixed-stress-total` at `main.tex:222` and
  `eq:reduced-weak-water` at `main.tex:298`, respectively, in the current
  `build/main.aux`.
- A two-pass `latexmk -lualatex` check found the current PDF up to date and
  found no undefined-reference, citation, overfull-box, underfull-box, or
  LaTeX-error diagnostic.
- I rendered and inspected all six PDF pages.  The title, equations,
  section transitions, citations, bibliography, and DOI hyperlinks are
  legible and clean; there is no clipping, collision, or awkward page break.

## Non-blocking suggestions

1. At `main.tex:111--113`, the text calls the discussion the "elastic
   specialization" and immediately describes an optional stored plastic
   factor (a^p).  This is mathematically harmless, and the later scope
   statement is clear, but a future polish pass could move that conditional
   sentence to the final poroplastic-extension qualification.  It would make
   the purely elastic PDE scope even crisper.

2. The notation in the Onsager section is correct for the declared
   **referential mass flux**, but one short parenthetical reminder that
   (
   \nabla_{\mbf X}\mu_f^{\mathrm{chem}}
   =\nabla_{\mbf X}p/\bar\rho_f
   \)
   is a reference-gradient convention would prevent a reader from confusing
   it with the corresponding spatial-gradient form.  This is explanatory,
   not a correction.

3. If this note is later expanded beyond an exploratory paper, it would
   benefit from one sentence identifying a concrete pressure/displacement
   space pair and a numerical demonstration of the proposed two-field
   prototype.  The present manuscript appropriately labels those steps as
   future validation rather than evidence already supplied.

These suggestions do not affect correctness or the present acceptance
recommendation.
