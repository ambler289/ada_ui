# -*- coding: utf-8 -*-
from __future__ import annotations


def bulk_parameter_editor(parameters, title="Set Parameter", message="Choose parameter and value"):
    """
    Simple ADa bulk parameter editor.

    parameters : list[str]
    returns : dict | None

    {
        "parameter": "...",
        "value": "..."
    }
    """

    from .pickers import pick_one
    from .inputs import ask_string

    if not parameters:
        return None

    parameter = pick_one(
        parameters,
        title=title,
        prompt=message
    )

    if not parameter:
        return None

    value = ask_string(
        prompt="Enter value for '{}'".format(parameter),
        title=title,
        default=""
    )

    if value is None:
        return None

    return {
        "parameter": parameter,
        "value": value
    }


def bulk_parameter_table_editor(rows, title="Edit Parameters (Bulk)"):
    """
    ADa table-style bulk parameter editor.

    rows : list[dict]
        Each row supports:
        {
            "parameter": "Name",
            "current": "Current value",
            "new_value": "Editable value" or bool,
            "unit": "mm",
            "kind": "text" | "bool"
        }

    returns : list[dict] | None
        Returns updated rows on OK, None on cancel.
    """

    import clr  # type: ignore
    clr.AddReference("PresentationFramework")
    clr.AddReference("PresentationCore")
    clr.AddReference("WindowsBase")

    from System.Windows import (  # type: ignore
        Window, WindowStartupLocation, Thickness, SizeToContent,
        HorizontalAlignment, VerticalAlignment, ResizeMode, WindowStyle
    )
    from System.Windows.Controls import (  # type: ignore
        Grid, Button, TextBlock, Border, StackPanel, ScrollViewer,
        RowDefinition, ColumnDefinition, TextBox, CheckBox
    )
    from System.Windows.Media import (  # type: ignore
        SolidColorBrush, LinearGradientBrush, GradientStop,
        GradientStopCollection, Color
    )
    from System.Windows import CornerRadius  # type: ignore
    from System.Windows.Input import MouseButtonState  # type: ignore

    try:
        from System.Windows.Media.Effects import DropShadowEffect  # type: ignore
    except Exception:
        DropShadowEffect = None

    ADA_BLUE = Color.FromRgb(0x5C, 0x7C, 0xFA)
    ADA_PINK = Color.FromRgb(0xF7, 0x59, 0xC0)
    BG_DARK = Color.FromRgb(0x1F, 0x23, 0x2B)
    FG_LIGHT = Color.FromRgb(0xE8, 0xEA, 0xED)

    data_rows = list(rows or [])
    if not data_rows:
        return None

    result = {"ok": False}

    def _grad_header():
        g = GradientStopCollection()
        g.Add(GradientStop(ADA_BLUE, 0.0))
        g.Add(GradientStop(ADA_PINK, 1.0))
        brush = LinearGradientBrush()
        brush.GradientStops = g
        return brush

    win = Window()

    try:
        win.WindowStyle = getattr(WindowStyle, "None")
    except Exception:
        try:
            win.WindowStyle = getattr(WindowStyle, "None_")
        except Exception:
            pass

    win.ResizeMode = ResizeMode.NoResize
    win.AllowsTransparency = True
    win.ShowInTaskbar = False
    win.Title = ""
    win.Background = SolidColorBrush(Color.FromArgb(0, 0, 0, 0))
    win.WindowStartupLocation = WindowStartupLocation.CenterScreen
    win.SizeToContent = SizeToContent.WidthAndHeight

    outer = Border()
    outer.Background = SolidColorBrush(BG_DARK)
    outer.CornerRadius = CornerRadius(12)
    outer.Padding = Thickness(0)

    if DropShadowEffect:
        try:
            shadow = DropShadowEffect()
            shadow.BlurRadius = 20
            shadow.Opacity = 0.35
            shadow.Direction = 270
            shadow.ShadowDepth = 0
            outer.Effect = shadow
        except Exception:
            pass

    win.Content = outer

    root = Grid()
    root.RowDefinitions.Add(RowDefinition())  # header
    root.RowDefinitions.Add(RowDefinition())  # body
    root.RowDefinitions.Add(RowDefinition())  # footer
    outer.Child = root

    # ---------------- Header ----------------
    header = Border()
    header.Background = _grad_header()
    header.CornerRadius = CornerRadius(12, 12, 0, 0)
    Grid.SetRow(header, 0)
    root.Children.Add(header)

    header_grid = Grid()
    header_grid.ColumnDefinitions.Add(ColumnDefinition())
    header_grid.ColumnDefinitions.Add(ColumnDefinition())
    header.Child = header_grid

    title_tb = TextBlock()
    title_tb.Text = str(title or "Edit Parameters (Bulk)")
    title_tb.Margin = Thickness(20, 14, 20, 14)
    title_tb.Foreground = SolidColorBrush(FG_LIGHT)
    title_tb.FontSize = 22
    title_tb.VerticalAlignment = VerticalAlignment.Center
    header_grid.Children.Add(title_tb)

    btn_close = Button()
    btn_close.Content = "✕"
    btn_close.Width = 36
    btn_close.Height = 28
    btn_close.Margin = Thickness(0, 10, 10, 10)
    btn_close.HorizontalAlignment = HorizontalAlignment.Right
    btn_close.VerticalAlignment = VerticalAlignment.Center
    btn_close.Background = SolidColorBrush(ADA_PINK)
    btn_close.Foreground = SolidColorBrush(Color.FromRgb(255, 255, 255))
    btn_close.BorderThickness = Thickness(0)

    def _close(sender, args):
        win.Close()

    btn_close.Click += _close
    Grid.SetColumn(btn_close, 1)
    header_grid.Children.Add(btn_close)

    def _drag(sender, e):
        if e.LeftButton == MouseButtonState.Pressed:
            try:
                win.DragMove()
            except Exception:
                pass

    header.MouseLeftButtonDown += _drag

    # ---------------- Body ----------------
    body = Border()
    body.Margin = Thickness(24, 18, 24, 10)
    Grid.SetRow(body, 1)
    root.Children.Add(body)

    body_stack = StackPanel()
    body.Child = body_stack

    # Column headers
    labels_grid = Grid()
    labels_grid.ColumnDefinitions.Add(ColumnDefinition())  # Parameter
    labels_grid.ColumnDefinitions.Add(ColumnDefinition())  # Current
    labels_grid.ColumnDefinitions.Add(ColumnDefinition())  # New Value
    labels_grid.ColumnDefinitions.Add(ColumnDefinition())  # Unit
    body_stack.Children.Add(labels_grid)

    def _mk_header(text, col):
        tb = TextBlock()
        tb.Text = text
        tb.Foreground = SolidColorBrush(FG_LIGHT)
        tb.FontSize = 14
        tb.Margin = Thickness(4, 0, 12, 8)
        Grid.SetColumn(tb, col)
        labels_grid.Children.Add(tb)

    _mk_header("Parameter", 0)
    _mk_header("Current", 1)
    _mk_header("New Value", 2)
    _mk_header("Unit", 3)

    scroller = ScrollViewer()
    scroller.Height = 360
    body_stack.Children.Add(scroller)

    table = Grid()
    table.ColumnDefinitions.Add(ColumnDefinition())  # Parameter
    table.ColumnDefinitions.Add(ColumnDefinition())  # Current
    table.ColumnDefinitions.Add(ColumnDefinition())  # New Value
    table.ColumnDefinitions.Add(ColumnDefinition())  # Unit
    scroller.Content = table

    editors = []

    for row_idx, row in enumerate(data_rows):
        table.RowDefinitions.Add(RowDefinition())

        param_name = str(row.get("parameter", ""))
        current_val = str(row.get("current", ""))
        new_val = row.get("new_value", "")
        unit_val = str(row.get("unit", ""))
        kind = str(row.get("kind", "text")).lower()

        # Parameter
        tb_param = TextBlock()
        tb_param.Text = param_name
        tb_param.Foreground = SolidColorBrush(FG_LIGHT)
        tb_param.FontSize = 13
        tb_param.Margin = Thickness(4, 4, 12, 8)
        Grid.SetRow(tb_param, row_idx)
        Grid.SetColumn(tb_param, 0)
        table.Children.Add(tb_param)

        # Current
        tb_current = TextBlock()
        tb_current.Text = current_val
        tb_current.Foreground = SolidColorBrush(FG_LIGHT)
        tb_current.FontSize = 13
        tb_current.Margin = Thickness(4, 4, 12, 8)
        Grid.SetRow(tb_current, row_idx)
        Grid.SetColumn(tb_current, 1)
        table.Children.Add(tb_current)

        # New Value editor
        if kind == "bool":
            editor = CheckBox()
            try:
                editor.IsChecked = bool(new_val)
            except Exception:
                editor.IsChecked = False
            editor.Margin = Thickness(4, 4, 12, 8)
        else:
            editor = TextBox()
            editor.Text = str(new_val)
            editor.Height = 30
            editor.Margin = Thickness(4, 0, 12, 8)

        Grid.SetRow(editor, row_idx)
        Grid.SetColumn(editor, 2)
        table.Children.Add(editor)

        # Unit
        tb_unit = TextBlock()
        tb_unit.Text = unit_val
        tb_unit.Foreground = SolidColorBrush(FG_LIGHT)
        tb_unit.FontSize = 13
        tb_unit.Margin = Thickness(4, 4, 4, 8)
        Grid.SetRow(tb_unit, row_idx)
        Grid.SetColumn(tb_unit, 3)
        table.Children.Add(tb_unit)

        editors.append((row, editor, kind))

    # ---------------- Footer ----------------
    footer = Border()
    footer.Margin = Thickness(24, 0, 24, 18)
    Grid.SetRow(footer, 2)
    root.Children.Add(footer)

    footer_panel = StackPanel()
    footer_panel.Orientation = 0  # Horizontal
    footer_panel.HorizontalAlignment = HorizontalAlignment.Right
    footer.Child = footer_panel

    def _mk_btn(label, primary=False):
        b = Button()
        b.Content = label
        b.Width = 140
        b.Height = 36
        b.Margin = Thickness(8, 0, 0, 0)
        b.BorderThickness = Thickness(0)
        b.Background = SolidColorBrush(ADA_BLUE if primary else ADA_PINK)
        b.Foreground = SolidColorBrush(Color.FromRgb(255, 255, 255))
        return b

    btn_ok = _mk_btn("OK", True)
    btn_cancel = _mk_btn("Cancel", False)
    footer_panel.Children.Add(btn_ok)
    footer_panel.Children.Add(btn_cancel)

    def _ok(sender, args):
        for row, editor, kind in editors:
            if kind == "bool":
                row["new_value"] = bool(getattr(editor, "IsChecked", False))
            else:
                row["new_value"] = str(getattr(editor, "Text", ""))

        result["ok"] = True
        win.Close()

    def _cancel(sender, args):
        win.Close()

    btn_ok.Click += _ok
    btn_cancel.Click += _cancel

    win.ShowDialog()

    if result["ok"]:
        return data_rows
    return None