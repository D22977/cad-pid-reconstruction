# Card and Receipt Rules

## Card states

`DRAFT → READY → PICKED_UP → RESULT_READY → REVIEWED → ACCEPTED`

`HOLD`, `FIX_REQUIRED`, and `WAIT_VALID_REVIEW` are explicit gates. Dispatch is not pickup. A comment or link is not PASS.

## Required worker receipt

```text
CARD_ID:
EXECUTOR:
BASE_SHA:
HEAD_SHA:
CHANGED_PATHS:
TEST_COMMANDS:
TEST_RESULTS:
RESULT: READY | BLOCKED
NOTES:
```

## Required reviewer receipt

```text
REVIEW_CARD_ID:
REVIEWER:
REVIEWED_HEAD_SHA:
REVIEWED_PATHS:
EVIDENCE:
VERDICT: PASS | FIX_REQUIRED
```

Only an exact `PASS` advances. After any repair, obtain a new review from a fresh context.
