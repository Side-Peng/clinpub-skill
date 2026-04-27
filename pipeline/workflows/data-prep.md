---
name: data-prep
description: "Phase 1 orchestration: Load raw data, discuss cleaning strategy with user, execute data preparation pipeline, produce cleaned.csv and data quality report."
---

<purpose>
Transform raw patient-level data into analysis-ready cleaned.csv with full quality documentation. Handle missing values, outliers, derived variables, and encoding through a tiered decision framework with user confirmation at ambiguity points.
</purpose>

<required_reading>
@./pipeline/references/analysis_methods.md
@./agents/analyst-agent.md
@./pipeline/references/checkpoints.md
</required_reading>

<process>

<step name="discuss_cleaning_strategy" priority="first">
Discuss with user before any data transformation:

1. **Missing value strategy**: confirm tiered thresholds (<5% delete/fill, 5-20% MICE imputation, >20% flag for discussion)
2. **Outlier handling**: IQR vs Z-score thresholds, winsorization vs exclusion
3. **Variable encoding**: categorical reference levels, continuous variable transformations
4. **Derived variables**: any calculated scores, indices, or composite variables needed
5. **Train/validation split**: needed? Ratio? Stratification variables?
</step>

<step name="execute_cleaning" priority="high">
Load raw data from `01_RawData/` and execute cleaning pipeline:

1. **Import data** → generate variable dictionary (name, type, missing rate, unique values, sample values)
2. **Missing value handling**
   - <5%: delete rows or fill with mean/median/mode
   - 5-20%: MICE imputation (report imputation model)
   - >20%: discuss with user before proceeding
3. **Outlier detection**
   - Continuous: IQR (1.5×) or Z-score (|Z|>3)
   - Categorical: check for unexpected values
   - Flag and document all outliers found
4. **Derived variables** + encoding
   - Create calculated variables
   - Set factor levels and reference categories
   - Apply any transformations (log, Box-Cox, etc.)
5. **Data quality report** (HTML):
   - Variable summary table
   - Missing value matrix
   - Distribution plots for key variables
   - Outlier documentation
   - Training/validation split summary (if applicable)

All ambiguous handling points must be confirmed with user.
</step>

<step name="validate_output" priority="high">
After cleaning:

1. Verify `cleaned.csv` exists at `02_PreprocessedData/data/`
2. Check row/column counts match expectations
3. Confirm high-missingness variables are handled
4. Verify data types are correct
5. Ensure cleaning code is independently reproducible
6. Report cleaning summary to user:
   - Rows removed/retained
   - Variables modified/created
   - Missing values imputed
   - Outliers detected and handled
</step>

<step name="checkpoint_confirm" priority="medium">
Present a `checkpoint:verify` to user confirming the cleaned data is ready:

- [ ] cleaned.csv validated with expected dimensions
- [ ] Data quality report generated
- [ ] All ambiguous decisions confirmed during cleaning

If user requests changes, address them. If approved, proceed to milestone.
</step>

<step name="milestone" priority="high">
Execute the milestone workflow to formally close Phase 1 and gate into Phase 2:

```bash
# The milestone workflow will:
# 1. Verify success criteria for Phase 1
# 2. Collect data cleaning decisions
# 3. Generate .planning/phases/01-data-prep/MILESTONE.md
# 4. Update ROADMAP.md: Phase 1 → ✅ Complete, Phase 2 → 🔄 In Progress
# 5. Update STATE.md: current_phase → 2
# 6. Request user sign-off
```

See @./pipeline/workflows/milestone.md for full protocol.
</step>

</process>

<success_criteria>
- cleaned.csv written to 02_PreprocessedData/data/
- Data quality report generated (HTML)
- Missing values handled per agreed strategy
- Outliers documented
- Derived variables created and encoded
- Cleaning code independently reproducible from raw data
- User briefed on cleaning summary
</success_criteria>
