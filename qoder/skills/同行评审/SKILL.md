---
name: 同行评审
description: "Post-submission peer-review response workflow. Intake the reviewers' real comments provided by the user, draft a point-by-point response letter and improvement directions, confirm with the user, then delegate the actual revision to the improving workflow. Loops per revision round until the user is satisfied."
description_zh: "投稿后同行评审回复工作流——录入用户提供的真实审稿意见，起草逐条回复信和改进方向，用户确认后委托稿件改进技能执行实际修订。按审稿轮次循环直至用户满意"
version: 2.3.0
user-invocable: true
argument-hint: "录入审稿意见并处理回复"
---

# 同行评审 — 投稿后审稿意见处理

处理投稿后阶段：稿件已提交、期刊返回审稿意见后，本技能录入审稿人的**真实意见**（由用户提供），起草逐条回复信和具体改进方向，取得用户确认后，将实际的稿件+分析修订委托给 `稿件改进` 技能执行。**不模拟审稿人**——真实审稿意见是必需的输入。

## 前置校验（优先执行）

验证待修订的已投稿稿件存在：

```bash
PROJECT_DIR=$(pwd)
MANUSCRIPT="$PROJECT_DIR/05_Manuscript/manuscript.md"
```

检查项：
1. `05_Manuscript/manuscript.md` 存在（已投稿的草稿）— 否则报错："未找到稿件。本命令用于投稿后处理审稿意见。请先执行 论文写作 技能。"
2. `project_config.yml` 存在（期刊名称/级别、语言）— 否则警告并继续。

## 步骤 1：收集审稿意见

审稿意见是**必需的输入**——不得捏造或模拟。

以两种方式之一请用户提供期刊审稿意见：
1. 将完整的审稿人/编辑意见直接粘贴到对话中，或
2. 提供文件路径（如 `05_Manuscript/` 下保存的决策信）。

如果用户两者都不提供，停止并解释：本命令处理投稿后的真实审稿反馈；如需在无审稿人情况下自审改进草稿，请使用 `稿件改进` 技能。

可选：记录编辑决定（大修 / 小修 / 拒稿重投）以校准语气和范围。

## 步骤 2：解析意见

将原始意见规范化为结构化列表并保存到 `05_Manuscript/reviewer_comments.md`：

每条意见记录：
- 审稿人编号和意见编号（如 Reviewer 2, Comment 3）
- 意见原文（引用）
- 类别：Major / Minor
- 所需行动类型：文本修改 / 补充分析 / 新增文献 / 澄清 / 反驳（持异议并说明理由）
- 可识别的受影响稿件位置

向用户呈现简明摘要表（审稿人 × 意见数量、Major/Minor 分布）。

## 步骤 3：起草回复信与改进方向

为每条意见起草两个关联产物：

1. **逐条回复信**（`05_Manuscript/final/response_letter.md`）：
```markdown
## Reviewer 1, Comment 1
> [审稿人意见原文]

**Response**: [如何解决该关切——或带有理由的礼貌反驳]
**Changes**: [稿件中将修改什么、改在哪里（章节、行/页）]

## Reviewer 1, Comment 2
...
```
每条回复必须：感谢审稿人，说明将修改什么及原因，如不修改则给出明确理由。

2. **改进方向**：将每条意见映射到 `稿件改进` 将执行的具体修订动作（文本修改、分析重跑、图表变更、新引用）。这成为交给 `稿件改进` 的已确认范围。

将两者呈现给用户。

## 步骤 4：检查点确认

修订前取得用户明确确认：

1. 展示回复信草稿 + 改进方向
2. 用户编辑/批准回复策略（可调整反驳、推迟条目、追加要求）
3. 就本轮修订范围达成一致

用户拒绝 → 停止（回复信草稿保留供手动使用）。
用户确认 → 继续执行。

## 步骤 5：执行修订

将实际的稿件+分析修订委托给 `稿件改进` 技能，范围限定为已确认的审稿驱动方向：

- 以已确认的改进方向作为预先商定的计划执行 `稿件改进`：
  - 跳过其开放式的 `self_review`（范围已由审稿意见定义）；从 `execute_revisions` 带着已确认条目进入。
  - 稿件改进 负责：分析重跑（分析修改 工作流）、图表调整、文献补充、文本修订（论文写作 工作流）、数字级联和完整性验证。

这保持了修订逻辑的单一实现（无重复）。

## 步骤 6：定稿

组装修订包并按需循环：

1. 将修订稿写入 `05_Manuscript/final/manuscript.md`（保留修订前版本供对比）。
2. 用稿件改进 轮次中填写的实际修改位置定稿 `05_Manuscript/final/response_letter.md`。
3. 如新增引用，更新 `Reference/references.bib`。
4. 呈现给用户：
   - 用户要求更多修改 → 循环回步骤 2 / 步骤 3 进行另一轮修订（如第二轮审稿）。
   - 用户满意 → 完成。

最终交付物：
- `05_Manuscript/reviewer_comments.md` — 规范化审稿意见
- `05_Manuscript/final/manuscript.md` — 修订稿
- `05_Manuscript/final/response_letter.md` — 给审稿人的逐条回复

```
────────────────────────────────
审稿意见处理完成（本轮）

已生成：
- 修订稿：05_Manuscript/final/manuscript.md
- 回复信：05_Manuscript/final/response_letter.md

请确认：输入 "approved" 结束本轮，或提供下一轮审稿意见继续。
────────────────────────────────
```

## 成功标准

- 稿件前置校验通过
- 从用户处收集到真实审稿意见（绝不模拟）并规范化为 `05_Manuscript/reviewer_comments.md`
- 起草了逐条回复信并附改进方向
- 用户确认了回复策略和修订范围
- 实际修订通过 稿件改进 技能执行（修订逻辑单一来源）
- 修订稿 + 回复信位于 `05_Manuscript/final/`
- 新增引用（如有）已加入 references.bib
- 支持多轮修订直至用户满意

## 参考资料

- [期刊标准](../知识库/references/journal_standards.md) — 期刊分级与报告规范
- [检查点](../知识库/references/checkpoints.md) — 阶段内决策点与验证门
- [稿件改进](../稿件改进/SKILL.md) — 实际修订执行者
- [写作工作流](../论文写作/references/writing-workflow.md) — 文本修订
