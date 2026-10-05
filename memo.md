# PharmEasy Regional Pulse — Recommendation Memo

## Title

**Guntur's April → May sales movement requires a focused review. [LOW]**

## Context

Guntur was one of the regions flagged by the Part 2 fixed-threshold rule for
the April → May 2026 transition. [HIGH]

## Key Insight

Guntur sales increased from **₹62,442.27 in April 2026 to ₹138,738.93 in May
2026**, a month-over-month change of **+122.19%**. [HIGH]

The same region recorded **₹99,745.18 in June 2026**, which is a **-28.11%**
change from May to June. [HIGH]

## Evidence

The Part 2 SQL-backed calculation uses:

```text
(Current Month - Previous Month) / Previous Month × 100
```

For Guntur's April → May transition:

```text
(138,738.93 - 62,442.27) / 62,442.27 × 100
= +122.19%
```

[HIGH]

The Part 2 significance rule flags a region when the absolute month-over-month
change is greater than 8%. [LOW]

## Recommendation

Review Guntur's April → May order and sales mix at the regional level before
taking an operational action. [MEDIUM]

The large movement is a signal for human review, not proof of a particular
external cause. [MEDIUM]

## Next Check

Compare the underlying Guntur order mix and category contribution for April and
May, then confirm whether the change is supported by the cleaned order data
before communicating the result downstream. [MEDIUM]

## Assumptions

No external market, competitor, festival, demand, or customer-behavior fact is
used in this memo. [LOW]

Any explanation for why Guntur moved is treated as a hypothesis until it is
supported by additional evidence from the dataset. [LOW]
