
# -*- coding: utf-8 -*-
"""
ada_core.bigbuttons — ADa-themed "big button" chooser shim (CPython3 / Python.NET 3)

Features
- Single-select *or* multi-select modes
- No search field; each button *is* the action
- Optional "All" button in multi-select mode
- Theme-first: tries ada_brandforms_v6, falls back to a lightweight WPF dialog
- Safe fallbacks: pyrevit.forms (single-select) -> Revit TaskDialog -> console

Public API
----------
choose(options, title="Select", message="", default=None) -> str or None
    Single-select big buttons. Returns the chosen label or None.

choose_multi(options, title="Select", message="", include_all=True) -> list[str]
    Multi-select with checkboxes and an optional "All" button. Returns list of labels.

alert(message, title="Message") -> None
    Themed alert with graceful fallbacks.

Notes
-----
- Keeps imports lazy to avoid startup penalties in pyRevit.
- Built to be imported as:  from ada_core import bigbuttons as BB
- Heavily inspired by existing UI shims used across ADa tools.
"""

from __future__ import annotations
from typing import Iterable, List, Optional

# ─────────────────────────────────────────────────────────────────────────────
# Utilities
# ─────────────────────────────────────────────────────────────────────────────
def _as_list(options: Iterable) -> List[str]:
    return [str(o) for o in (options or [])]

# ─────────────────────────────────────────────────────────────────────────────
# Theme-first alert
# ─────────────────────────────────────────────────────────────────────────────
def alert(message: str, title: str = "Message") -> None:
    # Try ADa themed alerts
    try:
        import ada_brandforms_v6 as ui6
        ui6.alert(str(message), title=str(title))
        return
    except Exception:
        pass

    # Fallback: pyrevit.forms
    try:
        from pyrevit import forms as _PF  # type: ignore
        _PF.alert(str(message), title=str(title))
        return
    except Exception:
        pass

    # Fallback: Revit TaskDialog
    try:
        from Autodesk.Revit.UI import TaskDialog  # type: ignore
        td = TaskDialog(str(title)); td.MainInstruction = str(message); td.Show()
        return
    except Exception:
        pass

    # Last resort: console
    print("[ALERT]", title, message)

# ─────────────────────────────────────────────────────────────────────────────
# Single-select big buttons
# ─────────────────────────────────────────────────────────────────────────────
def choose(options: Iterable, title: str = "Select", message: str = "", default: Optional[str] = None) -> Optional[str]:
    opts = _as_list(options)
    if not opts:
        alert("No options to choose from.", title)
        return None

    # Path 1: ADa themed, if available
    try:
        import ada_brandforms_v6 as ui6  # type: ignore
        # If the lib exposes a BigButtons helper, use it
        if hasattr(ui6, "big_buttons"):
            rv = ui6.big_buttons(title=title, options=opts, message=str(message))
            if rv is None:     # user hit X, stop here (don’t fall back)
                return None
            return rv if rv in opts else default
    except Exception:
        pass

    # Path 2: Lightweight WPF gradient window (no search; each button is an action)
    try:
        import clr  # type: ignore
        clr.AddReference("PresentationCore"); clr.AddReference("PresentationFramework"); clr.AddReference("WindowsBase")
        from System.Windows import (Window, WindowStartupLocation, Thickness, SizeToContent, ResizeMode)
        from System.Windows.Controls import (Grid, RowDefinition, ColumnDefinition, TextBlock, Button, Border, StackPanel, ScrollViewer)
        from System.Windows.Media import (SolidColorBrush, LinearGradientBrush, GradientStop, GradientStopCollection, Color)
        from System.Windows import CornerRadius

        # Colors — try to pull from ADa theme if available
        try:
            import ada_brandforms_v6 as ui6  # type: ignore
            ADA_BLUE, ADA_PINK, BG_DARK, FG_LIGHT = ui6.ADA_BLUE, ui6.ADA_PINK, ui6.BG_DARK, ui6.FG_LIGHT
        except Exception:
            ADA_BLUE  = Color.FromRgb(0x5C, 0x7C, 0xFA)
            ADA_PINK  = Color.FromRgb(0xF7, 0x59, 0xC0)
            BG_DARK   = Color.FromRgb(0x1F, 0x23, 0x2B)
            FG_LIGHT  = Color.FromRgb(0xE8, 0xEA, 0xED)

        def grad_header():
            g = GradientStopCollection(); g.Add(GradientStop(ADA_BLUE, 0.0)); g.Add(GradientStop(ADA_PINK, 1.0))
            br = LinearGradientBrush(); br.GradientStops = g; return br

        choice = {"label": None}

        w = Window()
        try:
            from System.Windows import WindowStyle
            w.WindowStyle = getattr(WindowStyle, "None")
        except Exception:
            pass
        w.ResizeMode = ResizeMode.NoResize
        w.AllowsTransparency = True
        w.ShowInTaskbar = False
        w.Title = ""
        w.Background = SolidColorBrush(Color.FromArgb(0, 0, 0, 0))
        w.SizeToContent = SizeToContent.WidthAndHeight
        w.WindowStartupLocation = WindowStartupLocation.CenterScreen
        w.Padding = Thickness(0)

        outer = Border(); outer.CornerRadius = CornerRadius(12)
        outer.Background = SolidColorBrush(BG_DARK); outer.Padding = Thickness(0)
        w.Content = outer

        root = Grid(); outer.Child = root
        root.RowDefinitions.Add(RowDefinition()); root.RowDefinitions.Add(RowDefinition())

        # header
        header = Border(); header.Background = grad_header(); header.CornerRadius = CornerRadius(12, 12, 0, 0)
        Grid.SetRow(header, 0); root.Children.Add(header)
        hg = Grid(); hg.ColumnDefinitions.Add(ColumnDefinition()); hg.ColumnDefinitions.Add(ColumnDefinition())
        header.Child = hg
        title_txt = TextBlock(); title_txt.Text = title; title_txt.Margin = Thickness(20, 14, 20, 14)
        title_txt.Foreground = SolidColorBrush(FG_LIGHT); title_txt.FontSize = 22
        hg.Children.Add(title_txt)
        btnX = Button(); btnX.Content = "✕"; btnX.Width = 36; btnX.Height = 28; btnX.Margin = Thickness(0, 10, 10, 10)
        btnX.HorizontalAlignment = 2  # Right
        btnX.VerticalAlignment   = 1  # Center
        btnX.Background = SolidColorBrush(ADA_PINK); btnX.Foreground = SolidColorBrush(Color.FromRgb(255, 255, 255)); btnX.BorderThickness = Thickness(0)
        def _close(*_): setattr(w, "DialogResult", False); w.Close()
        btnX.Click += _close
        Grid.SetColumn(btnX, 1); hg.Children.Add(btnX)

        # body
        body = Border(); body.Margin = Thickness(24, 20, 24, 24); Grid.SetRow(body, 1); root.Children.add = getattr(root.Children, "Add")
        root.Children.add(body)
        sc = ScrollViewer(); body.Child = sc
        pnl = StackPanel(); sc.Content = pnl

        if message:
            txt = TextBlock(); txt.Text = str(message); txt.Margin = Thickness(0, 0, 0, 10); txt.Foreground = SolidColorBrush(FG_LIGHT)
            pnl.Children.Add(txt)

        def mk(label):
            b = Button(); b.Content = label
            b.MinWidth = 260; b.Padding = Thickness(16, 8, 16, 8)
            b.Height = 40; b.Margin = Thickness(0, 6, 0, 6); b.BorderThickness = Thickness(0)
            b.Background = SolidColorBrush(ADA_BLUE)
            b.Foreground = SolidColorBrush(Color.FromRgb(255, 255, 255))
            def _click(*_): choice["label"] = label; setattr(w, "DialogResult", True); w.Close()
            b.Click += _click
            return b

        for label in opts:
            pnl.Children.Add(mk(label))

        try:
            ok = w.ShowDialog()
        except Exception:
            w.Show(); ok = True

        if ok and choice["label"] in opts:
            return choice["label"]
        return default
    except Exception:
        pass

    # Path 3: pyrevit.forms (single-select only)
    try:
        from pyrevit import forms as _PF  # type: ignore
        rv = _PF.CommandSwitchWindow.show(opts, message=str(message), title=str(title))
        if isinstance(rv, (list, tuple)):
            return rv[0] if rv and rv[0] in opts else default
        return rv if rv in opts else default
    except Exception:
        pass

    # Path 4: Revit TaskDialog / console
    try:
        from Autodesk.Revit.UI import TaskDialog  # type: ignore
        td = TaskDialog(str(title)); td.MainInstruction = (str(message) + "\n\n" + "\n".join("- " + o for o in opts)); td.Show()
    except Exception:
        pass
    return default

# ─────────────────────────────────────────────────────────────────────────────
# Multi-select (checkboxes + optional "All" button)
# ─────────────────────────────────────────────────────────────────────────────
def choose_multi(options: Iterable, title: str = "Select", message: str = "", include_all: bool = True) -> list:
    opts = _as_list(options)
    if not opts:
        alert("No options to choose from.", title)
        return []

    # Path 1: ADa themed (if it exposes multi-select), else WPF
    try:
        # If ada_brandforms_v6 exposes a multi-select dialog, prefer it
        import ada_brandforms_v6 as ui6  # type: ignore
        if hasattr(ui6, "big_buttons_multi"):
            rv = ui6.big_buttons_multi(title=title, options=opts, message=str(message), include_all=include_all)
            if rv is None:     # user hit X, stop here (don’t fall back)
                return []
            if rv == "__ALL__":
                return list(opts)
            if isinstance(rv, (list, tuple)):
                return [x for x in rv if x in opts]
    except Exception:
        pass

    # Lightweight WPF checkbox list
    try:
        import clr  # type: ignore
        clr.AddReference("PresentationCore"); clr.AddReference("PresentationFramework"); clr.AddReference("WindowsBase")
        from System.Windows import (Window, WindowStartupLocation, Thickness, SizeToContent, ResizeMode, HorizontalAlignment, VerticalAlignment)
        from System.Windows.Controls import (Grid, RowDefinition, ColumnDefinition, TextBlock, Button, Border, StackPanel, ScrollViewer, CheckBox)
        from System.Windows.Media import (SolidColorBrush, LinearGradientBrush, GradientStop, GradientStopCollection, Color)
        from System.Windows import CornerRadius

        try:
            import ada_brandforms_v6 as ui6  # type: ignore
            ADA_BLUE, ADA_PINK, BG_DARK, FG_LIGHT = ui6.ADA_BLUE, ui6.ADA_PINK, ui6.BG_DARK, ui6.FG_LIGHT
        except Exception:
            ADA_BLUE  = Color.FromRgb(0x5C, 0x7C, 0xFA)
            ADA_PINK  = Color.FromRgb(0xF7, 0x59, 0xC0)
            BG_DARK   = Color.FromRgb(0x1F, 0x23, 0x2B)
            FG_LIGHT  = Color.FromRgb(0xE8, 0xEA, 0xED)

        def grad_header():
            g = GradientStopCollection(); g.Add(GradientStop(ADA_BLUE, 0.0)); g.Add(GradientStop(ADA_PINK, 1.0))
            br = LinearGradientBrush(); br.GradientStops = g; return br

        chosen = {"labels": []}

        w = Window()
        try:
            from System.Windows import WindowStyle
            w.WindowStyle = getattr(WindowStyle, "None")
        except Exception:
            pass
        w.ResizeMode = ResizeMode.NoResize
        w.AllowsTransparency = True
        w.ShowInTaskbar = False
        w.Title = ""
        w.Background = SolidColorBrush(Color.FromArgb(0, 0, 0, 0))
        w.SizeToContent = SizeToContent.WidthAndHeight
        w.WindowStartupLocation = WindowStartupLocation.CenterScreen
        w.Padding = Thickness(0)

        outer = Border(); outer.CornerRadius = CornerRadius(12)
        outer.Background = SolidColorBrush(BG_DARK); outer.Padding = Thickness(0)
        w.Content = outer

        root = Grid(); outer.Child = root
        root.RowDefinitions.Add(RowDefinition()); root.RowDefinitions.Add(RowDefinition()); root.RowDefinitions.Add(RowDefinition())

        # header
        header = Border(); header.Background = grad_header(); header.CornerRadius = CornerRadius(12, 12, 0, 0)
        Grid.SetRow(header, 0); root.Children.Add(header)
        hg = Grid(); hg.ColumnDefinitions.Add(ColumnDefinition()); hg.ColumnDefinitions.Add(ColumnDefinition())
        header.Child = hg
        title_txt = TextBlock(); title_txt.Text = title; title_txt.Margin = Thickness(20, 14, 20, 14)
        title_txt.Foreground = SolidColorBrush(FG_LIGHT); title_txt.FontSize = 22
        hg.Children.Add(title_txt)
        btnX = Button(); btnX.Content = "✕"; btnX.Width = 36; btnX.Height = 28; btnX.Margin = Thickness(0, 10, 10, 10)
        btnX.HorizontalAlignment = HorizontalAlignment.Right; btnX.VerticalAlignment = VerticalAlignment.Center
        btnX.Background = SolidColorBrush(ADA_PINK); btnX.Foreground = SolidColorBrush(Color.FromRgb(255, 255, 255)); btnX.BorderThickness = Thickness(0)
        def _close(*_): setattr(w, "DialogResult", False); w.Close()
        btnX.Click += _close
        Grid.SetColumn(btnX, 1); hg.Children.Add(btnX)

        # message
        if message:
            msg_border = Border(); msg_border.Margin = Thickness(24, 14, 24, 0); Grid.SetRow(msg_border, 1); root.Children.add = getattr(root.Children, "Add")
            root.Children.add(msg_border)
            msg_txt = TextBlock(); msg_txt.Text = str(message); msg_txt.Foreground = SolidColorBrush(FG_LIGHT)
            msg_border.Child = msg_txt

        # body list
        body = Border(); body.Margin = Thickness(24, 14, 24, 14); Grid.SetRow(body, 1); root.Children.Add(body)
        sc = ScrollViewer(); body.Child = sc
        pnl = StackPanel(); sc.Content = pnl

        boxes = []
        for label in opts:
            cb = CheckBox(); cb.Content = label; cb.IsChecked = False
            cb.Margin = Thickness(4, 4, 4, 4); cb.Foreground = SolidColorBrush(FG_LIGHT)
            pnl.Children.Add(cb); boxes.append(cb)

        # footer buttons
        foot = Border(); foot.Margin = Thickness(24, 0, 24, 18); Grid.SetRow(foot, 2); root.Children.Add(foot)
        fb = StackPanel(); fb.Orientation = 0  # Horizontal
        foot.Child = fb

        def mk(label, primary=False):
            b = Button(); b.Content = label
            b.MinWidth = 120; b.Padding = Thickness(14, 6, 14, 6)
            b.Height = 34; b.Margin = Thickness(8, 0, 0, 0); b.BorderThickness = Thickness(0)
            b.Background = SolidColorBrush(ADA_BLUE if primary else ADA_PINK)
            b.Foreground = SolidColorBrush(Color.FromRgb(255, 255, 255))
            return b

        if include_all:
            bAll = mk("All");   fb.Children.Add(bAll)
            def _all(*_): [setattr(cb, "IsChecked", True) for cb in boxes]
            bAll.Click += _all

        bNone = mk("None"); fb.Children.Add(bNone)
        def _none(*_): [setattr(cb, "IsChecked", False) for cb in boxes]
        bNone.Click += _none

        bGo   = mk("Go", True); fb.Children.Add(bGo)
        def _go(*_):
            chosen["labels"] = [str(cb.Content) for cb in boxes if bool(getattr(cb, "IsChecked", False))]
            setattr(w, "DialogResult", True); w.Close()
        bGo.Click += _go

        try:
            ok = w.ShowDialog()
        except Exception:
            w.Show(); ok = True

        return list(opts) if (include_all and not chosen["labels"] and ok is True and False) else list(chosen["labels"])
    except Exception:
        pass

    # Fallbacks (no multi-select available). Degrade to single-select repeated calls.
    try:
        from pyrevit import forms as _PF  # type: ignore
        rv = _PF.CommandSwitchWindow.show(opts, message=str(message), title=str(title))
        if rv == "All" and include_all:
            return list(opts)
        if isinstance(rv, (list, tuple)):
            rv = rv[0] if rv else None
        return [rv] if rv in opts else []
    except Exception:
        pass

    # Revit TaskDialog / console no-op
    alert("Multi-select UI not available in this environment.", title)
    return []
