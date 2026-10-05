import json

def compute_percentage_change_v1(current, previous):
    if previous == 0: return 0
    return ((current - previous) / previous) * 100

def flag_significant_regions_v1(changes, threshold=8):
    return {r:p for r,p in changes.items() if abs(p) > threshold}

def save_state_v1(month_summary, path="state.json"):
    with open(path,"w") as f: json.dump(month_summary,f)

def load_previous_state_v1(path="state.json"):
    with open(path,"r") as f: return json.load(f)
