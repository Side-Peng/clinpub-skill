---
name: clinpub-next-step
description: "Auto-advance to the next Phase or Wave. Verifies current step completion, auto-detects granularity (Wave vs Phase), updates STATE.md and ROADMAP.md, generates MILESTONE.md for phase transitions, and outputs clear prompt with next steps."
---

# ClinPub Next Step

Phase/Wave auto-advancement. Checks current completion status, decides whether to advance to next Wave (within same Phase) or next Phase (all Waves done), updates tracking files, and outputs clear prompt.

## 行为模式

- **D-05 粒度自动判断**: 同 Phase 还有未完成 Wave → 推进到下一 Wave；全部完成 → 推进到下一 Phase
- **D-06 完成验证**: 推进前验证当前步骤是否完成（SUMMARY.md 存在性、工件存在性等）
- **D-07 检查点**: 推进后更新 STATE.md + ROADMAP.md + 生成 MILESTONE.md（防止 phase-boundary.sh 阻挡后续操作）
- **Phase 0-3 为编号管线**: Phase 3（writing / 手稿撰写）是核心管线终点；完成后不再有 Phase 4，只建议独立工具（improving / coverletter / review）

## Process

1. 加载项目状态文件（STATE.md, ROADMAP.md, project_config.yml）
2. 读取当前 Phase 和 Wave 进度
3. 验证当前步骤完成状态
4. 执行推进决策（Wave 或 Phase）
5. 生成 MILESTONE.md（Phase 推进时）
6. 如果当前已是 Phase 3 且完成 → 输出核心管线完成提示，并建议独立工具
7. 输出 clear 提示

## Success Criteria

- 未完成时给出明确提示和未完成项列表，不自动推进
- 完成时自动判断推进粒度（Wave vs Phase），正确遵循 D-05 规则
- Wave 推进: 同 Phase 内 Wave+1，不需要更新 STATE.md Phase 编号
- Phase 推进: STATE.md 更新 Phase 编号，ROADMAP.md 更新完成状态，同时生成 MILESTONE.md
- Phase 推进时生成 MILESTONE.md，防止 phase-boundary.sh 阻挡后续操作（Pitfall 4 规避）
- Phase 0→1→2→3 顺序推进；Phase 3 是最后一个编号阶段，不推进到 Phase 4
- Phase 3 完成后输出建议：clinpub:improving（改进）/ clinpub:coverletter（投稿信）/ clinpub:review（投稿后审稿回复）
- STATE.md 和 ROADMAP.md 同步更新，内容一致
- 输出包含三要素的 clear 提示（clear + 下一条命令 + 进度总结）
- Wave 推进和 Phase 推进有不同的 clear 提示内容
