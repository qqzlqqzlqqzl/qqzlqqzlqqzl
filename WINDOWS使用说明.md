# Windows 一键运行说明

## 最简单的用法

1. 在 GitHub 仓库页面点击 **Code → Download ZIP**。
2. 将 ZIP **完整解压**到一个路径较短的目录，例如：

   ```text
   D:\hardware-crawler
   ```

3. 双击根目录的：

   ```text
   RUN_WINDOWS.bat
   ```

4. 第一次运行时，脚本会自动完成：
   - 检查 Python 3.10 或更高版本；
   - 如未安装，可通过 Windows `winget` 自动安装 Python 3.12；
   - 创建独立环境 `.venv-windows`；
   - 安装依赖；
   - 询问目标条数和输出目录；
   - 运行爬虫；
   - 正式 10k 运行结束后自动验收；
   - 打开结果目录。

不需要手工输入 `pip`、创建虚拟环境或修改 PowerShell 执行策略。

## 推荐输入

正式复现时：

```text
目标条数：10500
输出目录：直接按 Enter，使用 output_v2
```

GitHub Token 建议填写。输入时内容不会显示，也不会写入文件，只在当前运行进程中使用。没有 Token 也可以运行，但更容易遇到 GitHub API 限流。

## 先做小规模测试

为了先验证本机环境，可以输入：

```text
目标条数：500
输出目录：output_test
```

小目标会生成文件，但程序最后可能提示未达到正式的 10,000 条质量门槛。这是预期行为，不代表安装失败。

## 运行完成后怎么看

正式结果默认位于：

```text
output_v2\
```

优先打开：

```text
output_v2\开源硬件商业化机会库_10000条.xlsx
```

推荐使用 Microsoft Excel 或 WPS 表格。

阅读顺序：

1. `摘要`；
2. `来源状态`；
3. `评分方法`；
4. `项目机会库`。

## 单独验收已有结果

双击：

```text
CHECK_RESULT_WINDOWS.bat
```

默认检查 `output_v2`，包括：

- 必要文件是否齐全；
- 数据条数和平台数；
- 项目 ID 与 URL 是否重复；
- 前四平台集中度；
- 评分范围；
- Excel 是否包含四个工作表。

验收通过后，可以选择立即打开 Excel。

## 常见问题

### 1. 提示没有 Python

脚本会先询问是否用 `winget` 自动安装 Python 3.12。选择默认的 `Y` 即可。

如电脑没有 `winget`，手动安装 Python 时务必勾选：

```text
Add python.exe to PATH
```

安装完成后重新双击 `RUN_WINDOWS.bat`。

### 2. 依赖安装失败

通常是网络、代理、防火墙或杀毒软件拦截。可以：

- 换一个网络；
- 暂时关闭会拦截 Python 下载的安全软件；
- 删除 `.venv-windows` 后重新双击运行；
- 检查公司网络是否限制 PyPI。

### 3. 抓取很慢

程序会访问多个公开网站，部分来源可能响应慢或暂时不可达。窗口仍有输出时不要关闭。

完整 10k 运行耗时取决于网络和各平台状态，不同日期结果也可能略有变化。

### 4. 窗口闪退

不要直接运行 `windows\run.ps1`。应双击根目录的 `RUN_WINDOWS.bat`，批处理会绕过本机 PowerShell 脚本策略，并在结束前暂停。

### 5. 路径问题

建议：

- 完整解压后再运行，不要在压缩包预览中双击；
- 避免放在层级非常深的目录；
- 不要把仓库拆散，只保留 BAT 文件；
- 路径中有中文或空格通常可以使用，但较短路径更稳妥。

## 命令行参数（可选）

也可以在 CMD 或 PowerShell 中直接指定参数：

```bat
RUN_WINDOWS.bat -Target 10500 -Output output_v2 -NoPause
```

跳过自动验收：

```bat
RUN_WINDOWS.bat -Target 10500 -Output output_v2 -SkipValidation
```

只测试 Windows 入口和环境，不进行抓取：

```bat
RUN_WINDOWS.bat -DryRun -NoPause
```

验收指定目录：

```bat
CHECK_RESULT_WINDOWS.bat -Output D:\data\output_v2
```

## 安全说明

- Token 不会被脚本保存到磁盘；
- 不要把 Token 写入 BAT、README 或截图；
- 程序只访问公开网页和公开 API；
- 抓取结果不代表项目许可商用，生产前仍需逐项核验许可证、专利、商标和产品法规。
