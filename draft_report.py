"""
Context–Insight–Implication narrative generator for flagged regional changes.
"""

from __future__ import annotations


def _period_label(period_key):
    return period_key.replace("_to_", " → ")


def _direction(change):
    if change > 0:
        return "increased"
    if change < 0:
        return "decreased"
    return "was unchanged"


def draft_report_v1(flagged_regions, metrics):
    """
    Build one CII block per unique flagged region.

    `metrics` is expected to be:
        {
            "2026-04_to_2026-05": {
                "Guntur": 122.19,
                ...
            },
            "2026-05_to_2026-06": {
                ...
            }
        }

    Only values supplied by the metrics object are used in the narrative.
    No external market facts are added.
    """
    unique_regions = list(dict.fromkeys(flagged_regions))
    blocks = []

    for region in unique_regions:
        transitions = []

        for period, changes in metrics.items():
            if region not in changes:
                continue

            change = float(changes[region])
            direction = _direction(change)
            transitions.append(
                f"{_period_label(period)}: {change:+.2f}% "
                f"({direction})"
            )

        if not transitions:
            continue

        context = (
            f"{region} was flagged by the Part 2 month-over-month "
            f"threshold in {len(transitions)} transition(s)."
        )
        insight = (
            f"Recorded sales movement for {region}: "
            + "; ".join(transitions)
            + "."
        )
        implication = (
            f"The regional lead should review the underlying monthly "
            f"performance before using this movement for an operational decision."
        )

        blocks.append({
            "region": region,
            "Context": context,
            "Insight": insight,
            "Implication": implication,
        })

    return blocks
