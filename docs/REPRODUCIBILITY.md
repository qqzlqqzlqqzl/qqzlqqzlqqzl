# 复现与验收

本文说明怎样复现方法、怎样运行新版本，以及怎样验证输出是否达到交付标准。

## 1. “复现”分成两种

### 方法复现

使用相同代码、依赖、来源规则、评分方法和质量门槛重新抓取。由于公开网站内容会变化，最终项目列表不要求逐字节相同。

### Run #11 成果复核

下载已经发布的固定 Release，对现有 10,500 条结果做文件完整性、行数、去重、平台集中度和 Excel 结构校验。这可以得到稳定结果。

## 2. 固定成果信息

- Release tag：`hardware-opportunities-10k-run-11`
- Actions run：`30010928798`
- 运行代码提交：`d179000f6d63d8df6af5f088e696c684a2ca470b`
- Artifact ID：`8566705160`
- Artifact SHA-256：`f8816afd891b757a43ce12a7d8a4535b964d2d51cab263127c068df55ef48ac8`
- 生成时间：2026-07-23 UTC
- 数据时间下限：2021-01-01

Run #11 的基准统计：

```json
{
  "candidate_records_before_dedupe": 13540,
  "deduplicated_candidates": 12869,
  "records": 10500,
  "platforms": 34,
  "top4_platform_share": 0.481905,
  "score_mean": 5.399455238095238,
  "score_stdev": 1.4476878407263245,
  "gte_8": 386
}
```

## 3. 复核已发布成果

### 下载

从 Release 下载完整 ZIP 并解压，确保得到 `output_v2` 目录。

### 使用仓库验收脚本

在仓库根目录执行：

```bash
python scripts/validate_output.py /path/to/output_v2
```

Windows 示例：

```powershell
python scripts\validate_output.py "D:\Downloads\open-hardware\output_v2"
```

脚本检查：

- 必要文件是否齐全；
- CSV 必要字段；
- 最终记录是否至少 10,000 条；
- 有效平台是否至少 25 个；
- 前四平台占比是否不高于 72%；
- `project_id` 和 URL 是否重复或为空；
- 原始分与正态化分是否处于 0–10；
- `summary.json` 是否与 CSV 一致；
- Excel 是否可作为 ZIP/XML 读取；
- Excel 是否包含四个必要工作表。

成功时退出码为 0 并打印：

```text
VALIDATION PASSED
```

## 4. 固定旧版本代码

只研究 Run #11 当时的代码：

```bash
git clone https://github.com/qqzlqqzlqqzl/qqzlqqzlqqzl.git
cd qqzlqqzlqqzl
git checkout d179000f6d63d8df6af5f088e696c684a2ca470b
```

也可以检出 Release tag：

```bash
git checkout tags/hardware-opportunities-10k-run-11
```

注意：旧提交保留了当时的行为，包括后来发现的硬超时问题。新运行应使用最新 `main`。

## 5. 使用最新代码重新运行

### 安装

```bash
git checkout main
git pull
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r crawler/requirements.txt
```

Windows 使用：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r crawler\requirements.txt
```

### Token

建议设置 `GITHUB_TOKEN`，否则 GitHub 公共搜索 API 更容易限流。

### 运行

```bash
python crawler/v2.py --target 10500 --out output_v2
```

完成后：

```bash
python scripts/validate_output.py output_v2
```

## 6. 使用 GitHub Actions 复现

1. 打开 Actions；
2. 选择 `Crawl 10k balanced hardware opportunities`；
3. 点击 `Run workflow`；
4. 选择 `main`；
5. `target` 填 `10500`；
6. 需要永久交付时保持 `publish_release=true`；
7. 启动。

工作流会：

1. 使用 Ubuntu 24.04 和 Python 3.12；
2. 安装固定版本依赖；
3. 执行带心跳和硬超时的 V2；
4. 打包全部输出；
5. 无论成功失败都上传可获得的 Artifact/诊断文件；
6. 成功且允许发布时创建 Release；
7. 未通过质量门槛时将工作流标记为失败。

`progress` 分支的 `progress/live.json` 是运行时状态通道，不需要合并到 `main`。

## 7. 正式质量门槛

代码层质量门槛：

- `records >= 10000`；
- `platforms >= 25`；
- `top4_platform_share <= 0.72`。

交付层还应检查：

- CSV、JSONL 和 Excel 数量一致；
- ID、URL 无重复；
- 所有输出文件存在；
- Excel 四个工作表存在；
- `source_status.csv` 可解释失败来源；
- `score_reason`、原始链接和审核状态字段存在；
- Release 附件可下载。

## 8. 哪些部分是确定性的

对同一批输入记录：

- URL 规范化；
- `project_id` 生成；
- 分类规则；
- 原始商业评分；
- 平台配额和平衡选择；
- 排名后的正态化映射；
- CSV/JSONL 字段结构；
- 质量门槛判断。

## 9. 哪些部分会随时间变化

- 平台 API 返回顺序；
- stars、forks、支持量；
- 页面标题、描述、图片和日期；
- Sitemap 内容；
- 网络失败、限流和超时；
- 项目被删除、归档或改名；
- 去重候选集合；
- 相对正态化分数。

因此新运行应追求“方法和质量标准可复现”，而不是与 Run #11 文件哈希完全相同。

## 10. 开发变更的验证

普通代码和 PR 不应直接启动完整抓取。仓库的 `Validate crawler` 工作流执行：

```bash
python -m compileall -q crawler tests scripts
python -m unittest discover -s tests -v
```

本地提交前也应执行相同命令。完整 10k 抓取只在确实需要刷新数据版本时手动运行。
