# 开源硬件商业化机会库

从公开网页、公开 API 和公开项目目录采集近五年活跃的开源硬件项目，生成可检索的商业化初筛数据。该仓库同时保存抓取程序、评分规则、GitHub Actions 工作流、运行交接说明和数据字典。

## Windows：下载后双击运行

Windows 用户不需要手工创建虚拟环境或输入 `pip` 命令：

1. 点击 GitHub 的 **Code → Download ZIP**；
2. 完整解压；
3. 双击根目录的 `RUN_WINDOWS.bat`；
4. 按提示输入目标条数，正式运行使用 `10500`；
5. 程序会自动检查或安装 Python、创建环境、安装依赖、抓取、验收并打开结果目录。

已有结果需要检查时，双击 `CHECK_RESULT_WINDOWS.bat`。

详细图文式说明和故障处理见 [WINDOWS使用说明.md](WINDOWS使用说明.md)。

## 当前正式成果

GitHub Actions Run #11 已于 2026-07-23 成功完成：

| 指标 | 结果 |
|---|---:|
| 抓取前原始记录 | 13,540 |
| 去重候选 | 12,869 |
| 最终入库 | 10,500 |
| 有效平台 | 34 |
| 前四平台合计占比 | 48.19% |
| 8 分及以上项目 | 386 |
| 正态化评分均值 / 标准差 | 5.40 / 1.45 |

永久成果：

- [下载 Release：开源硬件商业化机会库 10k · Run 11](https://github.com/qqzlqqzlqqzl/qqzlqqzlqqzl/releases/tag/hardware-opportunities-10k-run-11)
- [查看 GitHub Actions Run #11](https://github.com/qqzlqqzlqqzl/qqzlqqzlqqzl/actions/runs/30010928798)

## 下载后怎么打开

1. 在 Release 页面下载 `open-hardware-commercial-opportunities-10k.zip`，然后完整解压。
2. 普通阅读优先打开 `output_v2/开源硬件商业化机会库_10000条.xlsx`。
3. 使用 Microsoft Excel、WPS 表格或 LibreOffice Calc 打开。
4. 先看“摘要”工作表，再进入“项目机会库”。
5. 在“项目机会库”中建议先筛选：
   - `正态化商业评分 >= 8`；
   - 目标类别，例如“电子礼物/徽章/挂件”“测试测量/工程工具”；
   - `数据质量 = A`；
   - 可接受的量产难度、售后风险和合规风险。
6. 点击“原始链接”进入项目页面，逐项复核许可证、BOM、Gerber、固件、图片权利、专利、商标和真实市场需求。

更详细的操作说明见 [docs/LOCAL_USAGE.md](docs/LOCAL_USAGE.md)。

## 输出文件怎么选

| 文件 | 适合用途 |
|---|---|
| `开源硬件商业化机会库_10000条.xlsx` | 人工浏览、筛选、排序、查看摘要和来源状态 |
| `hardware_opportunities.csv` | Excel、Power BI、Python、数据库导入 |
| `hardware_opportunities.jsonl` | 程序处理、向量化、LLM/数据管道逐行读取 |
| `source_status.csv` | 检查各平台抓取成功、失败、耗时和条数 |
| `score_distribution.csv` | 查看 0–10 分各区间分布 |
| `summary.json` | 自动化读取本次运行的核心统计和质量门槛 |
| `SCORING_METHOD.md` | 查看评分方法和限制 |
| `progress.json` | 查看最后运行阶段、警告和来源进度 |

完整字段解释见 [docs/DATA_DICTIONARY.md](docs/DATA_DICTIONARY.md)。

## 最快复现方式：GitHub Actions

1. 打开仓库的 **Actions** 页面。
2. 选择 **Crawl 10k balanced hardware opportunities**。
3. 点击 **Run workflow**。
4. `target` 默认是 `10500`；测试时可改成较小数字，但质量门槛仍要求正式运行至少 10,000 条。
5. `publish_release=true` 时，成功运行会发布永久 Release；关闭后只保留 90 天的 Actions Artifact。
6. 运行过程中可查看 Actions 日志；`progress` 分支中的 `progress/live.json` 保存最近一次心跳状态。

整库工作流只允许手动触发，避免普通代码或文档合并意外启动一次长时间抓取。

## 本地运行

### Windows 推荐方式

直接双击：

```text
RUN_WINDOWS.bat
```

它会自动完成 Python 检查、虚拟环境、依赖、运行和验收。命令行也可使用：

```bat
RUN_WINDOWS.bat -Target 10500 -Output output_v2
```

### Linux / macOS

推荐 Python 3.12，在仓库根目录执行：

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r crawler/requirements.txt
python crawler/v2.py --target 10500 --out output_v2
```

本地直接运行 `v2.py` 不会写入 GitHub 的 `progress` 分支，也不会自动创建 Release。完整的环境、参数、网络要求、故障处理和结果校验见 [docs/LOCAL_USAGE.md](docs/LOCAL_USAGE.md) 与 [docs/REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md)。

## 仓库结构

```text
.
├─ RUN_WINDOWS.bat             # Windows 双击运行入口
├─ CHECK_RESULT_WINDOWS.bat    # Windows 双击验收入口
├─ WINDOWS使用说明.md          # Windows 完整说明
├─ windows/
│  ├─ run.ps1                  # 自动安装环境并运行
│  └─ check_result.ps1         # 自动验收并打开结果
├─ crawler/
│  ├─ main.py                  # 基础采集器、数据模型、导出与评分辅助
│  ├─ v2.py                    # 10k 多平台平衡采集和质量门槛
│  ├─ v2_progress.py           # 运行进度、心跳和来源状态
│  ├─ v2_progress_git.py       # GitHub Actions 持久化进度与硬超时入口
│  └─ requirements.txt
├─ scripts/validate_output.py  # 交付结果自动验收
├─ tests/                      # 轻量单元测试
├─ docs/
│  ├─ LOCAL_USAGE.md           # 下载、打开、本地运行和排障
│  ├─ REPRODUCIBILITY.md       # 复现流程和验收标准
│  └─ DATA_DICTIONARY.md       # 字段字典
├─ HANDOFF.md                  # 当前状态、设计决策、已知问题和后续维护
└─ .github/workflows/
   ├─ crawl-hardware-10k.yml   # 手动整库抓取
   └─ validate-crawler.yml     # Linux 与 Windows 入口验证
```

## 分支说明

- `main`：唯一产品代码和文档主线。
- `progress`：运行状态分支，只保存 `progress/live.json` 心跳；**不要合并进 main**。
- 临时功能分支：通过 PR 合并后即可删除。

## 评分应怎样理解

每条记录先依据自身元数据计算确定性规则原始分，因素包括类别、平台、支持量、时间、图片、描述、许可证线索、开源完整度、商业关键词、量产难度、售后风险和合规风险。随后按全库原始分排序，映射为近似正态分布的 0–10 分。

这是一套大范围初筛工具，不是人工逐条商业尽调。高分表示“值得优先打开原始链接复核”，不表示项目可以直接复制、生产或销售。

## 已知数据限制

- 最终 10,500 条记录的 `project_id` 和 URL 均已去重。
- 337 条记录没有抓到正文描述，但仍保留原始链接和其他可用元数据。
- 5,215 条记录目前归类为“其他”，精细研究时需要二次分类。
- 页面可公开访问不等于设计文件允许商用。
- 网站结构、API、限流和网络状态变化会导致不同日期运行结果不完全一致。

## 合规边界

- 只访问公开页面和公开 API。
- 不绕过登录、验证码、付费墙或访问控制。
- 使用有限并发、请求超时、重试退避和来源状态记录。
- 开发产品前必须逐项核验许可证、专利、商标、图片、字体、认证、产品安全和目标市场法规。

## 维护入口

首次接手本项目请先阅读 [HANDOFF.md](HANDOFF.md)。任何评分、来源或字段变更，都应同步更新数据字典、复现说明和评分说明，并通过 `Validate crawler` 工作流后再合并。
