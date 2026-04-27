---
name: clinpub:data-prep
description: "Phase 1: Data preparation and exploratory data analysis. Clean raw data, handle missing values, detect outliers, create derived variables, generate data quality report, and produce cleaned.csv."
argument-hint: ""
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - AskUserQuestion
---
<objective>
Phase 1: Data preparation. Transform raw data into analysis-ready cleaned.csv with full data quality documentation.

Handles: missing value imputation, outlier detection, derived variable creation, encoding, train/validation split.
</objective>

<execution_context>
@./pipeline/workflows/data-prep.md
</execution_context>

<process>
Execute the data-prep workflow from @./pipeline/workflows/data-prep.md end-to-end.
</process>

<success_criteria>
- cleaned.csv exists at 02_PreprocessedData/data/
- Data quality report generated (HTML)
- Missing values handled per tiered strategy
- Outliers documented
- Derived variables created and encoded
- Cleaning code independently reproducible
</success_criteria>
