---
name: analysis
description: "Phase 2 orchestration: Wave-based statistical analysis. Discuss method details with user, execute in dependency order (Wave 1→4), each method produces figure + table + README with publication-grade standards."
---

<purpose>
Execute statistical analysis methods in wave order with dependency tracking. Each method produces publication-grade figures (≥300 DPI, English labels), formatted tables, and method documentation (README.md).
</purpose>

<required_reading>
@./pipeline/references/analysis_methods.md
@./pipeline/references/r_patterns.md
@./pipeline/references/checkpoints.md
@./agents/analyst-agent.md
</required_reading>

<process>

<step name="discuss_analysis_plan" priority="first">
Discuss with user before executing any analysis:

1. **Method parameters**: variable selection strategy, model covariates, reference groups
2. **Figure/table preferences**: color palette, output format (PNG/PDF/TIFF), dimensions
3. **Train/validation split**: method and ratio (if applicable)
4. **Multiple comparison correction**: FDR vs Bonferroni vs none
5. **Significance level**: default α=0.05, confirm or adjust
</step>

<step name="execute_wave1" priority="high">
**Wave 1 — No dependencies.**

Execute confirmed methods from this set:

- **01_BaselineTable**: Table 1 (docx, 3-line style). Descriptive statistics by group. t-test/chi-square/Wilcoxon p-values.
- **02_GroupComparison**: Box/violin plots with 3-layer rendering (r_patterns §1). Z-score standardization if scales differ (§2). Dynamic significance annotation (§3). Descriptive stats + comparison to Excel.

Each method creates directory `03_AnalysisMethods/XX_MethodName/` with `main.R`, outputs figures/tables to `04_Outputs/XX_MethodName/`, and writes `README.md`.

Verify completeness before proceeding to Wave 2.
</step>

<step name="checkpoint_wave1_complete" priority="medium">
`checkpoint:verify` — Wave 1 outputs ready for review:

- [ ] BaselineTable: Table 1 (docx) + README completed
- [ ] GroupComparison: figures + Excel export + README completed
- [ ] All figures ≥300 DPI with publication theme

User confirms outputs before proceeding to Wave 2.
</step>

<step name="execute_wave2" priority="high">
**Wave 2 — Depends on Wave 1 results.**

- **03_LogisticRegression**: Univariate → multivariate → model diagnostics. OR + 95%CI + p-value table. Forest plot. Hosmer-Lemeshow, VIF.
- **04_SurvivalAnalysis**: KM curves with risk table, Log-rank p-value. Cox regression (univariate → multivariate). PH assumption test (Schoenfeld residuals). Forest plot.

Report effect size + 95%CI + exact p-value for every analysis.
</step>

<step name="checkpoint_wave2_complete" priority="medium">
`checkpoint:verify` — Wave 2 outputs ready for review:

- [ ] LogisticRegression: result table + forest plot + README completed
- [ ] SurvivalAnalysis: KM curves + Cox results + README completed
- [ ] Effect size + 95%CI + exact p-value reported in all analyses
- [ ] Assumption tests performed and documented

User confirms outputs before proceeding to Wave 3.
</step>

<step name="execute_wave3" priority="high">
**Wave 3 — Depends on Wave 2 models.**

- **05_SubgroupAnalysis**: Forest plot with interaction p-values. Use bregr package.
- **06_SensitivityAnalysis**: Comparison table of main results under alternative assumptions. E-value calculation for unmeasured confounding.

Subgroup and sensitivity results reference the main models from Wave 2.
</step>

<step name="checkpoint_wave3_complete" priority="medium">
`checkpoint:verify` — Wave 3 outputs ready for review:

- [ ] SubgroupAnalysis: forest plot + interaction table + README
- [ ] SensitivityAnalysis: comparison table + README

User confirms outputs before proceeding to Wave 4.
</step>

<step name="execute_wave4" priority="high">
**Wave 4 — Depends on data partitioning.**

- **07_CorrelationAnalysis**: Spearman correlation matrix heatmap + scatter matrix.
- **08_ROCAnalysis**: Per-biomarker ROC → AUC + 95%CI → Wilson CI for sensitivity/specificity. Unadjusted (direct) and Adjusted (via logistic regression) modes (r_patterns §5). Youden index for optimal threshold. AUC forest plot (§8).
- **09_MarkerPanel**: LASSO feature selection (cv.glmnet, §6). Train/validation split (§10). Train ROC → apply threshold to validation. Confusion matrix heatmap (§7). Risk stratification jitter plot (§9). Performance bar chart. Train/validation ROC overlay.
- **10_SimpleML**: Random Forest / XGBoost / SVM. Feature importance. ROC curve.
</step>

<step name="verify_outputs" priority="medium">
After all waves complete, final verification:

1. Each method's figure(s) + table(s) + README exist
2. Figures ≥300 DPI, English labels, publication-grade theme applied
3. Statistical reports include effect size + 95%CI + exact p-value
4. Code independently runnable from cleaned.csv
5. R version and key package versions documented
</step>

</process>

<step name="milestone" priority="high">
Execute the milestone workflow to formally close Phase 2 and gate into Phase 3:

```bash
# The milestone workflow will:
# 1. Verify success criteria for Phase 2
# 2. Collect analysis decisions (method selection, parameters)
# 3. Generate .planning/phases/02-analysis/MILESTONE.md
# 4. Update ROADMAP.md: Phase 2 → ✅ Complete, Phase 3 → 🔄 In Progress
# 5. Update STATE.md: current_phase → 3
# 6. Request user sign-off
```

See @./pipeline/workflows/milestone.md for full protocol.
</step>

<statistical_reporting_standards>
- Every analysis: **effect size + 95%CI + exact p-value** (not just "p < 0.05")
- Multiple comparisons: apply FDR/Bonferroni correction
- Report software: R version + key package versions
- Test assumptions: normality, homoscedasticity, proportional hazards
- Flag violations and document mitigations
</statistical_reporting_standards>

<success_criteria>
- Each confirmed method has complete figure + table + README
- All figures meet publication-grade standards
- Statistical reports complete with effect size + 95%CI + p-value
- Wave execution order respected (Wave 1→2→3→4)
- Code in 03_AnalysisMethods/ independently reproducible
- user briefed after each wave
</success_criteria>
