# PharmEasy Regional Pulse

**Headline finding:** Guntur's April→May sales moved from ₹62,442.27 to ₹138,738.93, a verified **+122.19%** month-over-month swing. [HIGH]

- **Streamlit dashboard (`app.py`) — live data exploration:** connects the overview KPIs, category breakdown, regional trends/comparison, and regional-month detail through one working region filter.
- **CII narrative (embedded in the dashboard) — what the data means:** turns flagged regional movement into Context–Insight–Implication blocks using Part 2 metrics.
- **One-page memo (`memo.md`) — the recommendation:** gives the seven-field recommendation memo and risk-tags factual claims.
- **Presentation storyline (`presentation_storyline.md`) — how you would defend it live:** reframes the same Guntur finding for an executive and a regional manager, then provides anticipated pushback Q&A.

**Reviewer consumption order:** dashboard → CII narrative → memo → presentation storyline.

**Single unverified assumption:** the memo does not establish an external cause for Guntur's movement; any competitor, festival, campaign, demand, or other external explanation remains a hypothesis until additional evidence is checked. [LOW]

## Setup and run

Use Python 3.10+.

```bash
python -m pip install pandas streamlit plotly
python generate_dataset.py && python clean_data.py && python build_db.py
streamlit run app.py
```
