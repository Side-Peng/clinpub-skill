# Verification Patterns

> Patterns for verifying statistical analysis validity and reproducibility in clinical research.

---

## Statistical Verification Patterns

### Pattern 1: Descriptive Statistics Cross-Check

**Purpose**: Verify baseline table matches raw data summary.

**Steps:**
1. Load cleaned.csv
2. Compute key statistics independently (N, mean, SD, median, IQR, proportions)
3. Compare against Table 1 output values
4. Tolerance: floating-point difference < 1e-6

**Failure indicators:**
- N mismatch between data and table
- Mean/SD discrepancy > 0.01
- Proportion rounding errors

---

### Pattern 2: Model Output Verification

**Purpose**: Verify regression model results are internally consistent.

**Steps:**
1. Check OR/HR direction matches coefficient sign
2. Verify 95% CI = estimate +/- 1.96 * SE (for normal-approximated models)
3. Confirm p-value consistency with CI (significant p ↔ CI excludes null)
4. Check VIF < 10 for all predictors (multicollinearity)
5. Verify sample size in model matches cleaned data (minus missing cases)

**Failure indicators:**
- OR > 1 but coefficient negative
- CI includes null but p < 0.05
- VIF > 10 without documented justification
- N in model output != N in cleaned data minus excluded cases

---

### Pattern 3: Survival Analysis Verification

**Purpose**: Ensure KM curves and Cox regression are consistent.

**Steps:**
1. Compare KM median survival time with raw event/censor data
2. Verify risk table N at each time point matches Kaplan-Meier estimate
3. Check log-rank p-value from KM matches Cox univariate p-value for same variable
4. Confirm PH assumption test (Schoenfeld) is reported for each covariate
5. Verify event count in Cox output matches data

**Failure indicators:**
- Median survival outside observed range
- Risk table N mismatch
- log-rank vs Cox p-value discrepancy > 0.01
- PH assumption violated without sensitivity analysis

---

### Pattern 4: ROC/AUC Verification

**Purpose**: Ensure diagnostic accuracy metrics are correct.

**Steps:**
1. Verify AUC is between 0 and 1
2. Check sensitivity + specificity values at Youden threshold
3. Confirm 95% CI for AUC is symmetric around point estimate
4. Cross-validate: Wilson CI for sensitivity/specificity matches reported values
5. Verify combined panel AUC > max individual AUC (or explain if not)

**Failure indicators:**
- AUC outside [0, 1]
- CI bounds inverted (lower > upper)
- Sensitivity or specificity outside [0, 1]
- Combined AUC < best individual AUC without explanation

---

### Pattern 5: Multiple Comparison Verification

**Purpose**: Ensure appropriate correction for multiple testing.

**Steps:**
1. Count total number of tests within each analysis family
2. If > 3 tests: verify FDR or Bonferroni correction applied
3. Check corrected p-values <= raw p-values
4. Verify correction method documented in README
5. Confirm significant results survive correction (or note which do not)

**Failure indicators:**
- No correction when > 3 tests performed
- Corrected p > raw p
- Significant result claimed without correction

---

## Reproducibility Verification Patterns

### Pattern 6: Code Reproducibility

**Purpose**: Ensure analysis can be independently reproduced.

**Steps:**
1. Verify all R/Python scripts read from `cleaned.csv` (not hardcoded paths)
2. Check no manual steps between script sections
3. Confirm random seeds set for any stochastic methods (ML, imputation)
4. Verify package versions documented (sessionInfo() or requirements.txt)
5. Check output file paths use relative references

**Required evidence:**
- Script runs from top to bottom without error
- Output files match previously generated results
- sessionInfo() or equivalent captured

---

### Pattern 7: Data Integrity Chain

**Purpose**: Verify data flows correctly through pipeline stages.

**Steps:**
1. Raw data row/column count matches data profile
2. Cleaned data row count = raw count - documented exclusions
3. Variable transformations are reversible or documented
4. No data leakage between train/validation splits
5. Imputed values flagged or in separate column

**Failure indicators:**
- Row count discrepancy without documented exclusion
- Train/validation overlap detected
- Imputed values mixed with observed values without flag

---

### Pattern 8: Figure-Table Consistency

**Purpose**: Ensure figures and tables tell the same story.

**Steps:**
1. Compare key values in figure annotations with table data
2. Check axis ranges cover all data points
3. Verify N in figure caption matches N in analysis
4. Confirm significance annotations match reported p-values
5. Check color coding is consistent across figures

**Failure indicators:**
- Figure shows significance but table p > 0.05
- Figure N differs from table N
- Axis truncation hides data points
- Inconsistent color scheme across related figures

---

## Verification Report Format

Each verification produces a structured report:

```markdown
# Verification Report: [Method Name]

**Date**: YYYY-MM-DD
**Verified by**: clinpub-verifier
**Status**: PASS / FAIL / CONDITIONAL

## Checks Performed

| # | Pattern | Check | Status | Notes |
|---|---------|-------|--------|-------|
| 1 | Pattern 1 | Descriptive cross-check | PASS | All values within tolerance |
| 2 | Pattern 2 | Model output check | FAIL | VIF = 12.5 for variable X |

## Issues Found

### Issue 1: [Title]
- **Severity**: Critical / Warning / Info
- **Pattern**: Pattern N
- **Description**: [What was found]
- **Recommendation**: [How to fix]

## Sign-off
- [ ] All critical issues resolved
- [ ] All warnings acknowledged
- [ ] Reproducibility confirmed
```
