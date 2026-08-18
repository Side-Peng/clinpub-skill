---
name: 投稿信
description: "Cover letter generation tool. Based on the target journal defined at initialization, gather the journal's official submission requirements (author guidelines / submission page) via web search, then draft a tailored cover letter. Falls back to journal-tier best practices if the web is unavailable. Output: 05_Manuscript/cover_letter.md."
description_zh: "投稿信生成工具——基于初始化时确定的目标期刊，联网检索期刊官方投稿要求（作者指南/投稿页面），生成量身定制的投稿信；联网不可用时降级到期刊分级最佳实践"
version: 2.3.0
user-invocable: true
argument-hint: "按目标期刊生成投稿信"
---

# 投稿信 — Cover Letter 生成

生成一份可直接投稿的目标期刊定制投稿信。从 `project_config.yml` 读取目标期刊（初始化时设定），检索期刊官网的投稿要求，撰写匹配期刊投稿信预期与宗旨范围的投稿信。只要稿件草稿存在即可随时调用。

## 前置校验（优先执行）

验证输入：

```bash
PROJECT_DIR=$(pwd)
MANUSCRIPT="$PROJECT_DIR/05_Manuscript/manuscript.md"
```

检查项：
1. `05_Manuscript/manuscript.md` 存在 — 否则报错："未找到稿件。请先执行 论文写作 技能。"
2. 从 `project_config.yml` 读取目标期刊：`journal.name`（优先）或 `project.target_journal`。
   - 如果期刊为空或"待定" → **立即询问用户**目标期刊（名称 + 级别），并写回 `project_config.yml`，确保下游步骤和后续工具保持一致。

## 步骤 1：收集期刊信息

收集期刊官方投稿要求。优先实时来源，允许优雅降级。

1. **定位官方指南**（WebSearch）：在官方出版社域名上搜索该期刊的 "author guidelines" / "guide for authors" / "submission guidelines" / "cover letter requirements"
2. **提取要求**（WebFetch 最佳匹配官方页面）：
   - 投稿信特定要求（必需声明、收件人/编辑、长度、格式）
   - 期刊宗旨与范围（用于定制契合度/重要性论证）
   - 与投稿信相关的投稿检查项（原创性、无同时投稿、伦理/IRB、数据共享、推荐/回避审稿人、利益冲突、作者署名、通讯作者）
3. **简要记录发现**（来源 URL）以保证透明。

**降级方案（联网不可用或未找到期刊）**：告知用户，然后使用 `journal_standards.md` 的期刊分级 + 临床投稿信通用最佳实践。在输出中明确注明要求未与期刊官网核对。

## 步骤 2：撰写投稿信

撰写定制投稿信并写入 `05_Manuscript/cover_letter.md`。从 `05_Manuscript/manuscript.md` + `project_config.yml` 提取稿件标题、关键发现和研究类型。

结构（根据上面收集到的期刊具体要求调整）：
1. 日期、通讯作者信息、编辑/期刊收件人
2. 稿件标题和文章类型；向本期刊投稿的声明
3. 重要性与新颖性 — 研究为何重要、如何契合期刊宗旨与范围
4. 关键发现的简明摘要（2-4 句，不过度声明）
5. 期刊要求的合规声明：原创性 / 未同时投稿 / 所有作者批准 / 伦理批准（IRB）与知情同意 / 数据可用性 / 利益冲突
6. 推荐（以及如被要求则回避的）审稿人 — 仅当期刊邀请时
7. 通讯作者联系方式与结尾

按 `language.manuscript` 配置的语言撰写（默认中文），除非期刊要求英文；保持简洁（通常 < 1 页）。

## 步骤 3：验证

检查草稿：
1. 期刊要求的每个投稿信要素都存在（或明确标注不适用）
2. 标题和关键发现与稿件一致
3. 没有超出稿件证据的过度声明
4. 用户特定字段的占位符（编辑姓名、日期、作者单位）清晰标注待用户填写

将投稿信呈现给用户，按需迭代。

```
────────────────────────────────
Cover Letter 已生成

文件：05_Manuscript/cover_letter.md
目标期刊：{journal}
来源：{已核对期刊官网 / 未联网，使用通用标准（请自行核对）}

请检查署名、编辑姓名、日期等占位项，并确认或提出修改意见。
────────────────────────────────
```

## 成功标准

- 稿件前置校验通过；目标期刊已解析（缺失时已询问）
- 从官网收集到期刊投稿要求（或已注明优雅降级）
- 投稿信已写入 `05_Manuscript/cover_letter.md`，按期刊宗旨与范围定制
- 包含期刊要求的全部投稿信要素与合规声明
- 关键发现与稿件一致；无过度声明
- 用户特定字段已清晰标注为占位符待填写

## 参考资料

- [期刊标准](../知识库/references/journal_standards.md) — 期刊分级与报告规范
- [检查点](../知识库/references/checkpoints.md) — 阶段内决策点与验证门
