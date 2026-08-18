---
name: 稿件改进
description: "Standalone manuscript improvement tool: self-review the draft, produce a concrete revision plan, confirm with user, then directly revise the manuscript (full text + analysis code re-run + numeric cascade). No response letter, no simulated reviewers. Invocable anytime a manuscript draft exists; repeatable."
description_zh: "独立稿件改进工具——自审草稿、产出具体修改计划、用户确认后直接修订稿件（全文 + 分析代码重跑 + 数字级联）。不生成回复信、不模拟审稿人。稿件草稿存在即可调用，可重复执行"
version: 2.3.0
user-invocable: true
argument-hint: "自审稿件并直接修订"
---

# 稿件改进 — 自审与直接修稿

帮助研究者写作期间或之后持续改进稿件。对当前草稿进行结构化自审，提出具体的逐项修改计划，并在用户确认后直接执行修订——同时覆盖稿件文本和底层分析（必要时重跑 R/Python，级联更新数字）。这是可重复的改进工具（类似 分析修改），**不是阶段**；不模拟审稿人、不生成回复信。

## 前置校验（优先执行）

验证待改进的稿件草稿存在：

```bash
PROJECT_DIR=$(pwd)
MANUSCRIPT="$PROJECT_DIR/05_Manuscript/manuscript.md"
OUTPUTS="$PROJECT_DIR/04_Outputs/"
```

检查项：
1. `05_Manuscript/manuscript.md` 存在 — 否则报错："未找到稿件。请先执行 论文写作 技能。"
2. `project_config.yml` 存在（用于期刊级别、语言、变量）— 否则警告并以默认值继续。

检查通过即可执行。`稿件改进` 可重复调用。

## 步骤 1：结构化自审

对当前草稿进行结构化自审。这是**内部质量评估**——不是模拟审稿人角色、不是回复信练习。将发现表述为具体的改进机会。

自审严格度默认按目标期刊级别——从 `project_config.yml` 读取 `journal.name` + `journal.tier`；如未配置，应用 Q2 标准（见 `journal_standards.md`）。

按以下维度评估，每条发现标记为 Major 或 Minor：

**Major（实质问题）：**
- 统计方法的适当性与完整性（缺少关键分析、检验选择错误）
- 样本量与统计功效
- 混杂因素控制的充分性
- 结果解读与过度推断（结论超出证据）
- 未处理的研究设计局限

**Minor（表达问题）：**
- 语言、语法与流畅性
- 引用完整性、相关性与时效性
- 图表格式、清晰度与引用
- 报告规范合规性（STROBE/CONSORT/PRISMA）
- 交叉引用与占位符一致性

将评估写入 `05_Manuscript/improvement_plan.md`。每条发现包含：
- 位置（章节，尽量到行/段落）
- 问题描述
- 改进建议
- 严重程度（Major / Minor）
- 是否需要重跑分析？（是/否）— 标记 Phase 2 代码是否需要变更

## 步骤 2：提出修改计划

将评估转化为具体、逐项的修订计划（写入 `05_Manuscript/improvement_plan.md`），按执行类型分组：

1. **仅文本修改**：哪些章节/段落需要重写或精简（委托 论文写作 工作流）
2. **分析重跑**：哪些 `03_AnalysisMethods/{method_id}/` 需要改代码 / 新方法 / 重新渲染（委托 分析修改 工作流）及其影响的下游数字
3. **图表调整**：对 `04_Outputs/*` 的样式或内容修改
4. **文献补充**：需要新增引用的缺口（委托文献检索）

将计划呈现给用户确认。

## 步骤 3：检查点确认

呈现逐项计划并取得用户对范围的明确确认：

1. 展示所有改进项及严重程度和执行类型
2. 用户确认现在执行哪些项（可推迟部分）
3. 用户可追加额外改进请求
4. 在做出任何修改前就修订范围达成一致

用户拒绝 → 停止，不做任何修改。
用户确认 → 继续执行。

## 步骤 4：执行修订

按确认的条目执行。顺序以最小化级联失败：先分析重跑（改变数字），再图表调整，再文献，最后文本。

1. **分析重跑**（如有条目需要）：委托 分析修改 工作流（`execute_modifications` + `verify_modifications`）。
   - 修改前记录当前提交哈希作为回滚参考。
   - 新方法 ID 必须遵循 `{NN}_{MethodName}`；同时创建 `03_AnalysisMethods/{id}/` 和 `04_Outputs/{id}/`。
   - 不自动安装缺失包 — 报告并跳过。
2. **图表调整**：通过 分析修改 样式路径重新渲染（≥300 DPI、英文标签）。
3. **文献补充**：更新 `Reference/reference_library.json` + `references.bib`（去重、DOI 必需）。
4. **文本修订**：对每个受影响章节进行修订。
   - 以 `## {Section}` 标题定位段落，就地编辑 `05_Manuscript/manuscript.md` 中的受影响段落，不重建 sections/ 文件。
   - **数字级联**：修补 Results 中受影响的效应量、p 值、CI 边界；统计方法变更时更新 Methods。
   - 内联应用 Humanizer 清单（无 AI 模板模式）。

逐项报告成功/失败。

## 步骤 5：验证

修订后验证完整性：

**稿件：**
1. IMRAD 结构完整（Introduction, Methods, Results, Discussion）
2. 所有引用有 DOI；引用库已去重
3. 所有引用的图表存在于 `04_Outputs/`
4. 无残留占位符（`{{Table:N}}`、`{{Figure:N}}` 等）
5. 字数在目标期刊限制内；Humanizer 检查通过

**分析（如有重跑）：**
6. 图表文件存在、非零、≥300 DPI、英文标签
7. 统计报告包含效应量 + 95%CI + 精确 p 值
8. 变更方法已更新 `方法说明.md`

某项验证失败 → 报告具体失败项，并提供重跑或跳过选项。

## 步骤 6：记录

记录本轮改进（无里程碑 / 无阶段关闭——本工具可重复）：

1. 更新 `05_Manuscript/improvement_plan.md`：将每项标记为 `done` / `deferred` / `failed`，追加带时间戳的轮次头。
2. 更新 `.clinpub/STATE.md` 的 "Last activity" 行。

```
─────────────────────────────────────────
 Improving Complete (round {N})
─────────────────────────────────────────
Executed: {N} item(s)   Deferred: {M}   Failed: {K}
Analysis re-runs: {A}    Sections revised: {S}
Manuscript: 05_Manuscript/manuscript.md updated
Plan/log: 05_Manuscript/improvement_plan.md
─────────────────────────────────────────
下一步：
- 继续改进 → 再次运行 稿件改进
- 准备投稿信 → 投稿信
- 投稿后收到审稿意见 → 同行评审
```

用户要求更多修改 → 循环回步骤 1（或对重点条目循环回步骤 2）。

## 成功标准

- 前置校验通过（稿件草稿存在）
- 自审产出 Major/Minor 发现于 `05_Manuscript/improvement_plan.md`
- 具体逐项修订计划在修改前经用户确认
- 已确认条目全部执行：文本修订、必要时分析重跑、数字级联进稿件
- 新增引用（如有）带 DOI；引用库已去重
- 修订稿通过完整性检查（IMRAD、DOI、图表存在、无占位符、Humanizer）
- 未产出回复信、未模拟审稿人
- 改进轮次已记录；工具保持可重复（无阶段/里程碑关闭）

## 参考资料

- [期刊标准](../知识库/references/journal_standards.md) — 期刊分级与报告规范
- [检查点](../知识库/references/checkpoints.md) — 阶段内决策点与验证门
- [分析方法目录](../知识库/references/analysis_methods.md) — 统计方法目录
- [R代码模板](../知识库/references/r_patterns.md) — 共享图表配置
- [修改代理指南](../分析修改/references/modify-agent-guide.md) — 分析重跑与图表调整
- [写作工作流](../论文写作/references/writing-workflow.md) — 文本修订
