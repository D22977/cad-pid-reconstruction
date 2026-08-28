# MASTER — CAD/P&ID Reconstruction

- Status: `WAIT_USER_SCOPE_CONFIRMATION`
- Current phase: M01/S01 documentation
- Remote: `D22977/cad-pid-reconstruction` (public)
- Production CAD: Not authorized

## Objective

Reconstruct a new, auditable 2D DXF from the supplied mixed evidence and later convert the accepted DXF to DWG in AutoCAD/BricsCAD.

## Card graph

`M01 → S01 → {P01A, P01B, P01C, P01D} → I01 → V01 → R01 → C01`

## Current gates

- M01 analysis is drafted and must be reviewed by the owner.
- S01 engineering/drawing contract is unanswered.
- P01 and later cards are held.

## Global constraints

- GitHub commit history is the durable public authority for the published workspace; exact commit IDs remain mandatory.
- Exact card/base/head/path binding is mandatory.
- Worker, fresh reviewer and Control remain separate.
- No self-review, fabricated PASS, silent scope expansion, merge/release, or successor activation.
- No production CAD before S01 acceptance.
- Source evidence is immutable.

## Subcards

- [M01 forensic freeze](subcards/M01-forensic-freeze.md)
- [S01 drawing contract](subcards/S01-drawing-contract.md)
- [P01A P-3635A/B](subcards/P01A-p3635.md)
- [P01B P-3637A/B](subcards/P01B-p3637.md)
- [P01C P-7509](subcards/P01C-p7509.md)
- [P01D P-7511A/B](subcards/P01D-p7511.md)
- [I01 integration](subcards/I01-integration.md)
- [V01 validation](subcards/V01-validation.md)
- [R01 fresh review](subcards/R01-fresh-review.md)
- [C01 owner acceptance](subcards/C01-owner-acceptance.md)
