<div align="center">

<img src="assets/banner.png" alt="IDA Chinese UI — runtime localization plugin" width="100%">

<br>

[![CI](https://github.com/3641397194-wq/ida-zh-cn/actions/workflows/ci.yml/badge.svg)](https://github.com/3641397194-wq/ida-zh-cn/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-6e86ff?labelColor=0a1020)](LICENSE)
[![IDA Pro](https://img.shields.io/badge/IDA%20Pro-9.1%20tested-21e0d0?labelColor=0a1020)](#compatibility)

**A runtime Simplified-Chinese UI for IDA Pro 9.x — patches nothing, toggles with one click, and never breaks your scripts.**

[简体中文](README.md)

</div>

## Why another localization?

IDA has no official language pack. The usual community approach walks the Qt widget tree and rewrites every string.
On IDA 9.1 that has two silent side effects (both verified):

| If you rewrite… | …this happens |
|---|---|
| a dock widget's `windowTitle` | that *is* IDA's widget identifier — `ida_kernwin.find_widget("Output window")` starts returning `None` |
| a menu `QAction.text` | `attach_action_to_menu("Options/")` fails; `Edit/Plugins/` grows a duplicate English `Plugins` submenu |

`ida_zh_cn` keeps identifiers untouched:

- **menu bar / menus / tab bars / list headers** are translated at *paint time* through a `QProxyStyle` — the widgets still hold English;
- **labels, buttons, tooltips, real dialog titles** are display-only, so their text is replaced and the original is remembered for a clean revert;
- dock `windowTitle`s are never modified.

Details and the crash you can cause if you get this wrong: [docs/how-it-works.md](docs/how-it-works.md) (Chinese).

## Install

Windows / macOS / Linux, IDA Pro 9.x built on **Qt5 / PyQt5**, IDAPython working.

**Windows**

```powershell
git clone https://github.com/3641397194-wq/ida-zh-cn.git
cd ida-zh-cn
powershell -ExecutionPolicy Bypass -File .\install.ps1     # add -Uninstall to remove
```

**macOS / Linux**

```bash
git clone https://github.com/3641397194-wq/ida-zh-cn.git
cd ida-zh-cn
chmod +x install.sh
./install.sh          # add --uninstall to remove, --target <dir> for a custom path
```

Either script copies `plugin/ida_zh_cn.py` and `plugin/zh_cn.json` into IDA's **user** plugin directory
(`$IDAUSR/plugins` if set, otherwise `%APPDATA%\Hex-Rays\IDA Pro\plugins` on Windows or `~/.idapro/plugins` on macOS/Linux).
Then either restart IDA, or press **Alt+F7** (File → Script file…) and pick `ida_zh_cn.py` to switch on immediately.

Toggle back to English any time: `Edit → Plugins → 中文界面 开/关`.

## Compatibility

| Environment | Status |
|---|---|
| IDA Professional **9.1**, Windows 11, Qt 5.15.3, Python 3.12 | ✅ tested |
| Other Qt5 / PyQt5 builds (e.g. 9.0) | ⚠️ untested, should work |
| Qt6 / PySide6 builds | ❌ not supported yet (PRs welcome) |
| macOS, Linux (installer `install.sh` provided, copy/uninstall paths covered by CI) | ⚠️ the plugin itself is unverified on a real IDA there — feedback welcome |

Not translatable from a plugin: text the IDA kernel writes itself (Output-window messages, some status-bar text)
and, of course, data (disassembly, hex view).

## Community (Chinese-speaking, QQ)

Bug reports, dictionary contributions, or general IDA/reverse-engineering chat — these QQ groups are Chinese-speaking:

| Group | Number |
|---|---|
| ai交流1群 | 1057540028 |
| ai交流2群 | 1077074552 |
| Cool coffeeAI交流 | 618179023 |

QR codes: see the [Chinese README](README.md#交流群).

## Contributing

Adding words is the most useful contribution — see [CONTRIBUTING.md](CONTRIBUTING.md).
Put your own strings in `zh_cn_user.json` next to the plugin to override the built-in dictionary.

## License & credits

Code, scripts, docs and artwork: [MIT](LICENSE), original to this project.
The dictionary is mostly a merge of two MIT-licensed community dictionaries —
[0x-focus/IDA-Pro-9.0-Chinese-Translation](https://github.com/0x-focus/IDA-Pro-9.0-Chinese-Translation) and
[tuxi/ida-i18n](https://github.com/tuxi/ida-i18n) — plus 148 entries added here; see [NOTICE.md](NOTICE.md).
No program code was copied from either.

IDA, IDA Pro and Hex-Rays are trademarks of Hex-Rays SA. This is an unofficial project, not affiliated with Hex-Rays,
and contains no Hex-Rays files. You need your own valid IDA license.
