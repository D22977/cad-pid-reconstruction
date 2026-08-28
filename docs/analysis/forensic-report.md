# Forensic and Page-by-Page Report

- Analysis scope: DOCX internal structure, 16-page PDF rendering, supplied PNG screenshot, embedded automation text
- Result: mixed Word/AI/raster/script artifact; not an original CAD source
- CAD production performed: No

## Executive conclusion

The most likely history is that a party did not possess the original CAD file and asked an AI system to recreate or describe it. The AI produced an AutoCAD-like image, raw AutoCAD commands, an AutoLISP macro, engineering explanations, line-numbering examples, and plotting advice. Those outputs were collected into a Word document and exported to PDF.

The package cannot be converted back into an original DWG/DXF because no vector CAD database is present. It can, however, support a controlled reconstruction of a new 2D schematic. Most basic geometry, layers, text, piping, valves, and instrument bubbles can be generated automatically after the engineering contract is confirmed. Engineering specifications, line classes, symbols, scale, title block, and visual acceptance require human confirmation.

## Container and provenance findings

### DOCX

- Valid native OOXML Word container.
- Only three embedded PNG images were found.
- No `.dwg`, `.dxf`, `.scr`, `.lsp`, embedded CAD object, or OLE CAD payload was found.
- Command and LISP text is stored as Word text, not as executable/source attachments.
- Conclusion: technically a Word file, but content is a mixed AI conversation/document artifact rather than a native engineering authoring file.

### PDF

- 16 A4 pages.
- Production path indicates Microsoft Word plus Adobe PDFMaker/Acrobat workflow.
- Not an AutoCAD plot/export and contains no CAD object model.

### PNG screenshot

- AutoCAD-like raster screenshot with four pump arrangements.
- Contains malformed or implausible interface text and an AI-generation-style sparkle mark.
- Geometry and labels do not fully match the supplied scripts.
- It is useful as a visual target only; scale and coordinates cannot be recovered reliably.

## Page-by-page findings

| Page | Content | Forensic assessment | CAD use / manual work |
|---:|---|---|---|
| 1 | Title plus raw command sequence for P-3635A/B: layers, baseplate, column, casing, motor, suction | Word text containing generated command prose, not attached SCR | Basic geometry can be regenerated; pump representation and dimensions require approval |
| 2 | P-3635A/B discharge, check/control valve, PI/FI, labels; begins P-3637A/B | Coordinates are structured but schematic and unverified | Automatable after confirming symbols, text and engineering data |
| 3 | P-3637A/B piping/instruments/labels; begins P-7509 | Continued coordinate script | Automatable; no evidence dimensions derive from an original drawing |
| 4 | P-7509 equipment, suction/discharge, PI/TI/LI and insulation note | Contains clear coordinate defect: control valve remains at `(322,22)`–`(328,28)` | Must be corrected manually in the model/data contract; line rating and heat tracing need engineering confirmation |
| 5 | P-7509 labels; P-7511A/B horizontal pump, motor, piping, valve, PI/FI/LI | Schematic AI-generated command set | Automatable; OH2 symbol/nozzles and 72 m³/h narrative need validation |
| 6 | P-7511A/B labels followed by technical meeting-style explanation | Explanatory prose asserts engineering closure without source evidence | Treat as hypotheses; owner/engineer must confirm every claimed process requirement |
| 7 | AI disclaimer, question to user, then duplicated script text | Strong evidence of copied AI conversation output | No additional CAD authority; duplicate content should not be executed |
| 8 | Continued duplicated script and transition text “以下是生成的圖像” | Explicit AI-image-generation language | Image is reference only; no vector recovery |
| 9 | Description claiming strict coordinate adherence and offering style changes | Marketing/assistant narrative, not verification evidence | No direct geometry authority; use only to list intended visual elements |
| 10 | Begins “complete” AutoLISP macro; environment and layer creation | Code is presented as runnable but has not been validated | Do not execute unmodified; reimplement deterministically |
| 11 | Valve helper and P-3635A/B macro geometry | Vertical-valve helper uses `(list (+ x 3) x)`, causing a Y-coordinate defect; function locals include `oldosoldbl` typo | Rebuild symbol logic and add coordinate-bound tests |
| 12 | P-3637A/B and start of P-7509 macro | Repeated schematic coordinates plus line numbering | Automatable only after drawing contract; line data unverified |
| 13 | P-7509 and start of P-7511A/B macro | Better valve call coordinates than raw script, but inherits defective helpers | Rebuild from data, not by running this LISP |
| 14 | Completes P-7511A/B, title frame, title block and environment restore | Contains line number and frame assumptions; restore depends on broken local declaration | Title block, sheet size and drawing number require owner approval |
| 15 | Line-numbering examples and CTB colour/lineweight table | Engineering/plotting recommendations without cited company standard | Human must confirm `150#C` vs `300# RF`, materials, insulation and CTB policy |
| 16 | Offer to add linetypes and layout-space automation | Conversational close; no new source evidence | No geometry to recover |

## Script and engineering contradictions

1. **P-7509 valve coordinate error:** raw commands locate the P-7509 control valve in the P-3637 zone.
2. **Vertical valve outlier:** the LISP can draw a line to a Y coordinate equal to X; with the P-7511 call this can extend near Y=900.
3. **Local variable typo:** `oldosoldbl` is one symbol, not separate `oldos` and `oldbl` locals.
4. **Rating conflict:** equipment prose repeatedly states `300# RF`; the line-number example uses `150#C` on the two slop-oil discharges.
5. **Visual/code mismatch:** screenshot pumps, UI and annotations are more detailed and arranged differently than primitive rectangles/circles/lines.
6. **Standards claims are unsupported:** statements about ISA compliance, materials, seal plans, CTB and process closure have no attached design basis.

## Feasibility by work type

| Scope | Automation feasibility | Human confirmation required |
|---|---:|---|
| Basic pump/motor/baseplate geometry | High | Symbol choice and dimensions |
| Piping centerlines and arrows | High | Routing and flow direction |
| Valves and instrument bubbles | High | Standard, type, tag and connectivity |
| Layers, colours and text styles | High | Company CAD standard and plot policy |
| Equipment and instrument labels | High | Exact approved wording |
| Line numbers and specifications | Medium | Size, rating, material, insulation/heat tracing |
| Sheet/title block/layout | Medium | Sheet size, scale, drawing number, revision, language |
| Dimensionally faithful original recovery | Not feasible | Original CAD or authoritative dimensions would be required |
| Final DWG production | High after DXF approval | AutoCAD/BricsCAD application-level review and Save As |

## Recommended construction route

1. Freeze evidence and hashes.
2. Approve the S01 drawing contract.
3. Model four pumps as separate bounded data/components.
4. Generate a clean DXF with Python/ezdxf.
5. Run structural, geometric, textual and visual checks.
6. Obtain a fresh external review bound to the exact commit/file set.
7. Open the accepted DXF in AutoCAD/BricsCAD, inspect, then Save As DWG.

## Manual redraw / review boundary

Manual tracing of every line is unnecessary. Human work is concentrated in specification confirmation, symbol selection, visual correction, title-block completion, and final CAD application review. If exact dimensional fidelity is required, additional authoritative dimensions or the original drawing must be supplied; raster inference alone is insufficient.
