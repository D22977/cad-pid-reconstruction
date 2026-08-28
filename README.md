# CAD / P&ID Reconstruction

Public, evidence-first workspace for reconstructing a **new** 2D CAD drawing from a Word/PDF/image package that appears to combine AI-generated AutoCAD-like imagery, raw `.scr` commands, AutoLISP, and engineering prose.

## Current status

**Phase 0 — analysis and pre-construction design only.** No production DXF or DWG has been approved or released.

Start here:

1. [PRD and acceptance gates](docs/prd/PRD.md)
2. [Workflow diagrams](docs/prd/FLOW.md)
3. [Forensic and page-by-page report](docs/analysis/forensic-report.md)
4. [Decision: rebuild, do not claim recovery](docs/decisions/D001-rebuild-not-recover.md)
5. [Master card and subcard chain](cards/MASTER.md)
6. [Source manifest](evidence/manifests/source-manifest.json)

## Working conclusion

- The package is not an original CAD deliverable and contains no recoverable DWG/DXF object.
- The PDF is a Word/PDFMaker document export, not an AutoCAD plot/export.
- The DOCX is a native OOXML container, but its content is a mixed AI conversation/document artifact rather than a native engineering drawing source.
- The existing SCR/LISP content is useful as untrusted reference data only; it contains geometry, syntax, and engineering inconsistencies.
- A clean 2D DXF can be reconstructed deterministically after the drawing contract is confirmed. DWG should be produced later by opening the verified DXF in AutoCAD/BricsCAD and using Save As.

## Review policy

Grok, Kimi, ChatGPT Web, engineers, and other reviewers may inspect this public repository. Review comments are advisory until recorded against an exact commit and source-file set. Only an explicit durable `PASS` for that exact revision may advance a gated stage.

## Public-evidence notice

The original evidence files are preserved byte-for-byte outside this public repository. They are intentionally withheld until metadata/privacy exposure is explicitly approved because Office/PDF files can contain author metadata. This repository publishes the manifest, hashes, analysis, workflow, and review artifacts without publishing those original binaries.
