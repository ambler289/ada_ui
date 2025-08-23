# -*- coding: utf-8 -*-
"""
ada_ui.forms — NameScope-aware + robust host handling for ButtonBox
- Resolves XAML parts via FindName (NameScope-aware)
- Adds buttons to panel host via Children/Items/Content fallback
- Parses Controls.xaml & Theme.xaml as ResourceDictionaries and merges
"""
from __future__ import annotations
from pathlib import Path

import clr  # type: ignore
clr.AddReference("PresentationFramework")
clr.AddReference("PresentationCore")
clr.AddReference("WindowsBase")

from System import String
from System.IO import StringReader
from System.Windows import Window, ResourceDictionary, MessageBox, MessageBoxButton, MessageBoxResult
from System.Windows.Markup import XamlReader
from System.Windows.Controls import Button, StackPanel, TextBlock, TextBox, ListBox
from System.Windows import Controls

__ada_ui_forms_marker__ = "FindName_FIX_3"

HERE = Path(__file__).resolve().parent

# -------------------- helpers --------------------
def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")

def _parse(xaml_text: str):
    return XamlReader.Parse(StringReader(xaml_text).ReadToEnd())

def _merge_theme(win: Window):
    for name in ("Controls.xaml", "Theme.xaml"):
        p = HERE / name
        if not p.exists():
            continue
        try:
            parsed = _parse(_read(p))
            if isinstance(parsed, ResourceDictionary):
                win.Resources.MergedDictionaries.Add(parsed)
        except Exception:
            pass

def _load_win(xaml_name: str):
    xaml_path = HERE / xaml_name
    if not xaml_path.exists():
        raise IOError("Missing XAML: {}".format(xaml_path))
    root = _parse(_read(xaml_path))
    if isinstance(root, Window):
        win = root; scope = win
    else:
        w = Window(); w.Content = root; win = w; scope = root

    _merge_theme(win)

    # >>> visibility guard must run BEFORE the return <<<
    try:
        # If XAML sets AllowsTransparency=True and Background is Transparent/None,
        # the window can be invisible. Make it visible.
        if hasattr(win, "AllowsTransparency") and bool(win.AllowsTransparency):
            from System.Windows.Media import Brushes
            bg = win.Background
            if bg is None or str(bg) in ("Transparent", "#00FFFFFF"):
                win.AllowsTransparency = False
                win.Background = Brushes.White
    except Exception:
        pass
    # <<< end guard >>>

    win.SizeToContent = 1  # WidthAndHeight
    win.Topmost = True
    return win, scope


def _find(scope, name: str):
    try:
        if hasattr(scope, "FindName"):
            el = scope.FindName(name)
            if el is not None:
                return el
    except Exception:
        pass
    try:
        from System.Windows import LogicalTreeHelper as LTH
        q = [scope]
        while q:
            n = q.pop(0)
            try:
                if getattr(n, "Name", None) == name:
                    return n
                for c in LTH.GetChildren(n):
                    q.append(c)
            except Exception:
                pass
    except Exception:
        pass
    return None

def _host_add_child(host, child):
    # Panels -> Children
    if hasattr(host, "Children"):
        try:
            host.Children.Add(child); return True
        except Exception: pass
    # ItemsControls -> Items
    if hasattr(host, "Items"):
        try:
            host.Items.Add(child); return True
        except Exception: pass
    # ContentControls -> Content
    if hasattr(host, "Content"):
        try:
            sp = StackPanel()
            sp.Children.Add(child)
            host.Content = sp
            return True
        except Exception: pass
    return False

# -------------------- public API --------------------
def alert(message, title="Message"):
    try:
        win, scope = _load_win("Alert.xaml")
        try: win.Title = title
        except Exception: pass

        tb = _find(scope, "text_message")
        if tb is not None:
            tb.Text = String(str(message))

        ok = _find(scope, "button_ok")
        cancel = _find(scope, "button_cancel")

        if ok is not None:
            def _ok(sender, e):
                try: win.DialogResult = True
                except Exception: pass
                win.Close()
            ok.Click += _ok

        if cancel is not None:
            def _cancel(sender, e):
                try: win.DialogResult = False
                except Exception: pass
                win.Close()
            cancel.Click += _cancel

        win.ShowDialog()
    except Exception:
        MessageBox.Show(str(message), str(title))

def confirm(message, title="Confirm", ok_text="Yes", cancel_text="No"):
    try:
        win, scope = _load_win("Confirm.xaml")
        try: win.Title = title
        except Exception: pass

        tb = _find(scope, "text_message")
        if tb is not None:
            tb.Text = String(str(message))

        yes = _find(scope, "button_yes") or _find(scope, "button_ok")
        no  = _find(scope, "button_no")  or _find(scope, "button_cancel")

        if yes is not None:
            try: yes.Content = ok_text
            except Exception: pass
            def _yes(sender, e):
                try: win.DialogResult = True
                except Exception: pass
                win.Close()
            yes.Click += _yes

        if no is not None:
            try: no.Content = cancel_text
            except Exception: pass
            def _no(sender, e):
                try: win.DialogResult = False
                except Exception: pass
                win.Close()
            no.Click += _no

        rv = win.ShowDialog()
        return bool(rv)
    except Exception:
        res = MessageBox.Show(str(message), str(title), MessageBoxButton.OKCancel)
        return res == MessageBoxResult.OK

def input_text(prompt="Enter text", title="Input"):
    try:
        win, scope = _load_win("InputText.xaml")
        try: win.Title = title
        except Exception: pass

        prompt_tb = _find(scope, "text_prompt")
        if prompt_tb is not None:
            prompt_tb.Text = String(str(prompt))

        box = _find(scope, "text_input")
        result = {"text": None}

        ok = _find(scope, "button_ok")
        cancel = _find(scope, "button_cancel")

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
    """Create large option buttons from ButtonBox.xaml"""
    try:
        win, scope = _load_win("ButtonBox.xaml")
        try: win.Title = title
        except Exception: pass

        title_tb = _find(scope, "TitleText")
        if message and title_tb is not None:
            try:
                existing = getattr(title_tb, "Text", "") or ""
                sep = "\n" if existing else ""
                title_tb.Text = String(str(existing) + sep + str(message))
            except Exception:
                pass

        host = _find(scope, "panel_buttons")
        result = {"choice": None}

        def _make(label):
            def _click(sender, e):
                result["choice"] = label
                try: win.DialogResult = True
                except Exception: pass
                win.Close()
            return _click

        if host is not None:
            for label in items:
                b = Button()
                b.Content = String(str(label))
                b.Margin = Controls.Thickness(6)
                b.MinWidth = 220
                b.Height = 36
                b.Click += _make(label)
                _host_add_child(host, b)

        cancel_btn = _find(scope, "button_cancel")
        ok_btn     = _find(scope, "button_ok")

        if cancel and cancel_btn is not None:
            def _cancel(sender, e):
                result["choice"] = None
                try: win.DialogResult = False
                except Exception: pass
                win.Close()
            cancel_btn.Click += _cancel

        if ok_btn is not None:
            def _ok(sender, e):
                if result["choice"] is None and items:
                    result["choice"] = items[0]
                try: win.DialogResult = True
                except Exception: pass
                win.Close()
            ok_btn.Click += _ok

        win.ShowDialog()
        return result["choice"]
    except Exception:
        return None

class SelectFromList(object):
    @staticmethod
    def show(items, title="Select", name_attr=None, button_name="OK", multiselect=False):
        try:
            win, scope = _load_win("SelectFromList.xaml")
            try: win.Title = title
            except Exception: pass

            lb = _find(scope, "list_items")
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

            result = {"sel": None, "selm": []}

            ok = _find(scope, "button_ok")
            cancel = _find(scope, "button_cancel")

            if ok is not None:
                try: ok.Content = button_name
                except Exception: pass
                def _ok(sender, e):
                    if multiselect:
                        result["selm"] = [lb.Items[i] for i in range(lb.Items.Count) if lb.SelectedItems.Contains(lb.Items[i])]
                    else:
                        result["sel"] = lb.SelectedItem
                    try: win.DialogResult = True
                    except Exception: pass
                    win.Close()
                ok.Click += _ok

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
                labels = [str(x) for x in items]
                selected = [str(x) for x in result["selm"]]
                return [items[labels.index(s)] for s in selected if s in labels]
            else:
                if result["sel"] is None:
                    return None
                lbl = str(result["sel"])
                labels = [str(x) for x in items]
                return items[labels.index(lbl)] if lbl in labels else None
        except Exception:
            return None
