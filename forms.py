# -*- coding: utf-8 -*-
"""
ada_ui.forms — XAML-backed dialog wrappers
- Uses Theme.xaml for styling (merged into each window)
- Exposes alert(), confirm(), input_text(), big_buttons(), SelectFromList.show()
"""
from __future__ import annotations
from pathlib import Path

# pythonnet / WPF
import clr  # type: ignore
clr.AddReference("PresentationFramework")
clr.AddReference("PresentationCore")
clr.AddReference("WindowsBase")
from System.IO import StringReader
from System import String
from System.Windows import Window, Application, ResourceDictionary, MessageBox, MessageBoxButton, MessageBoxResult
from System.Windows.Markup import XamlReader
from System.Windows.Controls import Button, StackPanel, TextBlock, TextBox, ListBox
from System.Windows import Controls

HERE = Path(__file__).resolve().parent

# ---------- XAML loaders ----------
def _read_text(p: Path) -> str:
    with open(p, "r", encoding="utf-8") as f:
        return f.read()

def _parse_xaml(xaml_text: str):
    return XamlReader.Parse(StringReader(xaml_text).ReadToEnd())

def _merge_theme(win: Window):
    theme = HERE / "Theme.xaml"
    if theme.exists():
        try:
            rd = ResourceDictionary()
            rd.Source = theme.as_uri()
            # Some XamlReader environments prefer explicit load:
            # rd = _parse_xaml(_read_text(theme))
            # win.Resources.MergedDictionaries.Add(rd)
            win.Resources.MergedDictionaries.Add(rd)
        except Exception:
            pass

def _load_window(xaml_name: str) -> Window:
    xaml_path = HERE / xaml_name
    if not xaml_path.exists():
        raise IOError("XAML not found: {}".format(xaml_path))
    win = _parse_xaml(_read_text(xaml_path))
    if not isinstance(win, Window):
        # Wrap UserControl in a Window
        w = Window()
        w.Content = win
        win = w
    _merge_theme(win)
    # Size and placement
    win.Topmost = True
    # 1 = WidthAndHeight (enum)
    win.SizeToContent = 1
    return win

def _find_first(root, t):
    from System.Windows import LogicalTreeHelper as LTH
    q = [root]
    while q:
        n = q.pop(0)
        if isinstance(n, t):
            return n
        try:
            for c in LTH.GetChildren(n):
                q.append(c)
        except Exception:
            pass
    return None

# ---------- Public API ----------
def alert(message, title="Message"):
    try:
        win = _load_window("Alert.xaml")
        try:
            win.Title = title
        except Exception:
            pass
        tb = getattr(win, "MessageText", None) or _find_first(win, TextBlock)
        if tb is not None:
            tb.Text = String(str(message))
        ok = getattr(win, "OkButton", None) or _find_first(win, Button)
        if ok is not None:
            def _ok(sender, e):
                try: win.DialogResult = True
                except Exception: pass
                win.Close()
            ok.Click += _ok
        win.ShowDialog()
    except Exception:
        MessageBox.Show(str(message), str(title))

def confirm(message, title="Confirm", ok_text="OK", cancel_text="Cancel"):
    try:
        win = _load_window("Confirm.xaml")
        try:
            win.Title = title
        except Exception:
            pass
        tb = getattr(win, "MessageText", None) or _find_first(win, TextBlock)
        if tb is not None:
            tb.Text = String(str(message))
        ok = getattr(win, "OkButton", None) or _find_first(win, Button)
        cancel = getattr(win, "CancelButton", None)
        if ok is not None:
            try: ok.Content = ok_text
            except Exception: pass
            def _ok(sender, e):
                try: win.DialogResult = True
                except Exception: pass
                win.Close()
            ok.Click += _ok
        if cancel is not None and cancel is not ok:
            try: cancel.Content = cancel_text
            except Exception: pass
            def _cancel(sender, e):
                try: win.DialogResult = False
                except Exception: pass
                win.Close()
            cancel.Click += _cancel
        rv = win.ShowDialog()
        return bool(rv)
    except Exception:
        res = MessageBox.Show(str(message), str(title), MessageBoxButton.OKCancel)
        return res == MessageBoxResult.OK

def input_text(prompt="Enter text", title="Input"):
    try:
        win = _load_window("InputText.xaml")
        try:
            win.Title = title
        except Exception:
            pass
        tb = getattr(win, "PromptText", None) or _find_first(win, TextBlock)
        if tb is not None:
            tb.Text = String(str(prompt))
        box = getattr(win, "InputBox", None) or _find_first(win, TextBox)
        result = {"text": None}
        ok = getattr(win, "OkButton", None) or _find_first(win, Button)
        cancel = getattr(win, "CancelButton", None)
        if ok is not None:
            def _ok(sender, e):
                result["text"] = box.Text if box is not None else ""
                try: win.DialogResult = True
                except Exception: pass
                win.Close()
            ok.Click += _ok
        if cancel is not None:
            def _cancel(sender, e):
                result["text"] = None
                try: win.DialogResult = False
                except Exception: pass
                win.Close()
            cancel.Click += _cancel
        rv = win.ShowDialog()
        return result["text"] if rv else None
    except Exception:
        return None

def big_buttons(title, items, message=None, cancel=True):
    """Large button chooser driven by ButtonBox.xaml — returns selected label or None."""
    try:
        win = _load_window("ButtonBox.xaml")
        try:
            win.Title = title
        except Exception:
            pass
        msg = getattr(win, "MessageText", None) or _find_first(win, TextBlock)
        if msg is not None and message:
            msg.Text = String(str(message))
        host = getattr(win, "ButtonsHost", None) or _find_first(win, StackPanel)
        result = {"choice": None}
        def _make(label):
            def _click(sender, e):
                result["choice"] = label
                try: win.DialogResult = True
                except Exception: pass
                win.Close()
            return _click
        for label in items:
            b = Button()
            b.Content = String(str(label))
            b.Margin = Controls.Thickness(4)
            b.MinWidth = 180
            b.Click += _make(label)
            if host is not None:
                host.Children.Add(b)
        if cancel:
            c = Button()
            c.Content = "Cancel"
            c.Margin = Controls.Thickness(4)
            def _cancel(sender, e):
                result["choice"] = None
                try: win.DialogResult = False
                except Exception: pass
                win.Close()
            c.Click += _cancel
            if host is not None:
                host.Children.Add(c)
        win.ShowDialog()
        return result["choice"]
    except Exception:
        return None

class SelectFromList(object):
    @staticmethod
    def show(items, title="Select", name_attr=None, button_name="OK", multiselect=False):
        try:
            win = _load_window("SelectFromList.xaml")
            try:
                win.Title = title
            except Exception:
                pass
            lb = getattr(win, "ItemsList", None) or _find_first(win, ListBox)
            if lb is None:
                return None
            from System.Windows.Controls import SelectionMode
            lb.SelectionMode = SelectionMode.Multiple if multiselect else SelectionMode.Single

            def _label(x):
                if name_attr and hasattr(x, name_attr):
                    return str(getattr(x, name_attr))
                return str(x)

            for it in items:
                lb.Items.Add(_label(it))

            result = {"index": None, "indices": None}
            ok = getattr(win, "OkButton", None) or _find_first(win, Button)
            if ok is not None:
                try: ok.Content = button_name
                except Exception: pass
                def _ok(sender, e):
                    if multiselect:
                        sel = [i for i in range(lb.Items.Count) if lb.SelectedItems.Contains(lb.Items[i])]
                        result["indices"] = sel
                    else:
                        result["index"] = lb.SelectedIndex
                    try: win.DialogResult = True
                    except Exception: pass
                    win.Close()
                ok.Click += _ok
            cancel = getattr(win, "CancelButton", None)
            if cancel is not None:
                def _cancel(sender, e):
                    try: win.DialogResult = False
                    except Exception: pass
                    win.Close()
                cancel.Click += _cancel

            rv = win.ShowDialog()
            if not rv:
                return None
            if multiselect:
                if result["indices"] is None:
                    return []
                return [items[i] for i in result["indices"]]
            else:
                if result["index"] is None or result["index"] < 0:
                    return None
                return items[result["index"]]
        except Exception:
            return None
