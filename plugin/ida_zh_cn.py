# -*- coding: utf-8 -*-
"""
ida_zh_cn -- IDA Pro 9.x 简体中文界面 (运行时汉化插件, Qt5 / PyQt5)

  版权所有 (c) 2026 3641397194-wq    许可证: MIT (词典的第三方来源见 NOTICE.md)
  项目主页: https://github.com/3641397194-wq/ida-zh-cn

不修改 IDA 的任何文件。卸载: 删除 ida_zh_cn.py 和 zh_cn.json 即可。
菜单 Edit > Plugins > "中文界面 开/关" 可随时切回英文界面。

设计要点 -- 为什么不直接把所有控件文字都改成中文:
  * 停靠窗口的 windowTitle 就是 IDA 的窗口标识, find_widget("Output window") 之类的脚本靠它查找;
    菜单项文字则被 attach_action_to_menu("Edit/Plugins/") 之类的路径查找使用。
    直接改这些文字会让脚本和其他插件失效。所以本插件分两条路:
      - 菜单栏 / 菜单 / 标签页 / 表头: 在"绘制层"翻译 (QProxyStyle), 控件上的真实文字保持英文。
      - 标签、按钮、提示、对话框标题: 纯显示文字, 直接替换, 并记住原文以便还原。
      - 停靠窗口 / TWidget 的 windowTitle 从不修改。
  * 词典: zh_cn.json (英文 -> 中文, 精确匹配)。同目录放 zh_cn_user.json 可覆盖/补充。
  * 未命中的界面英文会记录到 ida_zh_cn_missing.txt (仅本地、已过滤), 方便补词。

详见 docs/how-it-works.md。
"""

__version__ = "1.0.0"

import json
import os
import re
import sys
import warnings

# IDA 自带的 PyQt5 在 Python 3.12 下定义 Qt 子类时会打印 sipPyTypeDict 弃用警告, 屏蔽之
warnings.filterwarnings("ignore", message=".*sipPyTypeDict.*")
warnings.filterwarnings("ignore", category=DeprecationWarning)

import ida_idaapi
import ida_kernwin

from PyQt5 import QtCore, QtWidgets  # noqa: E402

try:
    _HERE = os.path.dirname(os.path.abspath(__file__))
except NameError:  # 通过 exec() 热加载时没有 __file__
    import ida_diskio
    _HERE = os.path.join(ida_diskio.get_user_idadir(), "plugins")

DICT_PATH = os.path.join(_HERE, "zh_cn.json")
USER_DICT_PATH = os.path.join(_HERE, "zh_cn_user.json")
CONF_PATH = os.path.join(_HERE, "ida_zh_cn.conf.json")
MISSING_PATH = os.path.join(_HERE, "ida_zh_cn_missing.txt")

STATE_ATTR = "_ida_zh_cn_state"
SWEEP_MS = 700

P_STYLE = "_zh_style"
P_TEXT = "_zh_text"
P_TIP = "_zh_tip"
P_STIP = "_zh_stip"
P_TITLE = "_zh_title"
P_PLACE = "_zh_place"

# 动态文本 (正则). 用于状态栏、按序号命名的窗口等
_RULE_SRC = [
    (r"^IDA View-([A-Za-z0-9]+)$", r"IDA 视图-\1"),
    (r"^Hex View-(\d+)$", r"十六进制视图-\1"),
    (r"^Pseudocode-([A-Za-z0-9]+)$", r"伪代码-\1"),
    (r"^Structures?-?(\d*)$", r"结构体\1"),
    (r"^Stack view-?(.*)$", r"栈视图\1"),
    (r"^Line (\d+) of (\d+)(.*)$", r"第 \1 行,共 \2 行\3"),
    (r"^AU:(\s+)idle(\s*)$", r"自动分析:\1空闲\2"),
    (r"^AU:(\s+)(.+)$", r"自动分析:\1\2"),
    (r"^Disk: (.+)$", r"磁盘: \1"),
    (r"^\(Synchronized with (.+)\)$", r"(与 \1 同步)"),
    (r"^xrefs to (.+)$", r"\1 的交叉引用"),
    (r"^xrefs from (.+)$", r"来自 \1 的交叉引用"),
]

_RE_MNEM = re.compile(r"&([A-Za-z0-9])")
_RE_UI_TEXT = re.compile(r"^[A-Za-z][A-Za-z &'/,.()\-:]{2,70}$")

# 调试开关: 出问题时可分别关闭 "绘制层样式" 或 "文字替换" 来定位
FLAGS = {"style": True, "text": True}

DICT = {}
RULES = [(re.compile(p), r) for p, r in _RULE_SRC]
_missing_seen = set()


# --------------------------------------------------------------------------- #
# 词典与翻译
# --------------------------------------------------------------------------- #
def _core(v):
    v = re.sub(r"\(&.\)", "", v).replace("&", "")
    for e in ("...", "…"):
        if v.endswith(e):
            v = v[: -len(e)]
    return v.strip()


def load_dict():
    global DICT
    d = {}
    for p in (DICT_PATH, USER_DICT_PATH):
        if not os.path.isfile(p):
            continue
        try:
            with open(p, encoding="utf-8") as f:
                raw = json.load(f)
        except Exception as e:  # noqa: BLE001
            ida_kernwin.msg("[ida_zh_cn] 读取词典失败 %s: %s\n" % (p, e))
            continue
        for k, v in raw.items():
            if k.startswith("_") or not isinstance(v, str):
                continue
            nk = k.replace("&", "").replace("~", "").strip()
            for e in ("...", "…"):
                if nk.endswith(e):
                    nk = nk[: -len(e)].rstrip()
            d[nk] = _core(v)
    DICT = d
    return len(d)


def translate(raw, mnemonic=True):
    """英文 -> 中文, 没有对应译文返回 None。保留省略号、冒号、首尾空白;
    mnemonic=True 时在译文后追加助记符 (&X) (用于按钮/标签, 绘制层菜单不加)。"""
    if not raw or not isinstance(raw, str) or len(raw) > 300:
        return None
    if raw.lstrip().startswith("<") and ">" in raw:  # 富文本, 不动
        return None
    lead = raw[: len(raw) - len(raw.lstrip())]
    trail = raw[len(raw.rstrip()):]
    s = raw.strip()
    if not s:
        return None
    m = _RE_MNEM.search(s)
    mn = m.group(1) if m else None
    k = s.replace("&&", "\0").replace("&", "").replace("\0", "&").replace("~", "")
    ell = ""
    for e in ("...", "…"):
        if k.endswith(e):
            k = k[: -len(e)].rstrip()
            ell = e
            break
    colon = ""
    zh = DICT.get(k)
    if zh is None and k.endswith(":"):
        zh = DICT.get(k[:-1].rstrip())
        colon = ":"
    if zh is None:
        for pat, rep in RULES:
            if pat.match(s):
                return lead + pat.sub(rep, s) + trail
        return None
    if zh == k:
        return None
    out = zh
    if mn and mnemonic:
        end = ""
        if out and out[-1] in ":：":     # 词典值自带冒号时, 助记符放在冒号前
            out, end = out[:-1], out[-1]
        out += "(&%s)" % mn.upper() + end
    return lead + out + colon + ell + trail


def translate_menu(text):
    """绘制层文字 (菜单/标签页/表头): 可能带 '\\t快捷键' 后缀, 只翻译前半段; 不追加助记符后缀。"""
    if not text:
        return None
    left, sep, right = text.partition("\t")
    z = translate(left, mnemonic=False)
    if z is None or z == left:
        return None
    return z + sep + right


def _note_missing(raw):
    if raw in _missing_seen or len(_missing_seen) > 4000:
        return
    if not _RE_UI_TEXT.match(raw) or "_" in raw or raw.isupper() or not any(c.islower() for c in raw):
        return
    _missing_seen.add(raw)
    try:
        with open(MISSING_PATH, "a", encoding="utf-8") as f:
            f.write(raw + "\n")
    except Exception:  # noqa: BLE001
        pass


# --------------------------------------------------------------------------- #
# 绘制层翻译: 菜单栏 / 菜单 / 标签页 / 表头
# --------------------------------------------------------------------------- #
_QS = QtWidgets.QStyle
_QO = QtWidgets.QStyleOption
_PAINT_ELEMENTS = {
    _QS.CE_MenuBarItem, _QS.CE_MenuItem, _QS.CE_HeaderLabel, _QS.CE_Header,
    _QS.CE_TabBarTabLabel, _QS.CE_TabBarTab,
}


def _expected_option_type(option):
    """包装类型 -> 选项自带的类型码。"""
    if isinstance(option, QtWidgets.QStyleOptionMenuItem):
        return _QO.SO_MenuItem
    if isinstance(option, QtWidgets.QStyleOptionHeader):
        return _QO.SO_Header
    if isinstance(option, QtWidgets.QStyleOptionTab):
        return _QO.SO_Tab
    return None


def _patched_option(option):
    """返回文字已翻译的选项副本; 无需翻译时返回原对象。

    关键的安全校验: 样式选项是 Qt 栈上的临时对象, 在 IDA 自带 PyQt5 + sip + Python 3.12 下,
    sip 可能把同一地址上一个已过期、类型不同的包装器交回来 (实测: 选项真实类型是 MenuItem,
    包装器却是 QStyleOptionHeader), 读它的 .text 会访问违规、直接崩掉 IDA。
    所以读取任何字段之前先核对 "选项自带的类型码 == 包装类型对应的类型码", 不一致就原样放行。
    """
    try:
        exp = _expected_option_type(option)
        if exp is None or option.type != exp:
            return option
        t = option.text
        if not t:
            return option
        z = translate_menu(t)
        if z is None:
            _note_missing(t.replace("&", "").split(chr(9))[0].strip())
            return option
        o2 = type(option)(option)
        o2.text = z
        return o2
    except Exception:  # noqa: BLE001
        return option


class ZhStyle(QtWidgets.QProxyStyle):
    # 只覆盖 drawControl。不要覆盖 sizeFromContents: 那条路径里读选项字段曾导致崩溃,
    # 而中文菜单项几乎都比英文窄, 不需要重算宽度。
    def drawControl(self, element, option, painter, widget=None):
        if element in _PAINT_ELEMENTS:
            option = _patched_option(option)
        super().drawControl(element, option, painter, widget)


# --------------------------------------------------------------------------- #
# 文字替换: 标签 / 按钮 / 提示 / 对话框标题 (可还原)
# --------------------------------------------------------------------------- #
def _swap(obj, getter, setter, prop):
    try:
        raw = getter()
    except Exception:  # noqa: BLE001
        return
    if not raw:
        return
    z = translate(raw)
    if z is None:
        _note_missing(raw.strip())
        return
    if z != raw:
        try:
            obj.setProperty(prop, raw)
            setter(z)
        except Exception:  # noqa: BLE001
            pass


def _restore(obj, getter_prop, setter):
    try:
        orig = obj.property(getter_prop)
        if orig:
            setter(orig)
            obj.setProperty(getter_prop, None)
    except Exception:  # noqa: BLE001
        pass


def _is_ida_dock_title(title):
    try:
        return ida_kernwin.find_widget(title) is not None
    except Exception:  # noqa: BLE001
        return True  # 拿不准就当作是窗口标识, 不动它


def _visit(w, st):
    """翻译单个控件。"""
    if isinstance(w, (QtWidgets.QMenu, QtWidgets.QMenuBar, QtWidgets.QTabBar, QtWidgets.QHeaderView)):
        if FLAGS["style"] and not w.property(P_STYLE):
            w.setStyle(st.style)
            w.setProperty(P_STYLE, True)
    if not FLAGS["text"]:
        return
    if isinstance(w, QtWidgets.QAbstractButton):
        if not (isinstance(w, QtWidgets.QToolButton) and w.defaultAction() is not None):
            _swap(w, w.text, w.setText, P_TEXT)
    elif isinstance(w, QtWidgets.QLabel):
        _swap(w, w.text, w.setText, P_TEXT)
    elif isinstance(w, QtWidgets.QGroupBox):
        _swap(w, w.title, w.setTitle, P_TEXT)
    elif isinstance(w, QtWidgets.QLineEdit):
        _swap(w, w.placeholderText, w.setPlaceholderText, P_PLACE)
    elif isinstance(w, QtWidgets.QComboBox):
        for i in range(min(w.count(), 200)):
            raw = w.itemText(i)
            z = translate(raw)
            if z is not None and z != raw:
                w.setItemText(i, z)
    elif isinstance(w, QtWidgets.QTreeWidget):
        hi = w.headerItem()
        if hi is not None:
            for c in range(hi.columnCount()):
                z = translate(hi.text(c))
                if z is not None:
                    hi.setText(c, z)
    elif isinstance(w, QtWidgets.QListWidget):
        for i in range(min(w.count(), 200)):
            it = w.item(i)
            z = translate(it.text())
            if z is not None and z != it.text():
                it.setText(z)

    # 工具提示 / 状态栏提示 (纯显示)
    if w.toolTip():
        _swap(w, w.toolTip, w.setToolTip, P_TIP)
    if isinstance(w, (QtWidgets.QToolBar, QtWidgets.QMenu, QtWidgets.QMenuBar)):
        for a in w.actions():
            if a.isSeparator():
                continue
            _swap(a, a.toolTip, a.setToolTip, P_TIP)
            _swap(a, a.statusTip, a.setStatusTip, P_STIP)

    # 对话框标题: 只改真正的对话框, 且不是 IDA 的停靠窗口
    if w.isWindow() and isinstance(w, QtWidgets.QDialog):
        t = w.windowTitle()
        if t and not _is_ida_dock_title(t):
            _swap(w, w.windowTitle, w.setWindowTitle, P_TITLE)


# --------------------------------------------------------------------------- #
# 安装 / 卸载
# --------------------------------------------------------------------------- #
class _Filter(QtCore.QObject):
    def __init__(self, st):
        super().__init__()
        self.st = st

    def eventFilter(self, obj, ev):
        try:
            if ev.type() == QtCore.QEvent.Polish and obj.isWidgetType():
                if obj.isWindow() or isinstance(obj, (QtWidgets.QMenu, QtWidgets.QMenuBar,
                                                      QtWidgets.QTabBar, QtWidgets.QHeaderView)):
                    self.st.visit_tree(obj)
        except Exception:  # noqa: BLE001
            pass
        return False


class _State:
    def __init__(self):
        self.style = ZhStyle()
        self.filter = _Filter(self)
        self.timer = QtCore.QTimer()
        self.timer.setInterval(SWEEP_MS)
        self.timer.timeout.connect(self.sweep)
        self.busy = False
        self.installed = False

    def visit_tree(self, root):
        if self.busy:
            return
        self.busy = True
        try:
            _visit(root, self)
            for c in root.findChildren(QtWidgets.QWidget):
                try:
                    _visit(c, self)
                except RuntimeError:
                    pass
        finally:
            self.busy = False

    def sweep(self):
        if self.busy:
            return
        app = QtWidgets.QApplication.instance()
        if app is None:
            return
        self.busy = True
        try:
            for w in app.allWidgets():
                try:
                    _visit(w, self)
                except RuntimeError:
                    pass  # C++ 对象已销毁
        except Exception:  # noqa: BLE001
            pass
        finally:
            self.busy = False

    def install(self):
        app = QtWidgets.QApplication.instance()
        if app is None or self.installed:
            return False
        app.installEventFilter(self.filter)
        self.timer.start()
        self.installed = True
        QtCore.QTimer.singleShot(50, self.sweep)
        return True

    def uninstall(self):
        app = QtWidgets.QApplication.instance()
        self.timer.stop()
        if app is not None:
            try:
                app.removeEventFilter(self.filter)
            except Exception:  # noqa: BLE001
                pass
            for w in app.allWidgets():
                try:
                    if w.property(P_STYLE):
                        w.setStyle(None)
                        w.setProperty(P_STYLE, None)
                    if isinstance(w, (QtWidgets.QAbstractButton, QtWidgets.QLabel)):
                        _restore(w, P_TEXT, w.setText)
                    elif isinstance(w, QtWidgets.QGroupBox):
                        _restore(w, P_TEXT, w.setTitle)
                    elif isinstance(w, QtWidgets.QLineEdit):
                        _restore(w, P_PLACE, w.setPlaceholderText)
                    _restore(w, P_TIP, w.setToolTip)
                    _restore(w, P_TITLE, w.setWindowTitle)
                    if isinstance(w, (QtWidgets.QToolBar, QtWidgets.QMenu, QtWidgets.QMenuBar)):
                        for a in w.actions():
                            _restore(a, P_TIP, a.setToolTip)
                            _restore(a, P_STIP, a.setStatusTip)
                except RuntimeError:
                    pass
        self.installed = False


def _load_conf():
    try:
        with open(CONF_PATH, encoding="utf-8") as f:
            return bool(json.load(f).get("enabled", True))
    except Exception:  # noqa: BLE001
        return True


def _save_conf(on):
    try:
        with open(CONF_PATH, "w", encoding="utf-8") as f:
            json.dump({"enabled": bool(on)}, f)
    except Exception:  # noqa: BLE001
        pass


def get_state():
    return getattr(sys, STATE_ATTR, None)


def enable(save=True):
    st = get_state()
    if st is None:
        st = _State()
        setattr(sys, STATE_ATTR, st)
    n = load_dict()
    ok = st.install()
    if save:
        _save_conf(True)
    ida_kernwin.msg("[ida_zh_cn] 中文界面已开启 (词典 %d 条)\n" % n)
    return ok


def disable(save=True):
    st = get_state()
    if st is not None:
        st.uninstall()
    if save:
        _save_conf(False)
    ida_kernwin.msg("[ida_zh_cn] 中文界面已关闭, 已还原英文\n")


def toggle():
    st = get_state()
    if st is not None and st.installed:
        disable()
    else:
        enable()


# --------------------------------------------------------------------------- #
# 插件入口
# --------------------------------------------------------------------------- #
class ZhCnPlugin(ida_idaapi.plugin_t):
    flags = ida_idaapi.PLUGIN_FIX
    comment = "IDA 简体中文界面"
    help = "运行时把 IDA 界面翻译成简体中文; 运行本插件可开/关"
    wanted_name = "中文界面 开/关"
    wanted_hotkey = ""

    def init(self):
        if QtWidgets.QApplication.instance() is None:
            return ida_idaapi.PLUGIN_SKIP
        if _load_conf():
            enable(save=False)
        return ida_idaapi.PLUGIN_KEEP

    def run(self, arg):
        toggle()

    def term(self):
        st = get_state()
        if st is not None:
            st.uninstall()


def PLUGIN_ENTRY():
    return ZhCnPlugin()


def reload_and_enable():
    """热加载入口: 在 IDAPython 控制台 exec 本文件后自动调用。"""
    old = get_state()
    if old is not None:
        old.uninstall()
        delattr(sys, STATE_ATTR)
    enable(save=False)


if __name__ == "__main__":  # File > Script file... (Alt+F7) 直接运行本文件即可立即开启, 无需重启 IDA
    reload_and_enable()
