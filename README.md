# 开源硬件商业化机会库爬虫

此仓库用于从公开网页、公开 API 和公开项目目录中采集近五年活跃的开源硬件项目，并生成商业化初筛数据。

## V2 正式交付

GitHub Actions Run #11 已于 2026-07-23 成功完成：

- 抓取前原始记录：13,540 条
- 去重候选：12,869 条
- 最终入库：10,500 条
- 有效平台：34 个
- 前四平台合计占比：48.19%（质量门槛不高于 72%）
- 正态化评分均值 / 标准差：5.40 / 1.45
- 8 分及以上项目：386 条

永久交付页：

- [开源硬件商业化机会库 10k · Run 11](https://github.com/qqzlqqzlqqzl/qqzlqqzlqqzl/releases/tag/hardware-opportunities-10k-run-11)
- [GitHub Actions Run #11](https://github.com/qqzlqqzlqqzl/qqzlqqzlqqzl/actions/runs/30010928798)

## 输出文件

Release 和 Actions Artifact `open-hardware-commercial-opportunities-10k` 包含：

- `开源硬件商业化机会库_10000条.xlsx`
- `hardware_opportunities.csv`
- `hardware_opportunities.jsonl`
- `source_status.csv`
- `score_distribution.csv`
- `summary.json`
- `SCORING_METHOD.md`
- `progress.json`
- 完整 ZIP 包

Excel 工作簿包含“项目机会库”“摘要”“来源状态”“评分方法”四个工作表。

## 字段与评分

每条记录保留项目 ID、名称、平台、原始链接、缩略图来源、日期、描述、关键词、类别、支持量、许可证线索、开源完整度、市场验证、典型竞品、商业价值、改进方向、目标客户、建议价格、量产难度、售后风险、合规风险和 0–10 分评分。

原始分由脚本依据每行自身证据进行确定性规则评分，再按全库排序映射为近似正态分布的正态化分数。该评分用于大范围初筛，不是人工逐条商业尽调。

## 质量说明

- 最终 10,500 条记录的项目 ID 和 URL 均已去重。
- 337 条记录未抓到正文描述，但仍保留原始链接与其他可用元数据。
- 5,215 条记录目前归类为“其他”，后续精细筛选时应结合原始页面复核。
- 高分项目仍需逐项核验真实销量、BOM、成本、许可证、专利、商标、图片、字体、认证和安全合规。

## 合规边界

- 只访问公开页面和公开 API。
- 不绕过登录、验证码、付费墙或访问控制。
- 使用有限并发、重试退避与来源状态记录。
- 公开可访问不等于允许商用；每个候选项目仍需逐项核验许可证、专利、商标、图片、字体与安全合规。
