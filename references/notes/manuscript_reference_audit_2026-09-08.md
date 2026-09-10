# Reference audit for the manuscript revision

The audit follows the citation keys consumed by `paper/main.tex`. Unused entries
in `all.bib` are outside the paper's current citation argument. The local and
retrieved full texts were inspected for the claims below. Citation counts were
not used to rank existing sources.

| Key | Inspected version and evidence | Support and manuscript action |
| --- | --- | --- |
| drumheller2000 | Published paper, pp. 354–357, equations (17)–(23), (35)–(36); pp. 363–364, equations (71)–(72) | Supports true motion, distention gradient A, distention a, J = a Jbar, and separate elastic/plastic factors. Use this terminology. The chosen Drucker–Prager specialization is an additional constitutive assumption. |
| fosterxu2025 | Author manuscript, sections 3–4, equations (21), (27c), (33)–(40), Appendix B | Supports the density conjugate, stress transformation and nonlinear Biot derivative. Contradicts identifying pore pressure with mean intrinsic grain stress. Does not derive the paper's plastic return mapping. |
| ingraham2017evolution | Published paper, pp. 2–3, equation (1), unloading-modulus procedure | Supports measured evolution of the elastic Biot coefficient during compaction. Explicitly distinguishes elastic and failure effective-stress coefficients. Experimental context, not validation of the selected yield law. |
| sunostien2013 | Full paper, section 4, AD residual evaluation | Supports scalar-templated AD evaluation in coupled finite-strain poromechanics. Its stabilization is not part of the present Q2/Q1 model. |
| lindsayetal2021ad | Published full text, sections II and III.C | Supports outer AD and AD-valued inner calculations in MOOSE. The present constitutive derivatives still require their own verification. |
| gastonetal2009moose | INL conference preprint with matching framework title; publisher metadata for the four-author journal article | Related framework evidence. The conference version is not the exact journal version. Use Lindsay for the specific AD claim; journal full-text version check remains open. |
| simotaylor1985 | Published paper, introduction and consistent-linearization derivation | Supports differentiating the discrete material algorithm for Newton iteration. Does not equate an active algorithmic derivative with an elastic unloading tangent. |
| miehe1996 | Published paper from the local reference library, pp. 223–224 and algorithmic-tangent construction | Supports the discrete stress-update tangent and numerical derivative checks. Keep this role distinct from the fixed-state definition of B. |
| hongetal2008 | Published PDF hosted by Suo, sections 2–4, equations (6), (13)–(16), (25) | Supports coupled diffusion and large deformation in gels; adopts molecular incompressibility. Context only for compressible-mineral poromechanics. |
| macminnetal2016 | arXiv:1510.03455v3, sections II–III and conclusions | Supports finite-deformation kinematics and transport in a porous material with incompressible constituents. Does not validate a compressible-mineral Biot law. |
| dehghanizilian2021 | arXiv:2103.06569v1, multiscale formulation and remodeling sections | Supports evolution of effective poroelastic properties through updated microstructure. Context, not the present local implicit construction. |
| biotwillis1957 | Metadata verified; original full text not located in the home-directory search or retrieved from ASME | **Not verifiable from original full text.** Preserve the established citation without adding source-specific claims. Needed: *The Elastic Coefficients of the Theory of Consolidation*, DOI 10.1115/1.4011606. |
| chengdetournay1988 | Wiley metadata and abstract; original full text not located in the home-directory search | **Not verifiable from original full text.** The analytical implementation is available for direct equation checks, but that does not verify the original attribution. Needed: *A Direct Boundary Element Method for Plane Strain Poroelasticity*, DOI 10.1002/nag.1610120508. |

PDFs acquired for inspection are kept in `references/pdfs/`; extracted text and
retrieval state are in `.agent-runtime/research/`. The Drumheller PDF was found
in the user's research files, and Miehe in the user's reference library. No
machine-specific source paths are required by this repository.

Authoritative and full-text access points:

- [Drumheller](https://doi.org/10.1016/S0020-7225(99)00047-6)
- [Foster and Xu](https://doi.org/10.1016/j.jmps.2025.106263)
- [Hong et al., full text](https://suo.seas.harvard.edu/sites/g/files/omnuum4271/files/suo/files/200.pdf)
- [MacMinn et al., preprint](https://arxiv.org/abs/1510.03455)
- [Dehghani and Zilian, preprint](https://arxiv.org/abs/2103.06569)
- [Gaston et al., journal metadata](https://www.sciencedirect.com/science/article/pii/S0029549309002635)
- [Biot and Willis](https://doi.org/10.1115/1.4011606)
- [Cheng and Detournay](https://doi.org/10.1002/nag.1610120508)
