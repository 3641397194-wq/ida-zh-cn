# 参与贡献

谢谢你愿意帮忙！最有价值的贡献是**补词条**，其次是报告 bug 和适配其他 IDA 版本。

## 补词条

1. 找到没翻的英文。最省事的办法：装上插件用一阵，打开 `ida_zh_cn.py` 同目录下的 `ida_zh_cn_missing.txt`，
   里面是插件没找到译文的界面英文（仅本地、已过滤掉带下划线的标识符和全大写缩写）。
2. 在 [`plugin/zh_cn.json`](plugin/zh_cn.json) 里加一行 `"英文原文": "中文译文"`。**键要规范化**：
   - 不写 `&` 快捷键标记；
   - 不写结尾的 `...`；
   - 大小写与界面完全一致（精确匹配）。
3. 译文里**不要**写 `(&X)` 助记符或结尾的 `...`，插件会按原文自动补回。
4. 校验：

   ```powershell
   python tools\check_dict.py
   ```

   它会报出空译文、没有汉字的译文、以及规范化后重复但译法不同的条目。
5. 提交 PR，说明你在哪个 IDA 版本的哪个窗口看到的这条文字。

只想自己用、不想提 PR？在 `ida_zh_cn.py` 同目录新建 `zh_cn_user.json`，格式相同，会覆盖内置词典。

### 术语约定

尽量与逆向社区的通行叫法一致，例如：导入表 / 导出表、反汇编、交叉引用、段、调试器、转储、伪代码、
栈变量、结构体、联合体。拿不准时优先直白，不要意译。

## 改代码前请读

[`docs/how-it-works.md`](docs/how-it-works.md) 第 4 节“必须遵守的安全守则”。其中两条最重要：

- **不要改任何会被脚本当作标识的文字**（停靠窗口 `windowTitle`、菜单项 `QAction.text`）。
- **在 `QProxyStyle` 里读样式选项之前必须校验类型码**，否则可能让 IDA 访问违规崩溃。

PR 清单：

- [ ] `python -m py_compile plugin/ida_zh_cn.py` 通过，`python tools/check_dict.py` 通过
- [ ] 在真实的 IDA 里验证过：不崩溃；开启后 `find_widget("Output window")` 仍能找到；关闭后文字完整还原
- [ ] 如果新增了 `setText` 类的替换，说明为什么这个文字不会被 IDA / 脚本反查
- [ ] 如果改了设计图源文件，附上 `tools/design/build.ps1` 重新渲染出的 `assets/*.png`

## 报告问题

请用 Issue 模板，并附上：IDA 版本、操作系统、Output 窗口里 `[ida_zh_cn]` 开头的那几行。
如果是崩溃，在 `plugin/ida_zh_cn.py` 里把 `FLAGS` 的 `style` / `text` 分别设为 `False` 试一次，告诉我们哪一个会崩，能省很多时间。

## 行为准则

友善、就事论事。这是个小项目，我们希望它保持轻松。
