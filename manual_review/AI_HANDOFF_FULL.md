# 开源硬件商业机会库 V3——完整 AI 接手说明

更新时间：2026-07-26

> 本文是另一个 AI 或自动化代理接手本项目的唯一入口。不要依赖原聊天记录恢复状态；以 GitHub 分支、批次 CSV 和进度账本为准。

## 1. 项目目标

原始数据包含 10,500 条开源硬件、商品页、项目仓库和误抓页面。V2 曾把它们直接包装为“商业机会”，导致大量教程、软件仓库、树莓派/Arduino 拼装 Demo、通用模块、转售元件和玩具项目获得虚假的高商业分，同时部分英雄图错配。

V3 的目标不是保留 10,500 个“机会”，而是：

1. 逐条读取对应原始页面或可信的精确缓存正文；
2. 先判断它究竟是独立产品、专业设备、通用模块、套件、教程还是软件；
3. 再核验客户、痛点、价格、销量/评价/众筹、竞品、拥挤度、制造、售后、合规、IP/许可及英雄图；
4. 同一产品族的规格变体只作为证据，不能虚增为多个独立机会；
5. 最终输出严格候选、观察名单、市场参考、淘汰清单和完整原始库。

## 2. 持久化接手句柄

- Repository：`qqzlqqzlqqzl/qqzlqqzlqqzl`
- Draft PR：`#9`，标题 `rebuild: strict commercial screening V3`
- Working branch：`agent/commercial-v3-strict-rebuild`
- 本接手文档提交前的检查点：`999cc1b89fa583b2cbc8907af0a6e1e2ae650fad`
- 规范：`commercial_v3/REBUILD_SPEC.md`
- 进度账本：`manual_review/PROGRESS.md`
- 存档索引：`manual_review/ARCHIVE_MANIFEST.md`
- 已复核批次：`manual_review/batch_*.csv`
- 延后队列：`manual_review/deferred_unresolved.csv`
- 当前工作队列：`manual_review/queue_next_200.csv`
- 队列生成工作流：`.github/workflows/prepare-v3-review-queue.yml`

PR #9 必须保持 Draft 和未合并，直到用户明确批准最终结果。

## 3. 当前真实进度

以 `manual_review/PROGRESS.md` 为准，当前检查点为：

- Raw records：10,500
- Page/source-reviewed：612
- Strict commercial candidates：0
- Watchlist：27
- Market-reference cases：181
- Rejected：404
- Deferred unresolved：15
- Remaining unreviewed or deferred：9,888

已完成的结构化批次从 `batch_001_...csv` 延伸到 `batch_041b_...csv`。当前共 612 个复核行、612 个唯一 `project_id`。

原来的 ChatGPT 小时调度在交接时已经暂停，避免两个 AI 同时写分支。新接手方应自行建立调度，并确保只有一个写入者。

## 4. 旧版数据来源

V3 队列使用经过翻译和英雄图处理的 10,500 行源 CSV：

- GitHub Actions run ID：`30068281842`
- Artifact name：`full-hero-images-10500-fast`
- Artifact 内路径：`final_output/hardware_opportunities_full_hero_images.csv`

队列工作流通过 `actions/download-artifact@v4` 下载该 Artifact，然后：

1. 收集全部 `manual_review/batch_*.csv` 和 `manual_review/deferred_*.csv` 中的 `project_id`；
2. 从源 CSV 中排除这些 ID；
3. 按源数据顺序选取下一批 200 条；
4. 写入 `manual_review/queue_next_200.csv`；
5. 自动提交回工作分支。

注意：源 CSV 中的旧分类、机器翻译、商业分和英雄图状态都不可信，只能作为定位线索，不能成为 V3 结论。

## 5. V2 已确认问题

必须先读 `commercial_v3/REBUILD_SPEC.md`。关键问题包括：

- 10,500 条抓取记录未经过产品形态硬门槛；
- 5,215 条旧分类为“其他”；
- 4,081 条有自动图片，但部分是树莓派、上游模块、教程图、视频缩略图或错配图片；
- 10,500 条只有约 1,332 种评分理由，其中一段重复 2,264 次；
- 旧“正态化商业评分”只是全库排名映射，不是绝对可行性；
- 机器翻译中存在错译、重复词和无意义文本。

因此禁止：

- 依据旧分排序后直接选高分；
- 依据名称或摘要批量生成商业结论；
- 把自动图片状态当人工英雄图核验；
- 把同一卖家同一产品族的多个尺寸、频段或型号当多个市场空白。

## 6. 产品形态硬门槛

### 允许进一步复核

- 独立成品或接近成品；
- 垂直专业设备；
- 高价值维修替换件；
- 面向明确工业、测试、实验室、农业、无障碍、专业音乐等场景的完整方案。

### 默认淘汰

- 通用模块、HAT、Shield、Breakout、普通开发板；
- 套件和教育拼装，除非有独有课程/IP/机构采购模式；
- 教程、构建指南、工作坊、Demo、示例；
- 软件仓库、网页项目和抓取误分类；
- 树莓派/Arduino 加现成屏幕或传感器的教程拼装；
- 通用低价元件分装和转售品；
- 已被成熟品牌及低价供应链卷烂的红海品类。

“使用树莓派”不是绝对淘汰条件。只有当用户为完整结果付费、板卡被隐藏在完整设备中、产品具备结构/软件/安装/服务闭环时，才允许保留。

## 7. 单条人工复核标准流程

每条记录必须执行以下步骤，未完成不得写成“已复核”：

1. 打开 `original_url`；确认最终 URL、页面标题和页面类型。
2. 阅读产品页、README、规格、文件树、许可、卖家页或项目文档。
3. 判断产品本体：成品、专业模块、通用模块、套件、教程、软件、研究 PoC、维修件或转售品。
4. 写清 `actual_product`，不能照抄营销标题。
5. 写清 `paying_customer` 和 `pain_point`；若无法回答谁付钱以及不买会损失什么，通常不能进入候选。
6. 记录价格、库存、订单、评价、stars/forks、众筹、活跃用户、卖家产品族等市场证据。
7. 搜索或阅读直接竞品，判断 `market_crowding`。有人卖不等于存在空白。
8. 核验 `third_party_dependency`，尤其是树莓派、Arduino、ESP32 开发板、现成显示屏、现成传感器和第三方云服务。
9. 评估 `manufacturing_risk`、`after_sales_risk`、`compliance_risk` 和 IP/许可风险。
10. 核验许可边界：软件许可不自动等于硬件、结构和商标可商业复用。
11. 查看英雄图是否展示准确型号的项目本体。上游板卡、教程步骤、UI 截图、框图、视频缩略图、相似型号图片都不能判为合格主图。
12. 判断是否属于已有 `opportunity_family`；规格变体作为证据保留，但不得虚增独立机会。
13. 写入结构化 CSV，并附 `evidence_urls`。

若精确页面无法读取：

- 不得根据名称猜测；
- 可使用精确 GitHub/GitLab README、原始文件、API、可信缓存或多源交叉核验；
- `review_status` 必须明确写“精确缓存”“交叉核验”等；
- 仍无法确认时移入 `deferred_unresolved.csv`，不评分。

## 8. 不同平台的页面获取方法

### GitHub

优先读取：

- 仓库主页与 README；
- repository tree；
- LICENSE；
- Releases、docs、BOM、Gerber、CAD、firmware；
- 官方产品/众筹链接。

可通过 GitHub API、连接器或 clone 获取。Stars/forks 只能说明开发者关注，不能当销量。

### GitLab

优先读取：

- 项目主页；
- raw README；
- repository tree；
- license；
- releases/tags。

GitLab 页面不可达时，使用精确项目 API 或 raw 文件。若只能得到搜索摘要，移入 deferred，不能给完整结论。

### Tindie 或其他商品页

至少阅读：

- 具体商品页；
- 卖家店铺和产品目录；
- 售价、库存、订单和评价；
- 同店产品族；
- 平台内或外部直接竞品。

卖家总订单是卖家能力证据，不等于该单品销量。低库存也可能只是小批量生产，不能自动当需求旺盛。

### Crowd Supply / Kickstarter / Hackaday / 项目博客

读取目标、规格、交付状态、众筹金额与人数、更新时间、制造资料、许可、评论和失败风险。众筹成功仍需判断是否已被成熟竞品覆盖。

## 9. 建议新增网页证据缓存（现有仓库尚不完整）

现有仓库主要保存结构化结论和证据 URL，并未保存每个网页的完整 HTML。新接手方应补充：

```text
page_cache/
  github.com/<project_id>.json
  gitlab.com/<project_id>.json
  tindie.com/<project_id>.json
  raw_html/<project_id>.html.gz
```

建议 JSON 字段：

```json
{
  "project_id": "...",
  "requested_url": "...",
  "final_url": "...",
  "fetched_at": "ISO-8601",
  "http_status": 200,
  "title": "...",
  "source_type": "direct-page|api|raw-readme|exact-cache|cross-check",
  "extracted_text": "...",
  "price": "...",
  "market_evidence": "...",
  "license": "...",
  "image_urls": ["..."],
  "content_sha256": "..."
}
```

可以并发抓取页面和生成缓存，但最终商业判断必须逐条基于对应正文完成。

## 10. 当前批次 CSV 标准字段

以最近批次 `batch_041b_...csv` 为模板：

```text
project_id
name
original_url
review_status
product_form
opportunity_family
family_business_model
commercialization_mode
actual_product
paying_customer
pain_point
price_usd
market_evidence
market_crowding
third_party_dependency
manufacturing_risk
after_sales_risk
compliance_risk
license_status
hero_image_verdict
final_bucket
verdict_reason
evidence_urls
reviewed_at
```

约束：

- `project_id` 必须唯一；
- `evidence_urls` 使用 `|` 分隔；
- `verdict_reason` 必须针对该项目，不能复制模板；
- `review_status` 必须反映证据类型；
- `final_bucket` 只使用：`严格商业候选`、`观察名单`、`市场参考案例`、`淘汰`；
- 对无法确认页面的记录不使用上述正常分层，移入 deferred。

## 11. 商业评分

只有通过产品形态门槛并且页面证据完整的项目才允许打分。禁止强制正态化。

正向 100 分：

- 痛点强度 15；
- 付费主体 10；
- 产品独立性 12；
- 市场验证 12；
- 差异化 15；
- 竞争空白 12；
- 小团队制造 10；
- 毛利/客单 8；
- 开源资料可复用性 6。

风险扣分：

- 售后/校准 -10；
- 合规/认证/责任 -10；
- 第三方板卡与供应链 -8；
- IP/商标/许可 -10。

参考阈值：

- 硬门槛不通过：直接淘汰；
- 70 及以上：严格候选；
- 55～69：观察名单；
- 55 以下：淘汰或市场参考。

不能只依赖总分，严格候选还必须具备清楚证据、正确英雄图和可执行商业路径。

## 12. 批量执行与速度

用户要求对用户的正式交付批次至少新增 1,000 条，而不是每 5～10 条汇报一次。这不等于可以声称一小时人工阅读 1,000 页。

建议架构：

1. 并行抓取 100～500 个页面，缓存正文；
2. 按平台和产品族分组；
3. 多代理并行逐条阅读，每个代理领取不重叠的 ID 分片；
4. 每个分片输出相同 schema；
5. 中央合并器按 `project_id` 去重并做跨分片产品族去重；
6. 质量代理抽检至少 10% 的淘汰项和 100% 的严格候选/观察名单；
7. 新增满 1,000 条后生成一次 Excel/CSV 交付。

若使用多个 AI，必须使用独立分支或文件分片，禁止同时更新同一个 CSV 或 `PROGRESS.md`。推荐：

```text
agent/review-shard-0001-0250
agent/review-shard-0251-0500
agent/review-shard-0501-0750
agent/review-shard-0751-1000
```

完成后由单一集成代理合并到 `agent/commercial-v3-strict-rebuild`。

## 13. 每批提交规则

每个批次提交应同时包含：

1. 新 `manual_review/batch_XXX_*.csv`；
2. 更新 `manual_review/PROGRESS.md`；
3. 必要时更新 `deferred_unresolved.csv`；
4. 必要时更新产品族索引或证据缓存；
5. 自检结果。

提交后队列工作流会自动刷新 `queue_next_200.csv`，可能产生一个 GitHub Actions bot 提交。推送前先 fetch/rebase，避免覆盖队列更新。

## 14. 每批强制自检

- reviewed rows 数量与唯一 `project_id` 数相同；
- 没有和旧批次重复的 ID；
- deferred 不计入 reviewed；
- totals 满足 `strict + watchlist + market reference + rejected = reviewed`；
- 没有未读页面却标记为普通“已逐页阅读”；
- 没有模板化、跨项目复制的 `verdict_reason`；
- 同产品族变体没有被计作多个商业空白；
- 自动图没有被直接当作人工核验通过；
- 严格候选和观察名单必须有直接竞品和市场证据；
- 产品页、卖家页和证据 URL 可追溯。

## 15. 当前队列的注意事项

`queue_next_200.csv` 按源数据顺序选取，并非按商业潜力排序。当前队列仍会出现大量 GitLab badge 软件、README 徽章项目和误分类软件。这些页面仍需读取或精确核验后明确淘汰，但不要花费与专业候选相同的研究深度。

建议将工作分两层：

- 快速证据核验：确认确为软件/教程/普通模块后结构化淘汰；
- 深度研究：独立成品、专业设备、高价值维修件、明确 B2B 场景。

脚本可以识别明显非硬件候选并安排优先级，但最终状态必须建立在对应页面正文上。

## 16. 接手到同一仓库

```bash
git clone https://github.com/qqzlqqzlqqzl/qqzlqqzlqqzl.git
cd qqzlqqzlqqzl
git fetch origin
git checkout agent/commercial-v3-strict-rebuild
git pull --ff-only origin agent/commercial-v3-strict-rebuild
```

随后依次阅读：

```text
manual_review/AI_HANDOFF_FULL.md
commercial_v3/REBUILD_SPEC.md
manual_review/PROGRESS.md
manual_review/ARCHIVE_MANIFEST.md
manual_review/queue_next_200.csv
manual_review/deferred_unresolved.csv
最近两个 batch CSV
```

## 17. 迁移到另一个仓库

先克隆当前仓库并保留完整提交历史：

```bash
git clone https://github.com/qqzlqqzlqqzl/qqzlqqzlqqzl.git
cd qqzlqqzlqqzl
git checkout agent/commercial-v3-strict-rebuild
git remote rename origin upstream
git remote add origin https://github.com/<NEW_OWNER>/<NEW_REPO>.git
git push -u origin agent/commercial-v3-strict-rebuild
```

在新仓库中需要额外处理：

- 原 Artifact run `30068281842` 属于旧仓库，`actions/download-artifact` 通常不能直接跨仓库复用；
- 应先从旧仓库下载源 CSV，然后上传为新仓库 Release、Artifact 或 Git LFS 文件；
- 修改 `.github/workflows/prepare-v3-review-queue.yml` 的源数据下载步骤；
- 确保新仓库 Actions 有 `contents: write` 权限；
- 修改 PR、分支和文档中的仓库句柄；
- 新建 Draft PR，禁止直接写 main。

最稳妥的迁移方法是：先在旧仓库下载 `full-hero-images-10500-fast`，将其中的 `hardware_opportunities_full_hero_images.csv` 单独放入新仓库的 Release 或对象存储，并记录 SHA-256。

## 18. 给另一个 AI 的可复制启动提示词

```text
你现在接手 GitHub 仓库 qqzlqqzlqqzl/qqzlqqzlqqzl 的开源硬件商业机会 V3 人工复核项目。

工作入口：
- PR #9（Draft，禁止合并）
- branch: agent/commercial-v3-strict-rebuild
- handoff: manual_review/AI_HANDOFF_FULL.md
- policy: commercial_v3/REBUILD_SPEC.md
- progress: manual_review/PROGRESS.md
- queue: manual_review/queue_next_200.csv
- deferred: manual_review/deferred_unresolved.csv

当前进度：10,500 条中 612 条已复核，27 条观察名单，181 条市场参考，404 条淘汰，15 条 deferred，严格候选 0 条。

先读取接手文档、规范、进度和最近两个 batch。收集所有 batch_*.csv 与 deferred_unresolved.csv 中的 project_id 去重。继续处理 queue_next_200.csv；每条必须实际读取原始商品页、项目页、精确 README/API 或可信缓存正文，不得只根据名称、摘要、旧商业分或关键词给结论。

每条核验：产品本体、产品形态、付费客户、痛点、价格和市场证据、竞品与拥挤度、第三方板卡依赖、制造/售后/合规/IP风险、许可、英雄图、产品族归并。教程、软件、树莓派/Arduino 拼装 Demo、通用模块、低价转售和红海项目明确淘汰。无法取得精确证据的放入 deferred，不得猜测。

输出必须使用最近 batch CSV 的字段 schema。新增 batch CSV、PROGRESS.md 和 deferred 必须在同一检查点更新；按 project_id 去重。对用户的正式交付批次至少新增 1,000 条，但不得虚称一小时人工阅读 1,000 页。多代理并行时使用不重叠分片和独立分支，最后由单一集成代理合并。

PR #9 保持 Draft、未合并，直到用户明确批准。
```

## 19. 最终交付要求

全部完成后生成最终 V3 Excel，至少包含：

- `严格候选`；
- `观察名单`；
- `市场参考案例`；
- `淘汰清单`；
- `延后/证据不足`；
- `原始抓取库`；
- `评分说明与字段字典`；
- `进度和质量报告`。

所有商业因素必须拆成独立可筛选列，不再把全部理由塞进一个单元格。最终 Excel 中的英雄图必须是项目本体；无合格图则标记“无合格英雄图”，不能使用相似图片代替。

## 20. 已知未完成事项

- 尚余 9,888 条未复核或 deferred；
- 尚无严格商业候选；
- 尚未对所有外部页面做完整离线快照；
- 尚未生成最终 V3 Excel；
- 当前队列生成逻辑是源顺序，不是商业优先级；
- V3 数值评分尚未系统应用到所有保留项；
- 需要建立统一产品族索引和更强的跨批语义去重；
- 需要对所有观察名单及未来严格候选进行二次独立复核。

这份文档描述的是可恢复的真实项目状态，不代表项目已经接近完成。