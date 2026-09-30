# 更新日志

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [SemVer](https://semver.org/lang/zh-CN/)。

## [未发布]

### 新增
- `install.sh`：macOS / Linux 安装 / 卸载脚本，逻辑与 `install.ps1` 对齐（默认 `$IDAUSR/plugins` 或 `~/.idapro/plugins`，`--target`/`--uninstall`）。
- CI 矩阵扩展到 `windows-latest` / `ubuntu-latest` / `macos-latest`，三个平台都跑安装器往返测试。
- README（中/英）补充 macOS / Linux 安装步骤，兼容性表格标注插件本体在这两个平台上尚未用真实 IDA 验证。

## [1.0.0] — 2026-09-30

首个公开版本。

### 新增
- 运行时汉化插件 `ida_zh_cn`：菜单栏、菜单、标签页、列表表头在绘制层翻译；标签、按钮、提示、对话框标题直接替换并可还原。
- 1860 条词典 `zh_cn.json`（主体来自两个 MIT 社区词典，另新增 148 条，见 `NOTICE.md`）。
- `Edit → Plugins → 中文界面 开/关`，状态持久化；`Alt+F7` 直接运行 `ida_zh_cn.py` 可免重启生效。
- `zh_cn_user.json` 用户词典覆盖；`ida_zh_cn_missing.txt` 记录未命中的界面英文。
- `install.ps1` 安装 / 卸载脚本，`tools/check_dict.py` 词典校验，`tools/design/` 设计图源文件与渲染脚本，GitHub Actions CI。

### 已验证
- IDA Professional 9.1 · Windows 11 · Qt 5.15.3 · Python 3.12：窗口标识与菜单路径不受影响；8 轮开关压力测试无崩溃；重绘内存不增长；关闭后完整还原。

### 已知限制
- IDA 内核直接输出的文字（Output 窗口消息等）无法翻译；列表底部自绘状态行暂未处理。
- 仅在 IDA 9.1 上测试；使用 Qt6 / PySide6 的版本暂不支持。
