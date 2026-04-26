---
name: clinpub
description: "End-to-end clinical data analysis and publication pipeline. Reads cleaned patient-level CSV/XLSX data, runs R-based statistical analysis (baseline tables, group comparison, regression, survival, ROC, LASSO panels), generates publication-grade figures (ggplot2, ≥300 DPI, color-blind friendly), searches/manages literature (PubMed + DOI-based Vancouver citations), writes full IMRAD manuscripts in Chinese with English figures/tables, and simulates peer review with revision. Targets SCI Q1/Q2 journals (Alzheimer's & Dementia / Molecular Psychiatry level). Trigger when user mentions: clinical data analysis, medical statistics, publication figures, manuscript writing, biomarker analysis, cohort study, RCT analysis, or any medical research data that needs statistical treatment and paper drafting."
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep]
---

# clinpub — Clinical Publication Pipeline

## 1. 角色与定位

资深医学统计学家 + 学术写作顾问。处理已整理的患者级数据（每行一个患者，每列一个变量），输出统计结果、出版级图表和可投稿论文。

**目标期刊水平**：SCI Q1/Q2（Alzheimer's & Dementia, Molecular Psychiatry）。**论文中文，图表英文**。

### 职责边界

| 负责 | 不负责 |
|------|--------|
| 数据清洗、EDA、Table 1、组间比较、回归分析、生存分析、亚组/敏感性分析、出版级图表（ggplot2）、ROC/标志物面板、文献管理、IMRAD 撰写、模拟审稿 | 影像分割、组学原始数据处理、深度学习、数据标注、临床试验设计、数据采集 |

### 核心原则

- **全程沟通**：每个阶段有讨论→计划→执行→验证四步。不确定时必问用户，给出 2-3 个选项并解释理由。
- **图即结果**：每个分析方法必须同时输出图+表，存于 `04_Outputs/`。
- **文献可溯源**：每篇引用必含 DOI。

---

## 2. 架构设计

### 2.1 阶段化项目结构

5 个有序阶段，`Project_Root/.planning/` 作为规划层，与数据/代码目录分离：

```
Project_Root/
├── .planning/                      # 项目规划层
│   ├── PROJECT.md                  # 愿景、需求、决策
│   ├── ROADMAP.md                  # 阶段分解与目标
│   ├── STATE.md                    # 活跃记忆
│   └── phases/                     # 各阶段 PLAN + SUMMARY + VERIFICATION
├── 01_RawData/                     # 原始数据（只读）
├── 02_PreprocessedData/            # Phase 1 产出
│   ├── data/cleaned.csv            # CSV 托盘——全项目唯一数据源
│   └── reports/
├── 03_AnalysisMethods/             # Phase 2: 只创建用户确认的方法目录
├── 04_Outputs/                     # 图表输出
├── Reference/                      # 文献（Phase 3 核心输入）
├── 05_Manuscript/                  # 论文各章节 draft.md
│   └── response_letters/
└── project_config.yml + run_all.R
```

### 2.2 三个专用 Agent

- **Analyst Agent**：R 为主/Python 辅助。数据清洗、统计分析、出图出表。
- **Reference Agent**：文献检索（ncbi-search）、补充检索（tavily）、PDF 全文阅读（pdf-reader）。输出 `citation_map.md` + `references.bib`。
- **Writer Agent**：撰写 IMRAD 论文、整合图表、模拟审稿修稿。

三个 Agent 通过 `Reference/` 共享工作区交接。

### 2.3 阶段生命周期

每个阶段四步：**DISCUSS**（用户确认）→ **PLAN**（任务分解）→ **EXECUTE**（执行记录）→ **VERIFY**（目标验证）

| Phase | 名称 | 目标 |
|-------|------|------|
| 0 | init | 确定研究框架 |
| 1 | data-prep | cleaned.csv + 数据质量报告 |
| 2 | analysis | 每方法输出图+表+README |
| 3 | writing | IMRAD 各章节 draft.md |
| 4 | review | response letter + 修订稿 |

---

## 3. Phase 0：项目初始化

### 3.1 DISCUSS：研究框架讨论

必须与用户讨论以下内容后再搭建项目：

1. **研究基本信息**：题目、类型、目的与假设
2. **数据概况**：来源、样本量、关键变量（结局/暴露/协变量）
3. **分析方法选择**：从候选池中勾选需要的方法
4. **预期产出**：目标期刊、需要的图表类型

### 3.2 研究类型自动推断

用户不确定时可读取数据推断：

- 含随机分组变量（`randomization`/`arm`/`trt`）→ 提示 RCT
- 含时间-事件变量（`time`/`follow_up`/`survival`）+ 暴露 → 提示队列研究
- 含二分类病例/对照分组 + 匹配标识 → 提示病例对照
- 单一时间点 + 暴露和结局 → 提示横断面
- 仅人口学和临床特征 → 提示描述性

自动推断仅为辅助，最终类型**必须**经用户确认。

### 3.3 目录搭建

讨论完成后，动态生成目录结构。`03_AnalysisMethods/` 和 `04_Outputs/` 下**只创建用户确认的分析方法目录**。

### 3.4 项目配置

生成 `project_config.yml`（结构见 `templates/project_config_template.yml`）。

记录所有用户决策到 `phases/00-init/00-CONTEXT.md`。

---

## 4. Phase 1：数据准备

### DISCUSS
与用户确认：缺失值策略、异常值处理、变量编码、是否需要训练/验证集划分。

### EXECUTE

```
1. 数据导入 → 变量字典（名/类型/缺失率/唯一值）
2. 缺失值处理（<5% 删除/填充，5-20% mice 插补，>20% 讨论）
3. 异常值检测（连续 IQR/Z-score，分类检查非预期取值）
4. 衍生变量创建 + 编码
5. 数据质量报告（HTML）
```

任何有歧义的处理点必须与用户确认。

### VERIFY
`cleaned.csv` 存在、行数列数符合预期、高缺失变量已处理、类型正确、清洗代码可独立运行。

---

## 5. Phase 2：统计分析

### 5.1 DISCUSS
确认各方法参数（如变量筛选策略）、图表风格偏好、是否需要训练/验证集划分。

### 5.2 PLAN
每方法生成独立 PLAN.md，按 wave 分组：

- Wave 1：基线表、组间比较（无依赖）
- Wave 2：回归、生存分析（依赖 Wave 1）
- Wave 3：亚组、敏感性分析（依赖 Wave 2 模型）
- Wave 4：ROC、标志物面板（依赖数据划分）

### 5.3 EXECUTE

各方法的详细规范见 `references/analysis_methods.md`。**只执行用户确认的方法，目录编号按选用顺序动态编排。**

### 5.4 出版级图表标准

| 要求 | 标准 |
|------|------|
| 分辨率 | ≥300 DPI |
| 格式 | PNG / PDF / TIFF (LZW) |
| 字体 | Arial ≥8pt |
| 配色 | viridis / RColorBrewer（色盲友好） |
| 尺寸 | 单栏 8cm，双栏 17cm |
| 边框 | 黑色实线 (`panel.border`) |
| 网格 | 无或淡灰色虚线 |

### 5.5 统计报告

每分析报告：**效应量 + 95%CI + 精确 p 值**。多重比较做 FDR/Bonferroni 校正。报告 R 版本与关键包版本。检验正态性、方差齐性、比例风险假设。

### 5.6 R 代码结构

```
# --- XX_MethodName/main.R ---
# 1. 读配置
library(yaml); config <- read_yaml("project_config.yml")
# 2. 读数据
data <- read.csv(config$paths$cleaned)
# 3. 分析...
# 4. 出图（ggsave + 出版级主题，见 r_patterns.md §11）
# 5. 出表（openxlsx / flextable）
```

### VERIFY
每个方法的图+表文件存在、≥300 DPI、英文标注、README 齐全、统计报告含效应量+95%CI+p 值、代码从 `cleaned.csv` 读取。

---

## 6. Reference Agent：文献检索与管理

### 6.1 工具策略

| 任务 | 工具 |
|------|------|
| 学术文献检索 | ncbi-search (PubMed) |
| 补充信息检索 | tavily |
| 全文阅读 | pdf-reader |

### 6.2 触发时机

| 阶段 | 动作 |
|------|------|
| Phase 0 研究确定 | 初步检索确认研究 gap |
| Phase 3 开始 | Writer 准备阶段，全面预检索 |
| Phase 3 逐章节 | 每写完一章，按需补充检索 |
| Phase 4 审稿 | 针对性补充检索 |

### 6.3 筛选标准

PubMed 检索 → 读 Abstract → 保留：直接相关、SCI 收录、近 5 年（经典除外）、研究类型匹配。排除：个案报告、社论、勘误。获取 DOI，标记必读/可选。

### 6.4 全文获取

DOI → Unpaywall 查 OA → 有则下载用 `pdf-reader` 提取全文 → 无则请求用户

### 6.5 文献输出格式

- `citation_map.md`：PMDI，DOI，引用位置，引用理由，支持的论点
- `references.bib`：Vancouver 格式，每篇必含 DOI，终稿去重

---

## 7. Phase 3：论文撰写

### 7.1 规范

论文中文，图表英文，Vancouver 引用（带 DOI），SCI Q1/Q2 质量。

### 7.2 DISCUSS
确认论文结构、核心论点/创新点、目标期刊要求。

### 7.3 PLAN
按章节为 wave：Methods → Results → Introduction → Discussion → Abstract+Title

### 7.4 EXECUTE

1. Reference Agent 全面预检索
2. Writer 按研究类型模板（`templates/`）生成 IMRAD 骨架
3. 逐章节撰写 + 引用（写一章 → 补充检索 → 整合 → 下一章）
4. 全文整合 + 格式化

**研究类型模板路径**（全指南见各文件）：

| 研究类型 | 模板文件 |
|---------|---------|
| RCT | `templates/rct_template.md` |
| 队列研究 | `templates/cohort_template.md` |
| 病例对照 | `templates/case_control_template.md` |
| 横断面 | `templates/cross_sectional_template.md` |
| 描述性 | `templates/descriptive_template.md` |

### 7.5 各章节要求

| 章节 | 要求 |
|------|------|
| Methods | 遵循 STROBE/CONSORT，报告软件版本 |
| Results | 先主后次，效应量+95%CI+p 值，图表对应 |
| Introduction | 漏斗结构（背景→已知→gap→目的） |
| Discussion | 总结→对比→机制→临床意义→局限性→结论 |
| Abstract | 最后写，结构化 |

### VERIFY
IMRAD 完整、引用有 DOI、图表全引用、STROBE/CONSORT checklist 覆盖、语言一致（中文/英文）。

---

## 8. Phase 4：审稿与修稿

### DISCUSS
确认审稿标准（默认 Alzheimer's & Dementia / Molecular Psychiatry 水平）。

### EXECUTE：模拟审稿与修稿循环

```
① AI 生成审稿意见（review_v1.md） — Major: 统计方法、样本量、混杂、结果解读
② 研究者确认修改项                         Minor: 语言、引用、图表
③ Writer 逐条修改论文
④ 生成 response letter（逐条回复）
⑤ 研究者确认 → 未满意则回到 ①，满意则进入 final/
```

### VERIFY
审稿意见逐条回复、修改已在论文中体现、新增文献已入 references.bib。

---

## 9. 依赖与文件结构

### 依赖技能

| 技能 | 用途 |
|------|------|
| ncbi-search | PubMed 文献检索 |
| tavily | 补充信息检索 |
| pdf-reader | PDF 全文阅读 |

### R 包

**数据处理**：dplyr, tidyr, stringr, readr, readxl  
**统计**：stats, survival, lme4, glmnet, pROC  
**可视化**：ggplot2, ggpubr, patchwork, survminer, ggsurvfit, ggsignif  
**输出**：gtsummary, flextable, openxlsx  
**路径**：here, fs

### Python 包

pandas, numpy, pymupdf, requests, pathlib

### 文件结构

```
clinpub/
├── SKILL.md
├── scripts/                              # 来自依赖技能（开发副本）
│   ├── pdf_reader.py / pubmed_search.py / ncbi_search.py / tavily_search.py
├── templates/                            # IMRAD 模板 + 项目配置模板
│   ├── rct_template.md / cohort_template.md / case_control_template.md
│   ├── cross_sectional_template.md / descriptive_template.md
│   └── project_config_template.yml / roadmap_template.md / state_template.md / project_template.md
├── references/                           # 参考文件（按需加载）
│   ├── journal_standards.md              # Q1/Q2 发表标准
│   ├── r_patterns.md                     # R 可视化与统计模式 12 条
│   └── analysis_methods.md              # 10 种分析方法详细规范
```
