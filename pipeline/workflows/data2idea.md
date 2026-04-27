---
name: data2idea
description: "Topic mining workflow: profile data → scan literature → generate 3-5 candidate paper topics with feasibility scores. No statistical analysis or manuscript writing."
---

<purpose>
Mine paper topics from clinical data tables without performing statistical analysis. Three-step process: data profiling → literature scanning → topic generation. Each step shows intermediate results for user feedback.

Agent: @./agents/topic-miner-agent.md — dedicated topic mining specialist.
</purpose>

<required_reading>
@./pipeline/templates/study_types/
@./agents/topic-miner-agent.md
</required_reading>

<process>

<step name="run_data_profile" priority="first">
Read user-provided CSV or XLSX and generate comprehensive data profile:

```bash
python scripts/data_profiler.py <filepath> --output idea/data_profile.json
```

Profile includes:
1. **Variable inventory**: name, data type, missing rate, unique count
2. **Distribution summaries**: 5-number summary for continuous, frequencies for categorical
3. **Missing pattern**: high-missing (>20%) flagged, medium (5-20%) noted
4. **Correlation matrix**: Spearman for numeric variables (warning if >30)
5. **Variable role detection** (auto-inferred):
   - Outcome: outcome, diagnosis, status, death, event, 结局
   - Exposure/group: group, treatment, arm, exposure, trt, 随机
   - Time: time, follow, survival, months, days, 随访
   - Covariates: age, sex, gender, bmi, smoke, etc.
   - Biomarkers: biomarker, protein, gene, serum, plasma, score, etc.
6. **Study type prediction**:
   - Randomized group + baseline + follow-up → RCT
   - Time-to-event + exposure → cohort
   - Case/control + matching ID → case-control
   - Single time-point + exposure + outcome → cross-sectional
   - Descriptive variables only → descriptive
   - Multiple biomarkers + outcome → biomarker panel
7. **Sample size assessment**:
   - <50: descriptive only
   - 50-200: simple comparison
   - 200-500: regression analysis possible
   - 500-2000: most methods supported
   - >2000: complex modeling + subgroup analysis

Present profile to user. Confirm variable roles before proceeding.
</step>

<step name="literature_scan" priority="high">
Based on data profile, conduct PubMed literature search:

1. Extract disease keywords from variable names and user description
2. Search PubMed for existing research on: disease + exposure/biomarker + outcome
3. For multi-biomarker data: search each biomarker's research status
4. **Gap annotation**:
   - 🟢 **Recommended**: variable combination rarely seen (high novelty)
   - 🔶 **Considerable**: some existing research (differentiation needed)
   - ✅ **Not recommended**: well-studied, limited publication space

Check API key before search:
```bash
if [ -z "$NCBI_API_KEY" ]; then
  echo "⚠️ NCBI_API_KEY not set. PubMed at 3req/s rate limit."
fi
```

Write scan results to `idea/literature_scan.md`: search queries, key references, gap analysis.
</step>

<step name="generate_topics" priority="high">
Synthesize 3-5 candidate topics from data profile + literature scan:

**Topic selection strategy:**
- Large dataset (>5000 rows) → prioritize cohort or RCT topics
- Many biomarkers (>10) → prioritize marker panel or LASSO topics
- No grouping/outcome variables → descriptive study
- User-specified direction → match priority

**Each topic includes:**
- Working title
- Feasibility score (⭐1-5)
- Research type (cohort/RCT/cross-sectional/case-control/diagnostic/descriptive)
- Core research question + hypothesis
- Variable mapping (outcome, exposure, covariates, subgroups)
- Proposed analysis methods
- Key figures/tables needed
- Novelty/gap rationale
- Recommended target journals
- Risk notes (sample size, confounding, variable limitations)

Write complete report to `idea/选题报告.md`. User selects topic → guide them to `clinpub` for full pipeline.
</step>

</process>

<success_criteria>
- Data profile generated with variable inventory, roles, study type prediction
- Literature scan with gap analysis completed
- 3-5 candidate topics with feasibility scores, variable mapping, target journals
- User has selected a topic (or returned to refine search)
- User informed about next steps (clinpub pipeline)
</success_criteria>
