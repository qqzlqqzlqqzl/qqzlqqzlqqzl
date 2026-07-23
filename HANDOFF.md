# 项目交接说明（HANDOFF）

最后更新：2026-07-23

## 1. 项目目标

本项目建立一个大规模开源硬件商业化机会库，用于发现值得进一步人工研究的项目，而不是直接给出“可复制生产”的结论。

正式目标：

- 最终不少于 10,000 条去重记录；
- 至少覆盖 25 个有效平台；
- 前四大平台合计不超过最终语料的 72%；
- 每条记录保留来源链接和评分理由；
- 输出 Excel、CSV、JSONL、来源状态、评分分布和摘要；
- 所有正式结果通过 GitHub Actions Artifact 和 Release 交付。

## 2. 当前完成状态

正式运行：GitHub Actions Run #11

- 状态：成功；
- 原始抓取记录：13,540；
- 去重候选：12,869；
- 最终入库：10,500；
- 有效平台：34；
- 前四平台占比：48.1905%；
- 8 分及以上：386；
- 评分均值 / 标准差：5.3995 / 1.4477；
- Artifact SHA-256：`f8816afd891b757a43ce12a7d8a4535b964d2d51cab263127c068df55ef48ac8`。

正式 Release：

`https://github.com/qqzlqqzlqqzl/qqzlqqzlqqzl/releases/tag/hardware-opportunities-10k-run-11`

正式 Actions 运行：

`https://github.com/qqzlqqzlqqzl/qqzlqqzlqqzl/actions/runs/30010928798`

## 3. 已交付文件

Release/Artifact 中应包含：

- `output_v2/开源硬件商业化机会库_10000条.xlsx`
- `output_v2/hardware_opportunities.csv`
- `output_v2/hardware_opportunities.jsonl`
- `output_v2/source_status.csv`
- `output_v2/score_distribution.csv`
- `output_v2/summary.json`
- `output_v2/SCORING_METHOD.md`
- `output_v2/progress.json`
- `open-hardware-commercial-opportunities-10k.zip`

Excel 应包含四个工作表：

1. 项目机会库；
2. 摘要；
3. 来源状态；
4. 评分方法。

## 4. 代码结构和数据流

### `crawler/main.py`

基础层，负责：

- `Record` 数据模型；
- URL 规范化、日期解析、分类和商业字段补全；
- OSHWA、Hack Club、GitHub、GitLab 和网页来源基础采集；
- 去重、分数正态化；
- CSV 和 Excel 导出。

### `crawler/v2.py`

V2 主流程，负责：

- 扩展平台来源；
- Sitemap/列表页快速发现；
- 每行确定性证据评分；
- 按平台配额进行平衡选取；
- 输出 10k 数据集；
- 执行质量门槛：记录数、平台数和前四平台集中度。

### `crawler/v2_progress.py`

可观测运行层，负责：

- 每分钟心跳；
- 当前来源、阶段耗时、候选数、详情页数和警告；
- `progress.json` 检查点；
- 单来源超时包装。

### `crawler/v2_progress_git.py`

GitHub Actions 入口，负责：

- 将心跳持久化到 `progress` 分支的 `progress/live.json`；
- 安装不会被嵌套 `except Exception` 吞掉的硬超时边界；
- 启动 `v2_progress.main()`。

### GitHub Actions

- `validate-crawler.yml`：普通 PR/推送时执行编译和单元测试，不联网抓取整库。
- `crawl-hardware-10k.yml`：仅允许手动触发，运行完整抓取、上传 Artifact，并可选发布 Release。

## 5. 分支约定

### `main`

产品代码和文档唯一主线。正式修复和文档都必须通过 PR 合入。

### `progress`

运行状态分支，只保存 `progress/live.json`。它相当于实时状态存储，不是开发分支，因此：

- 不要合并到 `main`；
- 不要在其中开发代码；
- 可以保留，供下一次 Actions 运行覆盖心跳；
- 如人工删除，GitHub 持久化入口需要先重新创建该分支。

### 临时功能分支

PR 合并后删除即可。不要长期维护第二条代码主线。

## 6. Run #11 中发现并处理的问题

### 单来源硬超时曾失效

OpenBuilds 实际耗时约 917.9 秒，超过文档声明的 12 分钟。根因是原信号处理器抛出 `TimeoutError`，而 `parse_detail()` 等函数包含宽泛的 `except Exception`，可能吞掉该异常。

修复方式：

- 信号处理器抛出继承自 `BaseException` 的 `SourceHardTimeout`；
- 它可穿过普通 `except Exception`；
- 到来源边界后转换为 `RuntimeError`；
- V2 将该来源记为失败并继续后续来源，而不是终止整库。

对应单元测试位于 `tests/test_timeout_boundary.py`。

### 整库工作流不应随普通合并自动运行

完整抓取会访问大量公开页面并运行较长时间，因此已改为 `workflow_dispatch` 手动触发。普通代码变更只运行轻量验证工作流。

## 7. 当前数据限制

- 337 条最终记录没有正文描述；
- 5,215 条记录被归为“其他”；
- 自动分类依赖标题、描述和关键词，不能代替人工分类；
- `hardware_license`、`software_license` 和 `open_source_completeness` 中的“待核验”不能视为授权；
- 支持量、发布时间和页面结构可能随时间变化；
- 各网站的限流、连接状态和 Sitemap 结构会影响复现结果；
- 评分是相对优先级，不代表销量预测、利润预测或法律意见。

## 8. 接手后的标准操作

### 只想阅读成果

按照 `docs/LOCAL_USAGE.md` 下载 Release，打开 Excel，并使用筛选器从高分和目标类别开始阅读。

### 修改采集器或评分逻辑

1. 从最新 `main` 创建功能分支；
2. 修改代码；
3. 同步修改测试和相关文档；
4. 提交 PR；
5. 确认 `Validate crawler` 通过；
6. 合并 PR；
7. 只有确实需要刷新数据时，才手动执行完整 10k 工作流。

### 发布新数据版本

1. Actions → `Crawl 10k balanced hardware opportunities`；
2. `target=10500` 或更高；
3. `publish_release=true`；
4. 运行完成后检查 `summary.json`；
5. 验证记录数 ≥ 10,000、平台数 ≥ 25、前四平台占比 ≤ 0.72；
6. 下载 Artifact 做文件级校验；
7. 在 README 和本文件更新正式版本链接和统计。

## 9. 推荐后续改进顺序

1. 对“其他”类别进行二次分类，优先处理高分记录；
2. 对 8 分以上的 386 条项目进行人工商业尽调；
3. 补充许可证解析和文件完整度检测；
4. 为失败或零结果平台更新采集规则；
5. 将平台和分类规则移出代码，改成可维护配置；
6. 增加增量抓取和历史版本差异，而不是每次全量重抓；
7. 对评分做人工标注校准，避免只依赖规则权重。

## 10. 完成判定

本轮“构建 10k 开源硬件商业化机会库”已经完成。后续工作属于数据精炼、人工尽调或新版本迭代，不是本轮交付缺口。
