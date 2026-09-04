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
- Push shared changes with `tools/sync_biot_moose.py push` and confirm the
  master/Biot hashes agree.
- Update `validation/theory_traceability.yml` for durable changes or open gaps.

## Validation

- Update `validation/acceptance.yml` and the equation/code map.
- Do not label calibration as independent validation.
- Keep transient outputs out of curated reference-data locations.

## Agent workflow

- Validate routing, path, or synchronization changes with a representative
  local command.
