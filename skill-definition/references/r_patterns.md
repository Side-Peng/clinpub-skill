# R 可视化与统计模式（默会知识）

> 从实际发表级 R 代码中提取的核心模式。不要原文照搬，而是理解其设计意图，在生成代码时灵活运用。

---

## 1. 三层绘图法（箱线图 + 散点叠加）

### 意图
既展示数据分布的整体概览（箱线图），又展示每个个体的具体数值（散点），避免箱线图掩盖数据特征。

### 模式
```r
# 第一层：渐变背景（可选）
ggplot(data, aes(x = group, y = value)) +
  geom_rect(aes(xmin = -Inf, xmax = Inf, ymin = -Inf, ymax = Inf), fill = "grey95") +
  # 第二层：散点（半透明，展示个体数据）
  geom_jitter(aes(fill = group), color = alpha("gray50", 0.4), 
              shape = 21, width = 0.2, size = 2) +
  # 第三层：箱线图（透明填充，叠加在散点上）
  geom_boxplot(aes(fill = group), alpha = 0.0, color = "black", 
               outlier.shape = NA, width = 0.5)
```

### 何时用
- 组间比较（样本量 < 200）
- 需要展示个体变异时
- 箱线图 + 散点组合作对比

### 变体
- 小提琴图替代箱线图：`geom_violin(alpha = 0.3)` + `geom_boxplot(width = 0.1)`
- 大样本时仅用箱线图或小提琴图，省略散点

---

## 2. Z-score 标准化可视化

### 意图
将不同量纲的变量统一到同一尺度上进行可视化比较。

### 模式
```r
scale_this <- function(x) {
  (x - mean(x, na.rm = TRUE)) / sd(x, na.rm = TRUE)
}
```

### 何时用
- 同一图中展示多个不同量纲的变量
- 热图中统一色标范围
- 比较不同标志物在组间的相对差异

---

## 3. 动态显著性标注

### 意图
自动计算显著性标注的位置，避免手动硬编码 y 坐标。

### 模式
```r
# 计算 y 轴范围
y_range <- max(data$value, na.rm = TRUE) - min(data$value, na.rm = TRUE)
y_max <- max(data$value, na.rm = TRUE) + y_range * 0.1  # 留 10% 空白

# 使用 ggsignif
library(ggsignif)
geom_signif(
  comparisons = list(c("Group1", "Group2")),
  map_signif_level = function(p) {
    ifelse(p < 0.001, "italic(p) < 0.001", 
           sprintf("italic(p) == %.3f", p))
  },
  test = "t.test", 
  textsize = 3.5, 
  parse = TRUE,
  y_position = y_max + seq(0, by = y_range * 0.08, length.out = n_comparisons)
)
```

### 关键细节
- `map_signif_level` 用自定义函数格式化 p 值，而非默认的星号
- `parse = TRUE` 启用表达式解析，支持斜体
- `y_position` 动态偏移，多个比较时阶梯排列

---

## 4. Wilson Score 置信区间

### 意图
为敏感度/特异度等比例指标计算精确置信区间（优于正态近似）。

### 模式
```r
wilson_ci <- function(p, n, z_alpha = 1.96) {
  denominator <- 1 + z_alpha^2 / n
  centre <- (p + z_alpha^2 / (2 * n)) / denominator
  margin <- z_alpha * sqrt(p * (1 - p) / n + z_alpha^2 / (4 * n^2)) / denominator
  c(lower = centre - margin, upper = centre + margin)
}
```

### 何时用
- ROC 分析中敏感度/特异度的置信区间
- 患病率/检出率的置信区间
- 任何比例指标的 CI（样本量较小时尤其重要）

---

## 5. ROC 分析双模式

### 意图
区分"仅标志物"（Unadjusted）和"调整协变量后"（Adjusted）的区分能力。

### 模式
```r
# Unadjusted：直接基于标志物值
library(pROC)
roc_obj <- roc(outcome ~ biomarker, data = df)
auc_obj <- auc(roc_obj)
ci_obj <- ci.auc(roc_obj)

# Adjusted：先做 Logistic 回归，用预测概率做 ROC
model <- glm(Outcome ~ biomarker + age + sex, data = df, family = binomial)
pred_prob <- predict(model, type = "response")
roc_adjusted <- roc(df$Outcome, pred_prob)
```

### 最佳阈值选取
```r
coords_best <- coords(roc_obj, "best", 
  ret = c("threshold", "sensitivity", "specificity", 
          "ppv", "npv", "accuracy"))
```

### 何时用
- 生物标志物诊断价值评估
- 需要对比"单纯标志物"vs"综合模型"的 AUC
- 需要报告最佳阈值和对应的诊断性能

---

## 6. LASSO 特征选择流程

### 意图
从高维生物标志物中筛选最具有区分能力的特征子集。

### 模式
```r
library(glmnet)
# 交叉验证选 lambda
cv_model <- cv.glmnet(X_train, Y_train, family = "binomial", alpha = 1)
best_lambda <- cv_model$lambda.min

# 最终模型
final_model <- glmnet(X_train, Y_train, family = "binomial", alpha = 1, 
                      lambda = best_lambda)

# 提取非零系数
coef_matrix <- as.matrix(coef(final_model))
non_zero_coefs <- coef_matrix[coef_matrix[, 1] != 0 & 
                                rownames(coef_matrix) != "(Intercept)", , drop = FALSE]
```

### 关键细节
- 训练集/验证集分割先行，避免数据泄露
- `lambda.min` 是最小交叉验证误差，`lambda.1se` 更保守
- 提取的特征用于下游建模（而非直接解释系数）

---

## 7. 混淆矩阵热图

### 意图
直观展示分类结果的混淆情况，同时显示频数和百分比。

### 模式
```r
ggplot(cm_df, aes(x = Actual, y = Predicted)) +
  geom_tile(aes(fill = Freq), color = "white", linewidth = 1) +
  geom_text(aes(label = sprintf("%d\n(%.1f%%)", Freq, Percent)), 
            size = 4, fontface = "bold") +
  scale_fill_gradient(low = "white", high = "steelblue") +
  coord_fixed()
```

### 何时用
- 分类模型性能展示
- ROC 分析中阈值确定后的分类结果
- 训练集 vs 验证集对比

---

## 8. 森林图（AUC/OR/HR 汇总）

### 意图
在一个图中汇总多个指标的效应量和置信区间。

### 模式
```r
ggplot(df, aes(x = estimate, y = reorder(label, estimate))) +
  geom_point(size = 4, color = "steelblue") +
  geom_errorbarh(aes(xmin = lower, xmax = upper), 
                 height = 0.2, color = "steelblue") +
  geom_vline(xintercept = reference, linetype = "dashed", color = "red") +
  labs(x = "AUC (95% CI)", y = "")
```

### 何时用
- 多标志物 AUC 汇总
- 亚组分析结果汇总
- 多因素回归结果可视化

---

## 9. 风险分层 jitter plot

### 意图
展示每个个体的预测概率，按真实结局分组，便于目测模型分离效果。

### 模式
```r
ggplot(df, aes(x = jitter(as.numeric(factor(outcome)), amount = 0.1), 
               y = predicted_prob, color = as.factor(outcome))) +
  geom_jitter(size = 2.5, alpha = 0.7, width = 0.15) +
  geom_hline(yintercept = cutoff, linetype = "dashed", color = "red") +
  scale_color_manual(values = c("steelblue", "coral")) +
  labs(x = "Actual Group", y = "Predicted Probability")
```

### 何时用
- 展示模型预测值的分布
- 验证集上展示分类效果
- 阈值清晰可见

---

## 10. 训练集/验证集分割模式

### 意图
自动从数据中识别训练集和验证集，而不依赖预分割文件。

### 模式
```r
train_set <- df %>% 
  filter(grepl("TRAIN|TRANNING", toupper(.data[[type_col]])))
validation_set <- df %>% 
  filter(grepl("VAL|VALIDATION", toupper(.data[[type_col]])))
```

### 设计思路
- 容错匹配（大小写不敏感，支持缩写）
- 如果数据中没有 TYPE 列，fallback 到随机分割
- 分割信息记录在 README 中

---

## 11. 出版级主题

### 意图
统一所有图表的视觉风格，满足期刊要求。

### 模式
```r
theme_pub <- function(base_size = 14) {
  theme_minimal(base_size = base_size) %+replace%
    theme(
      legend.position = "none",
      plot.title = element_text(hjust = 0.5, size = rel(1.2), face = "bold"),
      axis.title = element_text(size = rel(1), face = "bold"),
      axis.text = element_text(size = rel(1), face = "bold"),
      panel.grid = element_blank(),
      panel.border = element_rect(color = "black", fill = NA, linewidth = 1),
      axis.ticks = element_line(color = "black"),
      strip.background = element_rect(fill = "grey95", color = "black"),
      strip.text = element_text(face = "bold")
    )
}
```

### 保存
```r
# TIFF（LZW 压缩，投稿首选）
ggsave("figure.tiff", p, width = 7, height = 6, dpi = 300, compression = "lzw")

# PNG（预览）
ggsave("figure.png", p, width = 7, height = 6, dpi = 300)

# PDF（矢量，排版）
ggsave("figure.pdf", p, width = 7, height = 6)
```

---

## 12. 拼图模式

### 意图
将多个相关图组合为一个发表级复合图。

### 模式
```r
library(patchwork)
combined <- wrap_plots(plot_list, ncol = 3) +
  plot_annotation(tag_levels = "A") & 
  theme(legend.position = "bottom")
```

### 何时用
- 多个标志物的箱线图需要并列展示
- 主图 + 辅助图组合
- 多 panel 需统一图注
