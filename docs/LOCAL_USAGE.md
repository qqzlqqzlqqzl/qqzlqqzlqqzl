# 下载、打开和本地使用

本文分成三种场景：只阅读现成数据、用程序处理数据、重新运行爬虫。

## 一、只想下载并阅读现成结果

### 1. 下载

打开正式 Release：

`https://github.com/qqzlqqzlqqzl/qqzlqqzlqqzl/releases/tag/hardware-opportunities-10k-run-11`

推荐下载：

- `open-hardware-commercial-opportunities-10k.zip`：完整包；
- 或单独下载 `开源硬件商业化机会库_10000条.xlsx`。

下载 ZIP 后先完整解压，不要直接在压缩包预览器里编辑 Excel。

### 2. 打开 Excel

可使用：

- Microsoft Excel；
- WPS 表格；
- LibreOffice Calc。

优先使用桌面版 Microsoft Excel。表内缩略图使用 `IMAGE()` 公式，旧版本 Excel、部分 WPS 或 LibreOffice 可能不显示图片，但文本、评分、筛选器和原始链接仍可正常使用。

### 3. 推荐阅读顺序

1. 打开“摘要”工作表，确认项目总数、平台分布和类别分布；
2. 打开“来源状态”，查看哪些平台成功、失败或返回零结果；
3. 打开“评分方法”，理解分数只用于初筛；
4. 打开“项目机会库”开始筛选。

### 4. 推荐筛选方式

第一轮可按以下条件筛选：

- `正态化商业评分 >= 8`；
- `数据质量 = A`；
- 选择目标类别；
- `量产难度 <= 6`；
- `售后风险 <= 6`；
- `合规风险 <= 6`。

风险和难度列是“数值越低越容易处理”，评分列是“数值越高越值得优先看”。

第二轮逐项查看：

- 名称和描述是否与目标产品方向真正相关；
- 原始链接是否仍可访问；
- 是否存在原理图、PCB、BOM、Gerber、固件、外壳文件；
- 硬件与软件许可证是否允许目标用途；
- 是否已有明显竞品或商业化验证；
- 产品认证、安全和售后是否可承受。

不要仅凭高分决定量产。高分只是“优先打开原始链接”的排序信号。

## 二、用 CSV 或 JSONL 做二次分析

### CSV

`hardware_opportunities.csv` 为 UTF-8 with BOM，可直接用 Excel 打开，也适合 Power BI、Python、R、数据库导入。

使用 Python 标准库读取：

```python
import csv

with open("output_v2/hardware_opportunities.csv", encoding="utf-8-sig", newline="") as file:
    rows = list(csv.DictReader(file))

high_score = [
    row for row in rows
    if float(row["normalized_commercial_score"]) >= 8
]
print(len(high_score))
```

### JSONL

`hardware_opportunities.jsonl` 每一行都是一个独立 JSON 对象，适合流式处理：

```python
import json

with open("output_v2/hardware_opportunities.jsonl", encoding="utf-8") as file:
    for line in file:
        record = json.loads(line)
        if record["category"] == "电子礼物/徽章/挂件":
            print(record["name"], record["url"])
```

### 关键文件的区别

- `summary.json`：整次运行统计；
- `source_status.csv`：来源是否成功，不是项目数据；
- `score_distribution.csv`：各分数区间统计；
- `progress.json`：最后心跳和运行警告；
- `hardware_opportunities.*`：真正的项目明细。

## 三、把仓库下载到本地

### 方式 A：Git Clone

```bash
git clone https://github.com/qqzlqqzlqqzl/qqzlqqzlqqzl.git
cd qqzlqqzlqqzl
```

### 方式 B：Download ZIP

在仓库主页点击 **Code → Download ZIP**，解压后进入仓库根目录。

Git Clone 更适合后续更新；Download ZIP 适合只运行一次。

## 四、本地运行环境

推荐：

- Python 3.12；
- 稳定互联网连接；
- 至少数百 MB 可用磁盘空间；
- 可访问 GitHub、GitLab 和各公开硬件站点；
- GitHub Token，强烈建议配置，以降低公开 API 限流影响。

依赖由 `crawler/requirements.txt` 固定：

- Beautiful Soup；
- Requests；
- urllib3；
- python-dateutil；
- XlsxWriter。

### GitHub Token

爬虫没有 Token 也能访问 GitHub 公共 API，但限流更严格。建议使用只需要读取公开仓库的 Token。

Windows PowerShell：

```powershell
$env:GITHUB_TOKEN = "你的Token"
```

Linux / macOS：

```bash
export GITHUB_TOKEN="你的Token"
```

不要把 Token 写进代码、README、提交记录或公开日志。

## 五、Windows 本地复现

在 PowerShell 中进入仓库根目录：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r crawler\requirements.txt
python crawler\v2.py --target 10500 --out output_v2
```

如 PowerShell 禁止激活脚本，可在当前窗口临时执行：

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
```

也可以不激活虚拟环境，直接使用：

```powershell
.\.venv\Scripts\python.exe -m pip install -r crawler\requirements.txt
.\.venv\Scripts\python.exe crawler\v2.py --target 10500 --out output_v2
```

## 六、Linux / macOS 本地复现

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r crawler/requirements.txt
python crawler/v2.py --target 10500 --out output_v2
```

## 七、参数说明

```text
--target  最终希望选取的去重记录数，正式运行建议 10500
--out     输出目录，默认 output_v2
```

本地测试可先运行较小目标：

```bash
python crawler/v2.py --target 500 --out output_test
```

注意：V2 的正式质量门槛仍检查最终记录不少于 10,000、平台不少于 25、前四平台占比不高于 72%。因此小目标测试可能以非零退出码结束，即使已经生成部分文件。这属于预期行为。

## 八、本地运行和 GitHub Actions 的区别

直接运行：

```bash
python crawler/v2.py ...
```

会生成数据文件，但不会：

- 写入 `progress` 分支；
- 上传 Actions Artifact；
- 创建 GitHub Release；
-提供每分钟持久化心跳。

GitHub Actions 使用：

```bash
python -u crawler/v2_progress_git.py ...
```

它依赖 Ubuntu 的 `SIGALRM` 和 GitHub 环境变量。Windows 本地请使用 `v2.py`，不要直接运行 `v2_progress_git.py`。

## 九、运行完成后怎样验收

至少检查：

1. `summary.json` 中 `records >= 10000`；
2. `platforms >= 25`；
3. `top4_platform_share <= 0.72`；
4. `hardware_opportunities.csv` 行数与 `records` 一致；
5. `project_id` 无重复；
6. URL 无重复；
7. Excel 可以打开并包含四个工作表；
8. `source_status.csv` 中失败来源有明确记录；
9. 输出目录中包含评分方法和分布文件。

详细复现和校验命令见 `docs/REPRODUCIBILITY.md`。

## 十、常见问题

### GitHub API 403 / rate limit

- 确认 `GITHUB_TOKEN` 已配置；
- 不要并行启动多个完整爬虫；
- 等待限流窗口恢复后再运行；
- 检查 Token 是否仍有效。

### 某个平台返回零结果

网站结构、Sitemap、反爬策略或网络可能已经变化。查看 `source_status.csv` 和控制台日志，不要因为一个来源失败就删除整批结果。

### Excel 图片不显示

通常是软件不支持 `IMAGE()`、未联网加载图片或图片源失效。使用原始链接和 `thumbnail_url` 列仍可查看项目。

### 输出不到 10,000 条

检查：

- GitHub Token 和网络；
- 失败来源数量；
- GitHub/GitLab 是否被限流；
- 网站结构是否变化；
- 去重后候选是否足够。

### 重复运行会得到完全相同结果吗

不会保证完全相同。公开页面、项目更新时间、API 排序、站点可访问性和去重候选都会变化。复现目标是相同方法和质量门槛，而不是逐字节相同数据集。
