import json,time,uuid

def review_gate_v1(report, decision, reviewer_note=""):
    if decision not in {"approve","edit","reject"}:
        raise ValueError("Decision must be approve/edit/reject")
    entry={"timestamp":time.strftime("%Y-%m-%d %H:%M:%S"),
           "run_id":str(uuid.uuid4()),
           "region":report.get("region","unknown"),
           "decision":decision,
           "reviewer_note":reviewer_note}
    with open("audit_log.jsonl","a") as f: f.write(json.dumps(entry)+"\n")
    report["decision"]=decision
    report["reviewer_note"]=reviewer_note
    report["external_use_allowed"]=(decision=="approve")
    return report
