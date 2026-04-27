---
name: clinpub:writing
description: "Phase 3: IMRAD manuscript writing. Reference Agent performs literature search, Writer Agent follows study type template to draft full IMRAD manuscript in Chinese with English figures/tables. Vancouver citations with DOIs."
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
Phase 3: Manuscript writing. Draft a complete IMRAD manuscript in Chinese (English figures/tables) targeting SCI Q1/Q2 journals.

Two-agent workflow: Reference Agent (literature search) → Writer Agent (manuscript drafting). Follows the appropriate research type template (RCT/cohort/case-control/cross-sectional/descriptive).
</objective>

<execution_context>
@./pipeline/workflows/writing.md
@./pipeline/references/journal_standards.md
</execution_context>

<process>
Execute the writing workflow from @./pipeline/workflows/writing.md end-to-end.
</process>

<success_criteria>
- IMRAD structure complete (Methods → Results → Introduction → Discussion → Abstract)
- All citations have DOIs
- All figures/tables referenced in text
- STROBE/CONSORT checklist covered
- Language consistent (Chinese manuscript, English figures/tables)
- No AI-template patterns (checked via Humanizer checklist)
</success_criteria>
