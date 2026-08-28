# Product Requirements Document: 2D CAD Reconstruction

- Status: Draft for user and external review
- Version: 0.1
- Date: 2026-08-28
- Repository visibility: Public
- Current gate: `WAIT_USER_SCOPE_CONFIRMATION`
- Production CAD authorized: No

## 1. Problem

The available source package does not contain an original DWG or DXF. It contains a DOCX, a 16-page PDF exported from Word, a raster screenshot resembling AutoCAD, raw AutoCAD command fragments, AutoLISP, line-numbering suggestions, and CTB advice. Some of those elements conflict with each other or contain obvious defects.

The project must therefore reconstruct a **new, reviewable 2D CAD drawing** without presenting it as recovery of an original drawing and without silently treating AI-generated engineering statements as approved design data.

## 2. Product goal

Produce a deterministic and inspectable 2D DXF that captures the user-approved arrangement of four pump stations, related piping, valves, instruments, labels, layers, and title-block information. After technical and visual verification, AutoCAD/BricsCAD may open the DXF and save an approved DWG.

## 3. Non-goals

- Recovering an unavailable original DWG/DXF.
- Claiming the raster screenshot is dimensionally accurate.
- Executing the supplied LISP or SCR as trusted code.
- Inventing process design, line classes, pressure ratings, pump data, ISA symbols, scale, or title-block data.
- Releasing a DWG directly from an unreviewed conversion.
- Starting CAD generation before the user approves the drawing contract.

## 4. Source evidence

| Evidence | Role | Trust level |
|---|---|---|
| DOCX | Original mixed document/container | Untrusted evidence; structure is inspectable |
| 16-page PDF | Stable page rendering of the document | Primary page-by-page review source |
| PNG screenshot | Visual intent/reference | Raster only; likely AI-generated and not measurable |
| SCR/LISP text | Candidate coordinates and labels | Untrusted draft logic; must be re-derived and tested |

Hashes and sizes are recorded in `evidence/manifests/source-manifest.json`.

## 5. Users and roles

- **Owner / Control:** the user. Confirms engineering intent, scope, units, and final acceptance.
- **Coordinator:** maintains cards, exact revision bindings, evidence read-back, and stage gates.
- **Worker:** performs one bounded analysis or implementation card. Does not self-approve.
- **Fresh Reviewer:** independently reviews the exact commit and file set. Does not implement the work it reviews.
- **External Reviewer:** Grok, Kimi, ChatGPT Web, or a human engineer. May comment publicly; comments become authoritative only when accepted into a durable decision/receipt.

## 6. Functional requirements

### FR-01 Evidence preservation

- Preserve each source byte-for-byte and record SHA-256, size, media type, and provenance category.
- Never overwrite source evidence.
- Keep derived page images and scratch extracts out of the durable evidence set unless specifically needed for review.

### FR-02 Drawing contract

Before CAD generation, the owner must confirm or correct:

1. Drawing type: equipment/line diagram, P&ID-like schematic, GA, or another class.
2. Units and model-space convention.
3. Whether geometry is schematic/not-to-scale or must have a defined scale.
4. Sheet size, orientation, margins, title block, drawing number, revision, and language.
5. Required layers, colours, linetypes, lineweights, text style, and dimension style.
6. Four equipment tags and pump types: `P-3635A/B`, `P-3637A/B`, `P-7509`, `P-7511A/B`.
7. Suction/discharge routing, flow arrows, nozzles, valves, instrument bubbles, and seal-plan callouts.
8. Line numbers, size, pressure class, material class, insulation/heat tracing, and whether `150#C` or `300# RF` is correct for each line.
9. Required engineering standard/symbol library and whether the screenshot is only a visual target.

Ambiguity in any safety- or specification-relevant field produces `HOLD_ENGINEERING_CONFIRMATION`, not an invented default.

### FR-03 Deterministic generation

- Preferred implementation: Python plus `ezdxf` with data-driven equipment definitions.
- Repeated symbols must be blocks or controlled reusable geometry.
- Coordinates, tags, line data, and styling must be source-controlled text/data.
- A clean regeneration from the same commit must produce equivalent CAD content.

### FR-04 Layer model

The initial candidate layer set is:

| Layer | Intended contents | Status |
|---|---|---|
| `E-EQUIP` | Pump, motor, coupling, baseplate | Proposed |
| `E-PIPE` | Process piping, arrows, valve geometry | Proposed |
| `E-INST` | Instrument bubbles and signal/leader lines | Proposed |
| `E-TEXT` | Tags, notes, line numbers | Proposed |
| `E-FRAME` | Border and title block | Proposed |

Names and plotting rules remain unapproved until the drawing contract is signed off.

### FR-05 Outputs

- Primary: ASCII or binary DXF that passes parser/audit checks.
- Review aids: entity inventory, layer report, bounding-box report, and visual render.
- Final conversion: DWG created only after verified DXF is opened and reviewed in AutoCAD/BricsCAD.

## 7. Quality and validation requirements

### Automated checks

- DXF opens with `ezdxf` audit free of unrecoverable errors.
- All entities reside on approved layers.
- Expected equipment tags and instrument labels are present exactly once where specified.
- Geometry stays inside approved coordinate bounds; outlier detection must catch defects such as `(903,900)`.
- No duplicate entities caused by retries or card replay.
- Entity counts and block references match the approved drawing contract.
- Text height, linetype, colour, and lineweight satisfy the layer table.
- Regeneration is deterministic enough for meaningful diff/review.

### Visual and engineering checks

- Side-by-side comparison with the approved reference intent.
- Flow continuity and arrow direction.
- Symbol correctness.
- Label collision and readability at the chosen sheet size.
- Human confirmation of tags, line numbers, size, rating, class, insulation, scale, and title block.

## 8. Acceptance gates

1. `M01_FORENSICS_ACCEPTED`: source structure and defects reviewed.
2. `S01_DRAWING_CONTRACT_ACCEPTED`: owner confirms engineering and sheet assumptions.
3. `P01_COMPONENTS_READY`: four component cards complete against exact bases.
4. `I01_INTEGRATION_READY`: deterministic DXF candidate and reports published.
5. `V01_VALIDATION_PASS`: automated and AutoCAD/BricsCAD checks pass.
6. `R01_FRESH_REVIEW_PASS`: a reviewer who did not create the revision returns exact PASS.
7. `C01_OWNER_ACCEPTED`: user accepts the visible result and authorizes DWG conversion/release.

`FIX_REQUIRED`, unknown evidence, a valid link, a dispatched card, or a reviewer comment without exact revision binding is not PASS.

## 9. Known defects in supplied automation

- The P-7509 raw script places a control valve at `(322,22)`–`(328,28)`, in the P-3637 coordinate area rather than near X=600.
- The vertical-valve LISP contains `(list (+ x 3) x)` where the second coordinate should depend on `y`; at `x=900, y=37` it can produce an extreme outlier near `(903,900)`.
- `defun c:DRAWPUMPS ( / oldosoldbl oldlay)` fails to declare `oldos` as intended because names are concatenated.
- Source prose says some connections are `300# RF`, while later line-number text labels slop-oil lines `150#C`.
- The screenshot depicts detail not created by the primitive LINE/CIRCLE/RECTANG code.

These are evidence that the supplied automation cannot be trusted as the production generator.

## 10. Delivery and review model

The card chain is `M01 → S01 → P01A/P01B/P01C/P01D → I01 → V01 → R01 → C01`.

The four `P01` pump cards may run in parallel after `S01`. Integration, validation, and formal review are sequential. Each worker receipt must identify card, executor, base commit, head commit, changed paths, tests, and result. A fresh reviewer must bind its verdict to the same head and file set.

## 11. Immediate owner decisions

Before any CAD code is written, the owner must review this PRD and answer the drawing-contract questions in FR-02. The highest-risk unresolved items are drawing class, units/scale, specification authority, exact line ratings/classes, required symbol standard, and title-block requirements.
