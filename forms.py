# -*- coding: utf-8 -*-
"""
ada_ui.forms
Lightweight wrapper around ADa XAML dialogs (Alert, Confirm, ButtonBox, InputText, SelectFromList).
Works under pyRevit CPython (pythonnet) and should be resilient if some names differ.

XAML files expected in the same folder:
- Theme.xaml
- Controls.xaml
- Alert.xaml
- Confirm.xaml
- ButtonBox.xaml
- InputText.xaml
- SelectFromList.xaml
"""
from __future__ import annotations
import os
from pathlib import Path

# pythonnet / WPF
import clr  # type: ignore
clr.AddReference("PresentationFramework")
clr.AddReference("PresentationCore")
clr.AddReference("WindowsBase")
clr.AddReference("System")
from System.Windows import Window, Application
from System.Windows.Markup import XamlReader
from System.IO import StringReader
from System.Windows.Controls import Button, StackPanel, TextBlock, TextBox, ListBox
from System.Windows import Controls
from System.Windows import Forms as WinForms  # not used, but keeps parity
from System import String

HERE = Path(__file__).resolve().parent

def _read_text(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def _parse_xaml(xaml_text: str):
    # Some XAML may include themes/styles from Theme.xaml; leave merging to specific loaders if needed
    return XamlReader.Parse(StringReader(xaml_text).ReadToEnd())

def _load_window(xaml_name: str) -> Window:
    xaml_path = HERE / xaml_name
    if not xaml_path.exists():
        raise IOError("XAML not found: {}".format(xaml_path))
    xaml_text = _read_text(xaml_path)
    win = _parse_xaml(xaml_text)
    if not isinstance(win, Window):
        # Some XAML may be a UserControl; embed in a Window
        from System.Windows.Controls import ContentControl
        w = Window()
        w.Content = win
        win = w
    # Basic window defaults
    win.Topmost = True
    win.SizeToContent = 1  # WidthAndHeight
    return win

def _find_first(root, t):
    # breadth-first search by type
    from System.Windows import LogicalTreeHelper as LTH
    q = [root]
    while q:
        n = q.pop(0)
        if isinstance(n, t):
            return n
        for c in LTH.GetChildren(n):
            try:
                q.append(c)
            except Exception:
                pass
    return None

def alert(message, title="Message"):
    """Simple alert dialog using Alert.xaml (falls back to MessageBox)."""
    try:
        win = _load_window("Alert.xaml")
        try:
            win.Title = title
        except Exception:
            pass
        # Try to find a text presenter
        tb = getattr(win, "MessageText", None) or _find_first(win, TextBlock)
        if tb is not None:
            try:
                tb.Text = String(str(message))
            except Exception:
                tb.Text = str(message)
        # Wire first button to close
        btn = getattr(win, "OkButton", None) or _find_first(win, Button)
        if btn is not None:
            def _ok(sender, e):
                win.DialogResult = True
                win.Close()
            btn.Click += _ok
        win.ShowDialog()
    except Exception:
        # Fallback to plain MessageBox if XAML load fails
        from System.Windows import MessageBox
        MessageBox.Show(str(message), str(title))

def confirm(message, title="Confirm", ok_text="OK", cancel_text="Cancel"):
    """Confirm dialog using Confirm.xaml; returns True/False."""
    try:
        win = _load_window("Confirm.xaml")
        try:
            win.Title = title
        except Exception:
            pass
        tb = getattr(win, "MessageText", None) or _find_first(win, TextBlock)
        if tb is not None:
            tb.Text = String(str(message))
        ok = getattr(win, "OkButton", None)
        cancel = getattr(win, "CancelButton", None)
        if ok is None:
            ok = _find_first(win, Button)
        if ok is not None:
            try: ok.Content = ok_text
            except Exception: pass
            def _ok(sender, e):
                win.DialogResult = True
                win.Close()
            ok.Click += _ok
        if cancel is None or cancel == ok:
            # try to find another button
            # not perfect, but we attempt to pick the next button in the tree
            from System.Windows import LogicalTreeHelper as LTH
            found_second = None
            for c in LTH.GetChildren(win):
                b = _find_first(c, Button)
                if b and b is not ok:
                    found_second = b; break
            cancel = found_second
        if cancel is not None:
            try: cancel.Content = cancel_text
            except Exception: pass
            def _cancel(sender, e):
                win.DialogResult = False
                win.Close()
            cancel.Click += _cancel
        return bool(win.ShowDialog())
    except Exception:
        from System.Windows import MessageBox, MessageBoxResult, MessageBoxButton
        res = MessageBox.Show(str(message), str(title), MessageBoxButton.OKCancel)
        return res == MessageBoxResult.OK

def input_text(prompt="Enter text", title="Input"):
    """Text input using InputText.xaml; returns string or None."""
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
        value = {"text": None}
        ok = getattr(win, "OkButton", None) or _find_first(win, Button)
        cancel = getattr(win, "CancelButton", None)
        if ok is not None:
            def _ok(sender, e):
                value["text"] = box.Text if box is not None else ""
                win.DialogResult = True
                win.Close()
            ok.Click += _ok
        if cancel is not None:
            def _cancel(sender, e):
                value["text"] = None
                win.DialogResult = False
                win.Close()
            cancel.Click += _cancel
        rv = win.ShowDialog()
        return value["text"] if rv else None
    except Exception:
        # last resort: return None
        return None

def big_buttons(title, items, message=None, cancel=True):
    """Large button chooser using ButtonBox.xaml; returns selected label or None."""
    try:
        win = _load_window("ButtonBox.xaml")
        try:
            win.Title = title
        except Exception:
            pass
        # message text (optional)
        msg = getattr(win, "MessageText", None) or _find_first(win, TextBlock)
        if msg is not None and message:
            msg.Text = String(str(message))
        # host panel to place buttons into
        host = getattr(win, "ButtonsHost", None)
        if host is None:
            host = _find_first(win, StackPanel)
        result = {"choice": None}
        def _make(label):
            def _click(sender, e):
                result["choice"] = label
                win.DialogResult = True
                win.Close()
            return _click
        # Create one button per item
        for label in items:
            b = Button()
            b.Content = String(str(label))
            b.Margin = Controls.Thickness(4)
            b.MinWidth = 180
            b.Click += _make(label)
            if host is not None:
                host.Children.Add(b)
        # optional cancel button (esc-like)
        if cancel:
            c = Button()
            c.Content = "Cancel"
            c.Margin = Controls.Thickness(4)
            def _cancel(sender, e):
                result["choice"] = None
                win.DialogResult = False
                win.Close()
            c.Click += _cancel
            if host is not None:
                host.Children.Add(c)
        win.ShowDialog()
        return result["choice"]
    except Exception:
        return None

class SelectFromList(object):
    """List chooser using SelectFromList.xaml"""
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
            # configure selection mode
            from System.Windows.Controls import SelectionMode
            lb.SelectionMode = SelectionMode.Multiple if multiselect else SelectionMode.Single
            # bind items (convert to strings if needed)
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
                    win.DialogResult = True
                    win.Close()
                ok.Click += _ok
            cancel = getattr(win, "CancelButton", None)
            if cancel is not None:
                def _cancel(sender, e):
                    win.DialogResult = False
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
