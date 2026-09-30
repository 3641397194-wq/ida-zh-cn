# 工作原理

本文说明 `ida_zh_cn` 为什么这样设计，以及在 IDA 9.1（Qt 5.15.3、IDA 自带 PyQt5、Python 3.12）上实测得到的几条经验。
读完你应该能判断：某个改动是否安全。

## 1. 问题：直接改控件文字会弄坏什么

以下结论均由对照实验得到（同一个 IDA 实例，改前改后各测一次）：

| 操作 | 结果 |
|---|---|
| 只改 `QTabBar` 里的标签页文字 | `find_widget("Imports")` 仍为 `True`，`get_widget_title()` 仍为 `Imports` —— 安全 |
| 改停靠窗口 `QWidget.windowTitle` | `find_widget("Imports")` 变为 `False`，`get_widget_title()` 变成中文 —— **`windowTitle` 就是窗口标识** |
| 把菜单栏里 `Options` 的 `QAction.text` 改成中文 | `attach_action_to_menu("Options/", …)` 返回 `False` |
| 把 `Edit` 和 `Plugins` 的 `QAction.text` 改成中文 | `attach_action_to_menu("Edit/Plugins/", …)` 在中文「编辑」下另建一个英文 `Plugins` 子菜单 |
| 对列表的 `chooser_table_widget_model_t` 调用 `setHeaderData()` | 返回 `False`，表头不变（自定义 C++ 模型） |

所以：**凡是会被脚本或 IDA 当作标识的文字，都不能改。** 这类文字集中在停靠窗口标题、菜单项文字，其中列表表头压根改不了。

## 2. 方案：两条通道

```
界面文字
├─ 标识类：菜单栏、菜单、标签页、表头
│    └─ 绘制层翻译：给这些控件挂一个 QProxyStyle，只覆盖 drawControl，
│       在绘制那一刻把选项里的 text 换成中文；控件本身的文字仍是英文。
├─ 纯显示类：QLabel、按钮、工具提示、对话框标题、QComboBox 项、QTreeWidget 表头……
│    └─ setText，并把原文存进控件的动态属性 _zh_*，关闭插件时原样写回。
└─ 停靠窗口 / TWidget 的 windowTitle：从不修改
```

`ZhStyle` 通过 `QWidget.setStyle()` 挂到目标控件上（应用样式表 `QStyleSheetStyle` 会把它包成基础样式，
所以 IDA 的 QSS 主题外观不变）。所有控件共用同一个 `ZhStyle` 实例，实例由插件状态对象持有。

一个 700 ms 的定时器扫一遍 `QApplication.allWidgets()`（645 个控件约 7 ms），再加一个 `Polish` 事件过滤器，
让新弹出的对话框和菜单在第一次显示前就完成翻译。

对话框标题只改 `QDialog` 且 `find_widget(title)` 找不到的，即真正的对话框而不是 IDA 的停靠窗口。

## 3. 词典与翻译规则

`plugin/zh_cn.json` 是扁平的 `{"英文": "中文"}`，键是**规范化**的英文：去掉 `&` 快捷键标记、去掉结尾的 `...`。
翻译时（`translate()`）：

1. 记下原文里的 `&X` 助记符、结尾的 `...`/`…`、结尾冒号、首尾空白；
2. 用去掉这些之后的键查词典；再试一次去掉冒号；再试 `_RULE_SRC` 里的正则（状态栏、按序号命名的窗口）；
3. 把助记符（仅按钮/标签类，写成 `(&X)`）、省略号、冒号、空白按原样接回去。

绘制层（菜单/标签页/表头）不追加 `(&X)`：中文菜单项几乎都比英文窄，不需要额外宽度。

**合并规则。** 词典由两个 MIT 社区词典与本项目新增词条合并而成。冲突时默认取 `tuxi/ida-i18n` 的译法
（术语更规范，如「导入表」「调试器」「转储」），少数它译得别扭的（`Down`→向下、`Reset desktop`→重置桌面布局、
`Offset…`→偏移量… 等）改取 `0x-focus` 的；本项目新增的词条最后覆盖。来源与版权见 [NOTICE.md](../NOTICE.md)。

## 4. 必须遵守的安全守则

这些是踩坑后写下来的，改代码前请读一遍。

### 4.1 不要在 `sizeFromContents` / `drawControl` 里不加校验地读样式选项

样式选项（`QStyleOptionMenuItem` 等）是 Qt 栈上的临时对象。在 IDA 自带的 PyQt5 + sip + Python 3.12 下，
sip 有时会把**同一地址上一个已过期、类型不同的包装器**交给你。用 `faulthandler` 抓到的现场：

```
size ctype 8 QStyleOptionHeader opt.type 4 opt.version 1     # ← 接着读 option.text，访问违规
```

`ctype 8` 是菜单栏项，选项的类型码 `4` 是 `SO_MenuItem`，可 Python 侧拿到的包装类型却是 `QStyleOptionHeader`。
按错误的偏移读 `QString` → `0xC0000005`，整个 IDA 崩溃。触发点出现在打开/关闭对话框的过程中，很难联想到样式。

因此：

- 读任何字段之前先核对 `option.type == 包装类型对应的 SO_*`，不一致就原样放行（`_patched_option`）；
- 不覆盖 `sizeFromContents`（它曾是崩溃入口，而且没有必要）；
- 任何 `try/except` 都救不了访问违规，只能靠事前校验。

### 4.2 不要用 `PluginForm.TWidgetToPyQtWidget` / `FormToPyQtWidget`

在 sip 来自 site-packages、Qt 绑定来自 IDA 自带 `python\PyQt5` 的环境里，它们会直接崩溃。
要找某个窗口对应的 Qt 控件，遍历 `QApplication.allWidgets()` 按标题/类名匹配。

### 4.3 不要给控件共用样式后再把样式挂到控件名下（`setParent`）

试过给每个控件各建一个样式并 `setParent(widget)`：不再崩溃，但菜单栏、表头、标签页又变回英文——
Python 端重写的 `drawControl` 看起来不再被调用（推测与 sip 对象所有权转移有关，未深究）。
**不崩不等于修好了**——每次改动都要同时确认：不崩溃，并且翻译仍在生效。

### 4.4 只改显示，不改标识

见第 1 节。新增任何 `setText` / `setWindowTitle` 之前先想：这个文字会不会被 IDA 或脚本反查？

## 5. 怎么测试而不动你正在用的 IDA

在同一台机器上另起一个 IDA 实例，只加载一个小 exe：

```
ida.exe -A -c -o<临时>\t.i64 -S<测试脚本> <某个小 exe>
```

- 该实例需要 `HKCU\Software\Hex-Rays\IDA\Python3TargetDLL`（指向 `python3.dll`）才会加载 IDAPython。
  若你的注册表里没有，测试时临时写入、结束后删除；**只结束你自己启动的那个 PID**。
- 在脚本里 `faulthandler.enable(file=...)`，访问违规时能拿到 Python 调用栈。
- 截图用 `widget.grab()`，只渲染 IDA 自己的窗口；不要用整屏截图（会把桌面上别的窗口带进来）。
- 开关压力测试：反复 `process_ui_action("SetColors")` 并 `reject()`，以及打开/关闭字符串、名称、段、问题等窗口，
  每轮检查 `find_widget()` 与控件数量，并对比 `sys.getallocatedblocks()`。

`tools/design/` 里的对比图就是这样采集的真实界面。

## 6. 调试开关

`plugin/ida_zh_cn.py` 顶部有 `FLAGS = {"style": True, "text": True}`：把其中一项改成 `False`，再用 `Alt+F7` 重新运行该文件，
即可分别关掉绘制层翻译或文字替换。本项目定位崩溃时就是这样二分的。
