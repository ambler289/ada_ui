# -*- coding: utf-8 -*-
"""
ada_ui.forms — XAML-backed dialogs (NameScope-aware)
Exposes: alert, confirm, input_text, big_buttons, SelectFromList.show
"""
from __future__ import annotations
from pathlib import Path

import clr  # type: ignore
clr.AddReference("PresentationFramework")
clr.AddReference("PresentationCore")
clr.AddReference("WindowsBase")

from System import String, Uri, UriKind
from System.IO import StringReader
from System.Windows import Window, ResourceDictionary, MessageBox, MessageBoxButton, MessageBoxResult
from System.Windows.Markup import XamlReader
from System.Windows.Controls import Button, StackPanel, TextBlock, TextBox, ListBox
from System.Windows import Controls

HERE = Path(__file__).resolve().parent

# -------------------- helpers --------------------
def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")

def _parse(xaml_text: str):
    # parse text into a WPF element/dictionary
    return XamlReader.Parse(StringReader(xaml_text).ReadToEnd())

def _merge_theme(win: Window):
    """Load Controls.xaml + Theme.xaml as merged dictionaries (prefer Source URI; fallback to parse)."""
    for name in ("Controls.xaml", "Theme.xaml"):
        path = HERE / name
        if not path.exists():
            continue
        try:
            # Prefer Source; most robust when dictionaries merge others
            rd = ResourceDictionary()
            rd.Source = Uri(path.as_uri(), UriKind.Absolute)
            win.Resources.MergedDictionaries.Add(rd)
        except Exception:
            # Fallback: parse the XAML into a ResourceDictionary directly
            try:
                parsed = _parse(_read(path))
                if isinstance(parsed, ResourceDictionary):
                    win.Resources.MergedDictionaries.Add(parsed)
            except Exception:
                pass

def _load_win(xaml_name: str) -> Window:
    """Return a Window hosting the XAML (wrap UserControl in a Window if needed) and merge theme."""
    xaml_path = HERE / xaml_name
    if not xaml_path.exists():
        raise IOError("Missing XAML: {}".format(xaml_path))
    root = _parse(_read(xaml_path))
    if isinstance(root, Window):
        win = root
        scope = win  # FindName will work on the Window
    else:
        w = Window()
        w.Content = root
        win = w
        # If content is a FrameworkElement, it will host the NameScope for FindName()
        scope = root
    _merge_theme(win)
    # 1 = WidthAndHeight
    win.SizeToContent = 1
    win.Topmost = True
    return win, scope

def _find(scope, name: str):
    """Resolve named element from the root NameScope using FindName, with a tiny fallback search."""
    try:
        if hasattr(scope, "FindName"):
            el = scope.FindName(name)
            if el is not None:
                return el
    except Exception:
        pass
    # Fallback: very small logical walk (rarely needed if FindName is available)
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

        yes = _find(scope, "button_yes")
        no  = _find(scope, "button_no")

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
    """Use ButtonBox.xaml; add a button per label into panel_buttons."""
    try:
        win, scope = _load_win("ButtonBox.xaml")
        try: win.Title = title
        except Exception: pass

        # Optional title/description inside the window, if your XAML has them
        title_tb = _find(scope, "TitleText")
        desc_tb  = _find(scope, "text_message")
        if message and desc_tb is not None:
            desc_tb.Text = String(str(message))

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
                b.Margin = Controls.Thickness(4)
                b.MinWidth = 200
                b.Height = 36
                b.Click += _make(label)
                host.Children.Add(b)

        # Wire up explicit cancel/ok if present
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
