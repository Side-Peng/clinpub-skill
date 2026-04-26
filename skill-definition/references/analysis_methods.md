# 分析方法规范

> Phase 2 执行时参考本文件。每个方法必须同时输出图+表。

---

## 通用要求

- 全部读取 `cleaned.csv`，写入 `04_Outputs/XX_MethodName/`
- 统一应用出版级主题（见 `r_patterns.md §11`）
- 每方法生成 `README.md` 注明图例和表注
- 目录编号按用户确认的顺序动态编号

## 01_BaselineTable（基线表）

- **输出**：Table 1（三线表，docx格式）
- **内容**：按分组的人口学和临床特征
- **统计量**：连续变量用 mean±SD 或 median(IQR)；分类变量用 n(%)
- **组间比较**：t检验/卡方检验/秩和检验的 p 值

## 02_GroupComparison（组间比较）

- **输出**：比较结果表 + 箱线图/小提琴图
- **两组**：t检验 / Wilcoxon 秩和检验
- **多组**：ANOVA / Kruskal-Wallis + 事后比较
- **绘图**：
  - **三层绘图**：渐变背景 → 半透明散点(jitter) → 透明箱线图叠加（见 `r_patterns.md §1`）
  - 量纲差异大时先做 **Z-score 标准化**（见 `r_patterns.md §2`）
  - **动态显著性标注**：自动 y 轴留白 + `ggsignif` + `map_signif_level` 格式化 p 值（见 `r_patterns.md §3`）
  - 多变量并列用 `patchwork::wrap_plots()`（见 `r_patterns.md §12`）
  - 含训练集/验证集标记则分别出图
- **导出**：描述统计 + 组间比较到 Excel

## 03_LogisticRegression（Logistic 回归）

- **输出**：回归结果表（OR, 95%CI, p值） + 森林图
- **流程**：单因素 → 多因素 → 模型诊断
- **模型诊断**：Hosmer-Lemeshow 检验、VIF、ROC 曲线

## 04_SurvivalAnalysis（生存分析）

- **输出**：KM 生存曲线 + Cox 回归结果表 + 森林图
- **KM 曲线**：带风险表、Log-rank p 值、中位生存时间
- **Cox 回归**：单因素→多因素，PH 假设检验
- **推荐包**：KMunicate / ggsurvfit

## 05_SubgroupAnalysis（亚组分析）

- **输出**：亚组森林图 + 交互作用检验表
- **推荐包**：bregr

## 06_SensitivityAnalysis（敏感性分析）

- **输出**：敏感性分析结果对比表
- **常见方案**：排除特殊人群、不同定义、E-value

## 07_CorrelationAnalysis（相关性分析）

- **输出**：相关系数矩阵热图 + 散点图矩阵

## 08_ROCAnalysis（ROC 分析）

- **输出**：单指标 ROC 曲线 + 综合 ROC 曲线 + 森林图（AUC 汇总）
- **流程**：逐个标志物计算 ROC → AUC + 95%CI → Wilson CI 敏感度/特异度
- **两种模式**：
  - Unadjusted：`pROC::roc(outcome ~ biomarker)`（见 `r_patterns.md §5`）
  - Adjusted：Logistic 回归含协变量 → 预测概率做 ROC（见 `r_patterns.md §5`）
- **关键计算**：
  - **Wilson Score CI**（见 `r_patterns.md §4`）
  - **最佳阈值**：Youden 指数（`coords(roc_obj, "best")`，见 `r_patterns.md §5`）
  - **VR**：sqrt(敏感度 × 特异度)
- **AUC 森林图**：多标志物 AUC + 95%CI 汇总（见 `r_patterns.md §8`）

## 09_MarkerPanel（多标志物面板建模）

- **输出**：LASSO 特征选择结果 + 训练/验证集 ROC + 风险分层散点图 + 混淆矩阵热图 + 性能条形图
- **流程**：
  1. 训练/验证集分割（容错匹配，见 `r_patterns.md §10`）
  2. LASSO 交叉验证：`cv.glmnet(alpha=1)` → `lambda.min`（见 `r_patterns.md §6`）
  3. 提取非零系数，排除截距
  4. 训练集 ROC + 最佳阈值（见 `r_patterns.md §5`）
  5. 验证集应用 → 混淆矩阵热图（见 `r_patterns.md §7`）
  6. 性能条形图（Sensitivity, Specificity, PPV, NPV, F1）
- **可视化**：
  - **风险分层 jitter plot**：预测概率散点 + 阈值分割线（见 `r_patterns.md §9`）
  - **混淆矩阵热图**：频数 + 百分比双标注（见 `r_patterns.md §7`）
  - 统一应用出版级主题（见 `r_patterns.md §11`）

## 10_SimpleML（机器学习）

- **输出**：模型性能表 + ROC 曲线 + 特征重要性图
- **方法**：随机森林 / XGBoost / SVM
