# PharmEasy Regional Pulse — Presentation Storyline

The same verified finding is reframed below for two audiences: an executive and a regional manager.

## 1. Executive audience — Situation / Complication / Resolution

### Situation
Guntur sales increased from **₹62,442.27 in April 2026 to ₹138,738.93 in May 2026**, a verified month-over-month movement of **+122.19%**. [HIGH]

### Complication
A movement this large is a review signal, but the number by itself does not establish why the change happened. The May→June movement also reversed direction, so the evidence should be treated as a performance signal rather than a confirmed external cause. [MEDIUM]

### Resolution
Use the cleaned, SQL-backed regional and category detail to review Guntur's April→May change before making an operational decision; the dashboard provides the supporting evidence in one place. [MEDIUM]

## 2. Regional manager audience — Overview / Category / Detail

### Overview
The headline is Guntur's **+122.19% April→May sales movement**, calculated from ₹62,442.27 in April and ₹138,738.93 in May. [HIGH]

### Category
The category breakdown in the dashboard shows which of the six categories contributed to the selected region's sales, so the manager can see whether the headline movement is concentrated in a specific category. [LOW]

### Detail
The regional-month table provides the supporting sales, profit, and distinct-order values used by the dashboard. The underlying SQL workflow retains the zero-order Kurnool region through a LEFT JOIN, which is also why the detail layer can be reconciled to the master region list. [LOW]

## Anticipated pushback & Q&A

### Q1 — “Why should I believe this number?”
**1. Acknowledge:** That's a fair concern because a large percentage movement should be traceable before it is acted on.

**2. Verified vs. unverified:** Verified: the April sales total is ₹62,442.27, the May total is ₹138,738.93, and the SQL-backed calculation gives +122.19%. [HIGH] Unverified: the external reason for the movement.

**3. Resolve uncertainty:** Reconcile the underlying Guntur order/category detail in the dashboard before the next regional review; that check should be completed before the finding is used for an operational decision.

### Q2 — “What if an alternative explanation is driving this?”
**1. Acknowledge:** That is possible, and the current data does not prove a causal explanation.

**2. Verified vs. unverified:** Verified: the regional sales movement occurred in the cleaned order data. [HIGH] Unverified: whether a market event, competitor action, festival effect, or another external factor caused it.

**3. Resolve uncertainty:** Add or validate the relevant external evidence against the April/May period before assigning a cause; until then, keep the cause explicitly as a hypothesis.

### Q3 — “What would change your recommendation?”
**1. Acknowledge:** The recommendation should change if the underlying evidence shows the movement is a data-quality issue or cannot be reproduced.

**2. Verified vs. unverified:** Verified: Part 1 validation and the Part 2 SQL calculations reproduce the regional metric. [HIGH] Unverified: any causal explanation outside the order dataset.

**3. Resolve uncertainty:** Re-run the cleaning and SQL checks and reconcile the affected orders/categories before the next decision point; if the metric fails reconciliation, do not use the finding as an operational signal.

### Q4 — “What did you not check?”
**1. Acknowledge:** The dashboard is intentionally focused on the supplied order dataset rather than external market research.

**2. Verified vs. unverified:** Verified: regional sales, profit, category mix, and distinct-order counts in the supplied data. [HIGH] Unverified: competitor activity, customer-level causes, campaign effects, and other external drivers.

**3. Resolve uncertainty:** Obtain and validate the relevant external evidence before making any causal claim; until then, those explanations remain outside the verified scope.
