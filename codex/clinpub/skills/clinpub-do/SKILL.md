---
name: clinpub-do
description: "Read workspace state and auto-route to the appropriate clinpub command. With natural language input (e.g., 'clinpub:do 我想改清洗逻辑' or '我想写投稿信'), routes by intent. With no arguments, shows current state summary and suggests next commands."
---

# ClinPub Do

Workspace state router. Reads STATE.md, detects artifacts, and routes to the correct Phase command.

## 行为模式

- **无参数** (D-01): 读取 STATE.md + 检测关键工件 → 输出状态摘要 + 建议 1-3 条命令 → 用户确认后路由
- **有 NL 参数** (D-02): NL 意图识别优先于状态检测 → 成功则直接路由 → 失败则回退到无参行为（D-04）
- **路由依据** (D-03): 三合一决策：STATE.md `- 阶段：Phase N` + 工件检测 + 可选 NL 输入

## NL 意图推断规则

使用强信号关键词优先匹配策略，非简单包含匹配。关键词按优先级从高到低排列：

| 优先级 | 关键词（任一命中即路由） | 路由到 | 特异度 |
|--------|-------------------------|--------|--------|
| 1 | `(初始化\|init\|开始\|创建项目\|新建)` | init | 高 — 非清洗/分析语境 |
| 2 | `(清洗\|clean\|数据质量\|缺失\|异常值\|cleaned)` | data-prep | 高 — 特异性数据处理术语 |
| 3 | `(选题\|话题挖掘\|idea\|数据探索\|data2idea)` | data2idea | 高 — 选题挖掘术语 |
| 4 | `(审稿\|审稿意见\|reviewer\|回复信\|response\|rebuttal\|返修\|大修\|小修\|拒稿)` | review（投稿后） | 高 — 投稿后审稿回复术语（先于"稿"）|
| 5 | `(投稿信\|cover.?letter\|coverletter\|submission letter)` | coverletter | 高 — 投稿信术语 |
| 6 | `(改进\|完善\|润色\|自审\|打磨\|精修\|修订\|改稿\|improving)` | improving | 高 — 稿件改进术语（先于"稿"）|
| 7 | `(分析\|统计\|结果\|图\|表\|analysis\|figure\|table\|回归\|生存\|ROC)` | analysis | 高 — 分析术语 |
| 8 | `(写\|稿\|手稿\|文献\|引用\|writing\|IMRAD\|论文\|manuscript)` | writing | 高 — 写作术语 |
| 9 | `(推进\|下一步\|继续\|next\|advance)` | next-step | 高 — 推进术语 |
| 10 | `(状态\|摘要\|总览\|当前\|情况\|see\|status\|什么阶段)` | 回退到无参 | 明确表达"查看状态"意图，不是特定命令 |

**匹配规则**:
- 命中高优先级关键词立即路由，不继续检查低优先级（D-02：NL 优先于状态检测）
- review / coverletter / improving 组置于 writing 组之前，避免"审稿/投稿信/改稿"被 writing 组的"稿"抢先命中
- 命中第 9 组（推进）→ 执行自动推进；命中第 10 组（状态）→ 执行无参状态检测流程（D-04）
- 没有命中任何关键词组 → 回退到无参行为（D-04：推断不出明确意图）
- **跨组冲突时**（如同时包含"分析"和"写"）：以优先级高的为准（Group 编号小的优先），不按文本位置判断
- **反模式规避**: 不要匹配停用词（"看"、"查"、"项目"、"做"、"搞"、"弄"、"整"）

## 工件检测模式

```
Phase 0: -f project_config.yml + 验证 project.name != "项目名称"
Phase 1: -f 02_PreprocessedData/data/cleaned.csv
Phase 2: -d 04_Outputs && ls 04_Outputs/ 非空 + project_config.yml analysis_plan.waves
Phase 3: -f 05_Manuscript/manuscript.md  （核心管线终点）
```

Phase 3 完成后，improving / coverletter / review 为独立工具（需已有手稿），不占 Phase 编号。

## 命令路由映射

| 路由目标 | 命令名称 | 执行方式 |
|----------|---------|---------|
| Phase 0 | `clinpub:init` | 确认后提示用户执行 |
| Phase 1 | `clinpub:data-prep` | 确认后提示用户执行 |
| Phase 2 | `clinpub:analysis` | 确认后提示用户执行 |
| Phase 3 | `clinpub:writing` | 确认后提示用户执行 |
| 独立工具·改进 | `clinpub:improving` | 确认后提示用户执行（需已有手稿） |
| 独立工具·投稿信 | `clinpub:coverletter` | 确认后提示用户执行（需已有手稿） |
| 独立工具·审稿回复 | `clinpub:review` | 确认后提示用户执行（投稿后，需审稿意见） |
| 选题挖掘 | `clinpub:data2idea` | 确认后提示用户执行（无需初始化） |
| 自动推进 | `clinpub:next-step` | 确认后提示用户执行 |
| Phase 检查 | `clinpub:milestone <N>` | 确认后提示用户执行 |

## Process

1. 解析输入参数（NL 或无参）
2. 读取 STATE.md 获取当前 Phase（`- 阶段：Phase N`，Phase 0-3）
3. 执行工件检测（Phase 0-3 完成状态；Phase 3 完成后提示独立工具）
4. 输出状态摘要和建议命令（1-3 条）
5. 等待用户确认路由，不自动执行目标命令

## Success Criteria

- 无参数时输出准确的当前 Phase 状态摘要 + 1-3 条建议命令
- 带 NL 输入时正确推断意图并路由到对应命令
- NL 推断失败时正确回退到无参行为（显示状态摘要）
- 路由后等待用户确认，不自动执行目标命令
- Phase 3 完成时不再建议 Phase 4，改为建议 improving / coverletter / review 独立工具
- 所有命令的路由映射完整（init, data-prep, analysis, writing, improving, coverletter, review, next-step, milestone, data2idea）
- 不匹配停用词（"看"、"查"、"项目"、"做"）
