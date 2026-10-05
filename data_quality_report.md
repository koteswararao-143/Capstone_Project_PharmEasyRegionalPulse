# PharmEasy Regional Pulse — Data Quality Report

## Purpose

The raw monthly export contains realistic operational data-quality issues.
The cleaning process fixes those issues before any regional performance
metric is calculated.

## Data-quality dimensions

| Dimension | Issue addressed | Pipeline fix |
|---|---|---|
| Accuracy | Profit values can be missing | Estimate missing profit from the observed category margin |
| Completeness | Category and profit fields contain blanks | Fill category from the exact product lookup and profit from category margin |
| Consistency | Region names use different capitalization and whitespace | Strip whitespace and title-case the region value |
| Timeliness | Orders belong to the monthly reporting period | Preserve the supplied order dates and use them as the reporting period |
| Validity | Required fields must exist before analysis | `validate_schema()` checks the required schema |
| Uniqueness | Some rows are exact copies | Remove exact duplicate rows |
| Relevance | Master data includes a region with no orders | Keep Kurnool in the master table so zero-activity regions remain visible |

## Expected validation results

The deterministic generator should create 2,159 raw rows.
After exact duplicate removal, the cleaned dataset should contain 2,100 rows.

The generated raw data contains:
- 94 missing `profit_inr` values
- 48 missing `category` values
- inconsistent region spellings
- 59 exact duplicate rows

After cleaning, category and profit should contain no missing values.

## Why the order of operations matters

Category must be restored before profit is imputed because the profit rule is
category-specific. Exact duplicates are removed first so that duplicated rows
do not receive extra weight when calculating category-level margin averages.

## Schema gate

A valid cleaned dataset returns:

```text
status = validated
```

If one required column is removed, the function returns:

```text
status = blocked_schema
```

along with the missing column name.
