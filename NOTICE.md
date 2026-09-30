# 第三方声明 · Third-party notices

## 哪些是原创，哪些不是

| 部分 | 来源 |
|---|---|
| `plugin/ida_zh_cn.py`（插件本体）、`install.ps1`、`tools/`、`docs/`、`assets/` 下的全部设计与文档 | 本项目原创，MIT 许可 |
| `plugin/zh_cn.json`（词典） | **主体来自下面两个 MIT 许可的社区项目**，由本项目合并、规范化，并补充了表头、窗口名、图例、工具栏与提示语等词条 |

词典共 1860 条：其中 1712 条（约 92%）的英文原文与下列两个项目的词条重合，
本项目新增 148 条。重合词条的译文由本项目在两者之间择优取用（取舍规则见 `docs/how-it-works.md`）。

没有复制这两个项目的任何程序代码：本项目的插件实现方式（绘制层翻译 + 可还原的文字替换）与它们不同，
且为独立编写。

## 词典来源

### 0x-focus/IDA-Pro-9.0-Chinese-Translation
<https://github.com/0x-focus/IDA-Pro-9.0-Chinese-Translation> —— `zh_CN.json`

```
MIT License

Copyright (c) 2026 IDA Pro-CH contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### tuxi/ida-i18n
<https://github.com/tuxi/ida-i18n> —— `ida_i18n_zh_CN.json`

```
MIT License

Copyright (c) 2026 ida-i18n contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 商标与无关声明

IDA、IDA Pro、Hex-Rays 是 Hex-Rays SA 的商标。本项目为非官方社区项目，与 Hex-Rays 无隶属或授权关系；
仓库中不包含、也不分发任何 IDA 或 Hex-Rays 的文件。使用 IDA 需要你自己持有合法授权。

*IDA, IDA Pro and Hex-Rays are trademarks of Hex-Rays SA. This is an unofficial community project, not affiliated
with or endorsed by Hex-Rays. It contains no Hex-Rays files. You need your own valid IDA license.*
