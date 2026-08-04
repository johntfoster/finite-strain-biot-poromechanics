# Post-Edit Validation Checklist

## Manuscript

- Reopen the edited source and nearby displays.
- Search for stale labels, references, notation, and duplicated identities.
- Rebuild from `paper/main.tex`; inspect undefined references, citation failures,
  overfull boxes, and affected pages.
- Scan for rhetorical negative positioning and development-note language.
- Check every numerical or validation claim against the authoritative result.

## Implementation

- Confirm source-equation traceability for every changed MOOSE object.
- Run the narrowest relevant optimized build and quantitative test.
- Update `validation/theory_traceability.yml` for durable changes or open gaps.

## Validation

- Update `validation/acceptance.yml` and the equation/code map.
- Do not label calibration as independent validation.
- Keep transient outputs out of curated reference-data locations.

## Agent workflow

- Validate schema or template changes with a representative minimal example.
- Keep object names and include fragments consistent with the parent MOOSE app.
