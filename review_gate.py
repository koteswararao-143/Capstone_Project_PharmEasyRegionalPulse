"""Human review gate with an append-only JSON Lines audit trail."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import uuid

ALLOWED_DECISIONS = {"approve", "edit", "reject"}


def review_gate_v1(
    report,
    decision,
    reviewer_note="",
    *,
    region=None,
    audit_path="audit_log.jsonl",
    run_id=None,
):
    """Validate a human decision, update the report, and append one audit record."""
    if decision not in ALLOWED_DECISIONS:
        raise ValueError(f"decision must be one of {sorted(ALLOWED_DECISIONS)}")

    if run_id is None:
        run_id = uuid.uuid4().hex

    updated = dict(report)
    updated["review_decision"] = decision
    updated["reviewer_note"] = reviewer_note
    updated["external_downstream_use_allowed"] = decision == "approve"

    if region is None:
        region = updated.get("region", "")

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "run_id": run_id,
        "region": region,
        "decision": decision,
        "reviewer_note": reviewer_note,
    }

    path = Path(audit_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")

    return updated


def test_review_gate():
    """Exercise all three allowed decision paths and reject an invalid one."""
    audit = Path("audit_log.jsonl")
    if audit.exists():
        audit.unlink()

    report = {"region": "Guntur", "Insight": "example"}
    approved = review_gate_v1(report, "approve", "Approved after checking the SQL output.", region="Guntur", audit_path=audit, run_id="test-approve")
    edited = review_gate_v1(report, "edit", "Reworded the implication.", region="Guntur", audit_path=audit, run_id="test-edit")
    rejected = review_gate_v1(report, "reject", "Evidence needs another review.", region="Guntur", audit_path=audit, run_id="test-reject")

    assert approved["external_downstream_use_allowed"] is True
    assert edited["external_downstream_use_allowed"] is False
    assert rejected["external_downstream_use_allowed"] is False

    try:
        review_gate_v1(report, "publish", "Invalid decision", region="Guntur", audit_path=audit, run_id="test-invalid")
        raise AssertionError("Invalid decision was not rejected.")
    except ValueError:
        pass

    print("Review-gate test passed for approve, edit, reject, and invalid decision.")


if __name__ == "__main__":
    test_review_gate()
