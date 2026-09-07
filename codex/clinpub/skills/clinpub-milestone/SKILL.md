---
name: clinpub-milestone
description: "Phase auto-verification. Review completed phase deliverables, verify success criteria, record decisions, and auto-advance to next phase. Generates MILESTONE.md and updates ROADMAP.md."
---

# ClinPub Milestone

Automated phase verification. Checks that the completed phase meets all success criteria, records key decisions and outputs, and auto-advances to the next phase.

This is the VERIFY step of the DISCUSS → PLAN → EXECUTE → VERIFY lifecycle.

## Execution Context

- Workflow: pipeline/workflows/milestone.md
- References: pipeline/references/checkpoints.md
- Templates: pipeline/templates/milestone.md

## Process

Execute the milestone workflow from pipeline/workflows/milestone.md end-to-end.

Triggers:
- **Auto**: Called at the end of each core phase workflow (init-project, data-prep, analysis, writing)
- **Manual**: User can invoke `clinpub:milestone <N>` at any time to check phase status (Phase 0-3 only)

Phase 3（writing）是最后一个编号阶段；独立工具（improving / coverletter / review / modify / data2idea）不使用 milestone 门控。

## Success Criteria

- MILESTONE.md generated in .clinpub/phases/NN-phase-name/
- All success criteria verified (or documented exceptions)
- ROADMAP.md updated with phase completion status
- STATE.md auto-advanced to next phase
- No blocking user confirmation required
