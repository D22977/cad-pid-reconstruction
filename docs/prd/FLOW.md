# Workflow Diagrams

## Delivery flow

```mermaid
flowchart TD
    A[Source intake: DOCX + PDF + PNG] --> B[M01 forensic analysis and SHA-256 manifest]
    B --> C{Owner accepts forensic conclusion?}
    C -- No --> B1[Revise analysis or add evidence]
    B1 --> B
    C -- Yes --> D[S01 drawing contract]
    D --> E{Units, scale, standards, tags, lines and title block confirmed?}
    E -- No --> H[HOLD_ENGINEERING_CONFIRMATION]
    H --> D
    E -- Yes --> P1[P01A P-3635A/B]
    E -- Yes --> P2[P01B P-3637A/B]
    E -- Yes --> P3[P01C P-7509]
    E -- Yes --> P4[P01D P-7511A/B]
    P1 --> I[I01 integrate deterministic DXF]
    P2 --> I
    P3 --> I
    P4 --> I
    I --> V[V01 automated audit + render + CAD open test]
    V --> R[R01 new fresh reviewer]
    R --> G{Exact PASS on exact head and file set?}
    G -- FIX_REQUIRED --> F[Create bounded repair card]
    F --> V
    G -- Unknown or unbound --> W[WAIT_VALID_REVIEW]
    W --> R
    G -- PASS --> O[C01 owner visual and engineering acceptance]
    O --> X[Release DXF]
    X --> Y[Open in AutoCAD/BricsCAD and Save As DWG]
```

## Authority and receipt flow

```mermaid
sequenceDiagram
    participant C as Owner / Control
    participant G as GitHub durable record
    participant W as Worker
    participant R as Fresh Reviewer

    C->>G: Publish exact card and accepted base
    G->>W: Worker reads card and base
    W->>G: READY receipt with head, files and tests
    Note over C,G: Dispatch or link alone is not pickup or PASS
    G->>R: Review exact head and file set in a new context
    R->>G: PASS or FIX_REQUIRED with evidence
    alt Exact PASS
        G->>C: Control reads back verdict and advances
    else FIX_REQUIRED or unknown
        G->>C: Hold; create bounded repair or request valid review
    end
```

## Handoff reading order

```mermaid
flowchart LR
    R0[README] --> R1[PRD]
    R1 --> R2[Forensic report]
    R2 --> R3[Decision records]
    R3 --> R4[Master card]
    R4 --> R5[Current subcard]
    R5 --> R6[Exact commit and receipts]
```
