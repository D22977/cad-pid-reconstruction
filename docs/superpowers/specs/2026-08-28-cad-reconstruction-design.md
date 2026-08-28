# CAD Reconstruction Design

- Design status: Draft for owner review
- Implementation status: Not started
- Remote status: public GitHub repository active; original evidence binaries withheld pending metadata/privacy approval

## Design summary

Build a small, data-driven generator that converts an owner-approved drawing contract into a clean DXF. Separate source evidence, engineering data, symbol geometry, sheet/layout configuration, validation, and rendered review output. Do not execute the supplied SCR/LISP as the source of truth.

## Proposed structure

- `evidence/`: immutable received files and source manifest
- `docs/`: PRD, forensic report, decisions, review notes
- `cards/`: exact scoped work and review gates
- `src/`: future deterministic generator only after approval
- `tests/`: future geometry, text, layer and DXF audit checks
- `output/`: generated candidates, excluded until a release card authorizes publication

## Data flow

`approved drawing contract → equipment/line data → reusable symbols → model-space composition → layout/title block → DXF audit → render → fresh review → owner acceptance`

## Error handling

- Fail closed on missing units, scale, standards or line specifications.
- Reject geometry outside approved bounds.
- Reject duplicate tags or missing required layers.
- Preserve generated diagnostics without mutating source evidence.
- Treat an external review as advisory unless it names the exact revision and files.

## Testing design

- Unit tests for reusable pump, valve, arrow, instrument and text primitives.
- Contract tests for four pump data records.
- Bounding-box and outlier tests targeting known defects.
- Entity/layer/tag inventory tests.
- DXF parser/audit test and deterministic regeneration comparison.
- Visual render review plus AutoCAD/BricsCAD open test.

## Approval boundary

This design permits documentation and planning only. CAD implementation begins only after the owner accepts `docs/prd/PRD.md` and completes S01.
