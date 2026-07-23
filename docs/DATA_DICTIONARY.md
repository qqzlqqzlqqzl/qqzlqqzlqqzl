# 数据字典

本文解释 `hardware_opportunities.csv` 和 `hardware_opportunities.jsonl` 的字段。CSV 使用 UTF-8 with BOM；JSONL 每行一个 UTF-8 JSON 对象。

## 项目标识与来源

| 字段 | 类型 | 说明 |
|---|---|---|
| `project_id` | string | 由平台和规范化 URL 稳定生成的短 SHA-1 标识。用于本数据集内部去重和关联，不是来源平台官方 ID。 |
| `name` | string | 项目名称。优先来自 API 或页面标题；缺失时由 URL slug 推导。 |
| `platform` | string | 项目被采集的平台或来源名称，例如 GitHub、GitLab、OSHWA认证目录。 |
| `url` | string | 规范化后的原始项目页面链接。商业复核必须回到该链接。 |
| `source_domain` | string | URL 的域名，用于来源检查和域名级分析。 |
| `crawl_time` | ISO-8601 string | 本次记录生成时间，通常为 UTC。它不是项目发布时间。 |

## 图片与时间

| 字段 | 类型 | 说明 |
|---|---|---|
| `thumbnail_url` | string | 项目图、Open Graph 图片、平台图标或项目卡图片地址。图片权利必须单独核验。 |
| `thumbnail_type` | enum string | 常见值：`产品图`、`项目图`、`项目卡`、`平台图`、`缺失`。表示图片来源质量，不代表版权状态。 |
| `published_date` | `YYYY-MM-DD` 或空 | 项目创建、发布或页面声明的发布时间。不同平台语义可能不同。 |
| `updated_date` | `YYYY-MM-DD` 或空 | 最近更新、推送或活动日期。不同平台语义可能不同。 |

## 内容与分类

| 字段 | 类型 | 说明 |
|---|---|---|
| `description` | string | API 或页面元数据中的项目描述。部分页面抓取不到正文时为空。 |
| `keywords` | string | 平台 topics、标签、meta keywords 或采集器补充的关键词。 |
| `category` | enum string | 基于名称、描述和关键词的自动规则分类。`其他`表示现有规则没有可靠命中，不表示没有商业价值。 |

当前分类包括：

- 电子礼物/徽章/挂件；
- 键盘/宏键盘/控制器；
- 音频/音乐设备；
- 测试测量/工程工具；
- 传感器/环境监测；
- 智能家居/物联网；
- 机器人/机电；
- 可穿戴/健康；
- 游戏/娱乐；
- 教育套件/创客；
- 农业/园艺；
- 能源/电源；
- 制造设备/桌面机器；
- 科研/实验室仪器；
- 网络/通信设备；
- 其他。

## 开源和市场证据

| 字段 | 类型 | 说明 |
|---|---|---|
| `stars_or_support` | number | GitHub/GitLab stars、众筹支持量或平台可获得的支持信号。跨平台不能直接等同比较。 |
| `hardware_license` | string | 硬件许可证线索。`待核验`、`页面待核验`或`未说明`不构成授权。 |
| `software_license` | string | 软件许可证线索，可能来自 API SPDX ID 或页面信息。仍需检查仓库实际 LICENSE 和文件级声明。 |
| `open_source_completeness` | string | 对原理图、PCB、BOM、Gerber、固件、外壳等公开完整度的自动说明或线索。 |
| `market_validation` | string | stars、forks、众筹、商品目录、认证目录或项目平台收录等市场/成熟度线索。 |

## 自动商业分析字段

下列字段由类别模板和规则自动生成，用于初筛，不是人工研究结论。

| 字段 | 类型 | 说明 |
|---|---|---|
| `typical_competitors` | string | 该类别常见竞品和替代方案，不一定是该项目的直接竞品。 |
| `commercial_value` | string | 该类别可能存在的商业价值。 |
| `improvement_direction` | string | 适合小团队差异化的通用改进建议。 |
| `target_customer` | string | 该类别可能的目标客户。 |
| `suggested_price_low_cny` | integer | 类别级建议售价下限，人民币，仅用于早期定位。 |
| `suggested_price_high_cny` | integer | 类别级建议售价上限，人民币，仅用于早期定位。 |

## 难度、风险和评分

| 字段 | 类型 | 方向 | 说明 |
|---|---|---|---|
| `manufacturing_difficulty` | float 0–10 | 越低越容易 | 量产、结构、供应链、测试和装配的规则化难度。 |
| `after_sales_risk` | float 0–10 | 越低越好 | 兼容、固件、校准、易损件和使用复杂度带来的售后风险。 |
| `compliance_risk` | float 0–10 | 越低越好 | 无线、电池、电气安全、医疗宣称等法规和认证风险。 |
| `raw_commercial_score` | float 0–10 | 越高越优先 | 每条记录基于自身证据计算的确定性规则原始分。 |
| `normalized_commercial_score` | float 0–10 | 越高越优先 | 按全库原始分排序后映射到近似正态分布的相对优先级。 |
| `score_reason` | string | — | 各评分分量、逐条证据、机会和主要约束的可读解释。 |

### 原始分权重

V2 原始分大致由以下部分组成：

- 需求：20%；
- 市场验证：15%；
- 成熟度：15%；
- 可量产：15%；
- 差异化：10%；
- 传播：10%；
- 风险友好：10%；
- 能力匹配：5%。

`normalized_commercial_score` 是全库相对排序分。如果候选集合发生变化，同一个项目的正态化分可能改变，即使原始分未变。

## 数据质量与审核状态

| 字段 | 类型 | 说明 |
|---|---|---|
| `data_quality` | enum `A/B/C` | 自动证据完整度等级。A 通常拥有更多描述、图片、日期、许可或市场线索；它不是内容真实性保证。 |
| `review_status` | string | 当前记录的处理状态。V2 常见值为`V2逐条规则评分（非人工尽调）`。 |

## Excel 与 CSV 的差异

Excel 的“项目机会库”为了阅读体验，列名使用中文，并增加可视化缩略图列、条件格式、超链接和冻结窗格。CSV/JSONL 使用上表中的英文字段名，便于程序处理。

Excel 中主要映射：

| Excel 列 | CSV/JSONL 字段 |
|---|---|
| 项目ID | `project_id` |
| 名称 | `name` |
| 平台 | `platform` |
| 原始链接 | `url` |
| 类别 | `category` |
| 正态化商业评分 | `normalized_commercial_score` |
| 原始商业评分 | `raw_commercial_score` |
| 数据质量 | `data_quality` |
| 审核状态 | `review_status` |

## 使用注意

1. `A` 级数据不代表许可证安全；
2. `待核验`不等于允许商用；
3. 类别级竞品、售价和客户描述不能代替单项目市场研究；
4. 正态化高分是相对优先级，不是成功概率；
5. 所有计划量产的项目都必须重新打开原始链接并进行法律、技术、供应链和市场核验。
