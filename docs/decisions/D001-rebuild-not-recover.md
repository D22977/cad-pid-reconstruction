# D001 — Rebuild a new CAD drawing; do not claim original recovery

- Status: Proposed, awaiting owner acceptance
- Date: 2026-08-28

## Decision

Treat the sources as untrusted visual/textual evidence and reconstruct a new 2D drawing. Do not describe the result as conversion or recovery of an original DWG/DXF.

## Why

- No DWG, DXF, embedded CAD object, or OLE CAD payload is present in the DOCX package.
- The PDF identifies a Word/PDFMaker production path rather than an AutoCAD plot path.
- The screenshot is raster, visually inconsistent, and not dimensionally recoverable.
- Supplied SCR/LISP contains defects and contradicts some engineering prose.

## Consequences

- Engineering fields require explicit confirmation.
- Source coordinates may seed a schematic layout, but cannot be accepted blindly.
- The first controlled deliverable is DXF; DWG follows application-level verification.
- Every release must state that it is a reconstruction based on incomplete sources.
