#!/usr/bin/env bash
# clinpub-phase-boundary.sh
#
# Claude Code hook that enforces phase boundary conditions.
# Checks that prerequisite milestones are complete before starting a new phase.
#
# Installed as: PreToolUse hook for Bash tool
# Trigger: When agent runs analysis commands (Rscript, python analysis scripts)

set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-$(pwd)}"
STATE_FILE="$PROJECT_DIR/.planning/STATE.md"
ROADMAP_FILE="$PROJECT_DIR/.planning/ROADMAP.md"

# Color codes for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

check_phase_boundary() {
  local target_phase="$1"
  local prev_phase=$((target_phase - 1))

  # Phase 0 has no prerequisite
  if [ "$prev_phase" -lt 0 ]; then
    echo -e "${GREEN}OK: Phase 0 has no prerequisite.${NC}"
    return 0
  fi

  # Check STATE.md exists
  if [ ! -f "$STATE_FILE" ]; then
    echo -e "${RED}BLOCK: .planning/STATE.md not found. Run '/clinpub init' first.${NC}"
    return 1
  fi

  # Check if previous phase milestone is signed off
  if grep -q "Phase $prev_phase.*✅\|Phase $prev_phase.*Complete\|Phase $prev_phase.*signed" "$STATE_FILE" 2>/dev/null; then
    echo -e "${GREEN}OK: Phase $prev_phase milestone complete.${NC}"
    return 0
  fi

  # Check milestone files
  local milestone_dir="$PROJECT_DIR/.planning/phases/"
  if [ -d "$milestone_dir" ]; then
    local prev_milestone
    prev_milestone=$(find "$milestone_dir" -name "MILESTONE.md" -path "*$prev_phase*" 2>/dev/null | head -1)
    if [ -n "$prev_milestone" ] && grep -qi "Complete\|✅" "$prev_milestone" 2>/dev/null; then
      echo -e "${GREEN}OK: Phase $prev_phase milestone file found and complete.${NC}"
      return 0
    fi
  fi

  # Check for gate requirements
  if [ -f "$PROJECT_DIR/pipeline/references/gates.md" ]; then
    echo -e "${YELLOW}WARNING: Phase $prev_phase milestone not confirmed.${NC}"
    echo -e "${YELLOW}Gate verification required before starting Phase $target_phase.${NC}"
  fi

  echo -e "${RED}BLOCK: Phase $prev_phase is not marked as complete in STATE.md.${NC}"
  echo -e "${RED}Complete Phase $prev_phase and get milestone signoff before proceeding.${NC}"
  return 1
}

check_data_exists() {
  local phase="$1"

  case "$phase" in
    1)
      # Phase 1 needs raw data
      if [ ! -d "$PROJECT_DIR/01_RawData" ] || [ -z "$(ls "$PROJECT_DIR/01_RawData/"*.csv 2>/dev/null)" ]; then
        echo -e "${RED}BLOCK: No raw data files found in 01_RawData/.${NC}"
        return 1
      fi
      ;;
    2)
      # Phase 2 needs cleaned data
      if [ ! -f "$PROJECT_DIR/02_PreprocessedData/data/cleaned.csv" ]; then
        echo -e "${RED}BLOCK: cleaned.csv not found. Complete Phase 1 data preparation first.${NC}"
        return 1
      fi
      ;;
    3)
      # Phase 3 needs analysis outputs
      if [ ! -d "$PROJECT_DIR/04_Outputs" ] || [ -z "$(ls "$PROJECT_DIR/04_Outputs/" 2>/dev/null)" ]; then
        echo -e "${RED}BLOCK: No analysis outputs found in 04_Outputs/. Complete Phase 2 first.${NC}"
        return 1
      fi
      ;;
    4)
      # Phase 4 needs manuscript
      if [ ! -f "$PROJECT_DIR/05_Manuscript/manuscript.md" ]; then
        echo -e "${RED}BLOCK: manuscript.md not found. Complete Phase 3 writing first.${NC}"
        return 1
      fi
      ;;
  esac

  return 0
}

# Main execution
main() {
  # Read command from stdin (hook protocol)
  local input
  input=$(cat)

  local command
  command=$(echo "$input" | grep -o '"command":"[^"]*"' | head -1 | cut -d'"' -f4 2>/dev/null || echo "")

  if [ -z "$command" ]; then
    echo '{"decision":"allow"}'
    exit 0
  fi

  # Detect phase from command patterns
  local target_phase=-1

  if echo "$command" | grep -qi "Rscript.*analysis\|python.*analysis\|03_AnalysisMethods\|04_Outputs"; then
    target_phase=2
  elif echo "$command" | grep -qi "data_prep\|preprocess\|clean.*data\|02_PreprocessedData"; then
    target_phase=1
  elif echo "$command" | grep -qi "manuscript\|writing\|05_Manuscript"; then
    target_phase=3
  elif echo "$command" | grep -qi "review\|final"; then
    target_phase=4
  fi

  if [ "$target_phase" -lt 0 ]; then
    # Not a phase-specific command, allow
    echo '{"decision":"allow"}'
    exit 0
  fi

  # Check phase boundary
  if ! check_phase_boundary "$target_phase" >/dev/null 2>&1; then
    local reason
    reason=$(check_phase_boundary "$target_phase" 2>&1 | grep "BLOCK:" | head -1)
    echo "{\"decision\":\"block\",\"reason\":\"$reason\"}"
    exit 0
  fi

  # Check data prerequisites
  if ! check_data_exists "$target_phase" >/dev/null 2>&1; then
    local reason
    reason=$(check_data_exists "$target_phase" 2>&1 | grep "BLOCK:" | head -1)
    echo "{\"decision\":\"block\",\"reason\":\"$reason\"}"
    exit 0
  fi

  echo '{"decision":"allow"}'
}

main
