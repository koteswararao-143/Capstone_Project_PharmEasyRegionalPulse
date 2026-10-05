# Data Quality Report — PharmEasy Regional Pulse

## Why cleaning is needed
The raw file had issues like duplicates, blanks, and messy names. Fixing them ensures later numbers are reliable.

## Data quality points
- **Accuracy:** Profit values missing → filled using average margin for that category.
- **Completeness:** Category and profit blanks → category restored from product lookup, profit filled via margin rule.
- **Consistency:** Region names inconsistent → standardized with strip + title‑case.
- **Timeliness:** Order dates already matched reporting months → kept as is.
- **Validity:** Required columns checked with 'validate_schema()'.
- **Uniqueness:** Duplicate rows → removed.
- **Relevance:** Master list includes Kurnool (zero orders) → kept for completeness.

## Validation results
- Raw dataset: 2,159 rows  
- After duplicate removal: 2,100 rows  
- Missing values: 94 profit, 48 category → all imputed  
- Region variants collapsed to 9 canonical names  
- Schema check:  
  - Clean data → 'status = validated' 
  - Broken copy → 'status = blocked_schema'

## Order of operations
Duplicates removed first. Category restored before profit imputation, since profit filling depends on category margins.
