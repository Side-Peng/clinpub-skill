# 导入模式工作流

## 目的

允许 clinpub 接管一个已存在的临床研究项目。检测文件、推断角色、与用户确认映射、分析差距、迁移文件到标准目录结构、设置正确的起始阶段。

## 前置阅读

- `../知识库/references/import-heuristics.md` — 导入启发式规则
- `../知识库/references/gates.md` — 质量门控
- `../知识库/references/templates/import-milestone.md` — 导入里程碑模板

## 步骤详解

### 1. 检测未完成导入

检查 `.clinpub/STATE.md`：
- 如果 `import_mode: true` 存在 → 上次导入被中断
  - 提示用户: "检测到上次导入未完成。输入 `continue` 继续，或 `restart` 重新开始。"
  - `continue` → 跳到差距分析
  - `restart` → 清除 import_mode 并从扫描开始

### 2. 扫描工件

扫描项目根目录和一级子目录：

| 类别 | 扩展名 | 额外模式 |
|------|--------|---------|
| 数据文件 | .csv, .xlsx, .xls, .tsv, .sav, .dta, .rds, .rda | 检查文件名中的 "cleaned", "raw", "data" |
| 图表文件 | .png, .pdf, .tiff, .svg, .jpg, .jpeg | 排除 .clinpub/ 图片 |
| 文档文件 | .md, .docx, .doc, .tex, .bib, .ris | 读取 .md 前 10 行确定类型 |
| 代码文件 | .R, .r, .Rmd, .py, .ipynb | 读取前 20 行确定功能 |
| 配置文件 | project_config.yml, MANIFEST.yaml | 直接识别 |

对于 .md 文件：读取前 10 行检测 IMRAD 章节标记。
对于代码文件：读取前 20 行检测功能（清洗/分析/绘图）。
对于数据文件：如果可行，读取表头获取列数和变量名。

同时检查标准 clinpub 目录：
- 01_RawData/ 存在?
- 02_PreprocessedData/data/cleaned.csv 存在?
- 03_AnalysisMethods/ 有子目录?
- 04_Outputs/ 有文件?
- 05_Manuscript/manuscript.md 存在?（兼容旧项目：若存在 `05_Manuscript/sections/` 文件，一并记录，导入时合并段落到 manuscript.md）
- Reference/ 有 .bib 文件?

### 3. 推断角色

**推断优先级**（高→低）：
1. **目录位置** — 已在标准目录中的文件直接分配角色（置信度: definite）
2. **文件名模式** — 强关键词匹配（置信度: high）
3. **内容采样** — 读取前 N 行的额外信号（置信度: medium）
4. **弱信号** — 仅扩展名匹配（置信度: low）

**角色 → 目标目录映射**:

| 角色 | 目标目录 |
|------|---------|
| raw_data | `01_RawData/` |
| cleaned_data | `02_PreprocessedData/data/cleaned.csv` |
| variable_dictionary | `02_PreprocessedData/data/` |
| data_quality_report | `02_PreprocessedData/reports/` |
| analysis_code | `03_AnalysisMethods/{method_id}/` |
| method_description | `03_AnalysisMethods/{method_id}/方法说明.md` |
| analysis_output_figure | `04_Outputs/{method_id}/` |
| analysis_output_table | `04_Outputs/{method_id}/` |
| reference_library | `Reference/references.bib` |
| manuscript_introduction | `05_Manuscript/manuscript.md`（## Introduction 段落） |
| manuscript_methods | `05_Manuscript/manuscript.md`（## Methods 段落） |
| manuscript_results | `05_Manuscript/manuscript.md`（## Results 段落） |
| manuscript_discussion | `05_Manuscript/manuscript.md`（## Discussion 段落） |
| manuscript_full | `05_Manuscript/manuscript.md` |

**旧项目兼容**：若源项目使用 `05_Manuscript/sections/01-introduction.md` 等分段文件，导入时将其段落内容按 IMRAD 顺序合并追加到 `05_Manuscript/manuscript.md`（带 `## {Section}` 标题），并告知用户已合并。

**方法子目录分组**:
- "baseline"/"table1" → `01_BaselineTable`
- "survival"/"kaplan"/"km" → `02_SurvivalAnalysis`
- "regression"/"logistic"/"cox" → `03_RegressionAnalysis`
- "comparison"/"t-test"/"wilcox" → `04_GroupComparison`
- 其他 → 顺序方法 ID

### 4. 呈现映射

以表格形式向用户展示推断的文件映射：

```
检测到 {total} 个研究文件，已自动推断角色：

数据文件:
#  | 文件                    | 推断角色        | 置信度 | 目标位置
1  | data/patients.csv       | 原始数据        | 中     | 01_RawData/
2  | cleaned_final.csv       | 清洗后数据      | 高     | 02_PreprocessedData/data/cleaned.csv

图表文件:
3  | results/table1.docx     | 基线表          | 高     | 04_Outputs/01_BaselineTable/

文档文件:
4  | draft_v2.docx           | 手稿(部分)      | 中     | 05_Manuscript/
5  | references.bib          | 参考文献库      | 确定   | Reference/

代码文件:
6  | analysis.R              | 分析代码        | 中     | 03_AnalysisMethods/

标记为 中/低 的项目建议确认。
输入序号修正角色（如 "3:raw_data"），输入 "confirm" 全部接受。
```

用户可以：
- `#N:new_role` 修正角色
- `#N:skip` 排除文件
- `confirm` 全部接受

### 5. 差距分析

**各 Phase 完整性检查**:

**Phase 0**: project_config.yml 和 .clinpub/ 目录（总是由导入生成）

**Phase 1**:
- cleaned.csv 存在 → PASS
- 数据质量报告缺失 → WARN
- 清洗代码缺失 → WARN
- 变量字典缺失 → INFO

**Phase 2**: 每个推断方法组检查 figure + table + 方法说明
- 方法说明缺失 → WARN（Gate 3 必需）
- 分析代码缺失 → INFO

**Phase 3**: 检查 manuscript.md 中 Introduction / Methods / Results / Discussion 段落
- 部分段落存在 → 标记已有段落，建议补全缺失

**起始 Phase 判断**:
- 有 cleaned.csv 但无分析输出 → 建议 Phase 2
- 有分析输出但无手稿 → 建议 Phase 3
- 有手稿（manuscript.md）→ 建议 Phase 3（续写）或 Phase 4（如完整）

### 6. 部分框架讨论

基于已有工件自动推断尽可能多的研究框架信息，只讨论缺失部分：

- 如果 cleaned.csv 存在：运行 data_profiler 获取变量列表
- 从 profile 推断研究类型、结局变量、协变量
- 从图表文件名推断已完成的分析方法
- 从手稿内容推断研究标题、设计、目标期刊
- 如果已有 project_config.yml：读取并使用已填写字段

**讨论范围**（仅询问无法自动推断的内容）：
1. 研究基础信息
2. 变量角色确认
3. 目标期刊
4. **IRB 信息**（强制——Gate 1 不可跳过）
5. 分析方法确认

### 7. 创建适配目录结构

1. **设置 import_mode 标志**: 写入最小 STATE.md 含 `import_mode: true`
2. **创建缺失目录**: 仅创建不存在的标准目录
3. **复制（永不移动）文件**: 保留原始文件在原位
4. **创建占位符方法说明**: 标记为"导入项目——方法说明待补全"
5. **特殊文件转换**: xlsx→csv 转换（如需要）
6. **清除 import_mode 标志**: 更新 STATE.md

### 8. 生成导入配置

**project_config.yml**: 从模板生成，填充推断值，添加 import 段：

```yaml
import:
  mode: true
  date: "{today}"
  source_description: "{description}"
  starting_phase: {phase}
  skipped_phases: [{skipped}]
  imported_files:
    - source: "{original}"
      target: "{clinpub}"
      role: "{role}"
  unverified_gates:
    - gate: {number}
      reason: "{reason}"
      status: "imported_unverified"
```

**STATE.md**: 设置起始 Phase，清除 import_mode
**ROADMAP.md**: 跳过的阶段标记"已跳过（导入）"
**决策日志**: 写入 `.clinpub/phases/00-init/00-IMPORT-CONTEXT.md`

### 9. 导入里程碑

生成 `IMPORT-MILESTONE.md`:

1. 导入摘要
2. 已导入文件表
3. 跳过阶段的 Gate 状态（PASS / UNVERIFIED / FAIL）
4. 差距修复计划
5. 用户签字清单

```
────────────────────────────────
导入完成 — 请确认

已将 {count} 个文件导入 clinpub 项目结构。
起始阶段: Phase {N} — {name}

未验证的 Gate 项 ({count}):
{summary}

请确认:
- 输入 "approved" 确认导入
- 或描述需要调整的地方
────────────────────────────────
```

## 成功标准

- 所有扫描文件有确认的角色（无未分类文件残留，或用户明确跳过）
- 文件已复制到标准目录结构
- project_config.yml 已生成（含 import 段）
- STATE.md 设置为正确的起始阶段（import_mode 已清除）
- ROADMAP.md 显示跳过阶段为"已跳过"
- IMPORT-MILESTONE.md 已生成
- Gate 1（IRB/伦理）信息已提供
- 用户已签字确认导入映射和起始阶段
