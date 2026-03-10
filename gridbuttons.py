# -*- coding: utf-8 -*-
from __future__ import annotations


def choose_grid_buttons(options, title="Choose", message="", columns=3):
    """
    Compact ADa themed grid button chooser.

    options : list[str]
    columns : number of columns in grid layout
    returns : selected label or None
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
        Grid, Button, TextBlock, Border,
        RowDefinition, ColumnDefinition, StackPanel
    )

    from System.Windows.Media import (  # type: ignore
        SolidColorBrush, Color, LinearGradientBrush,
        GradientStop, GradientStopCollection
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

    opts = [str(x) for x in (options or [])]
    if not opts:
        return None

    columns = max(1, int(columns or 1))

    choice = {"value": None}

    # ------------------------------------------------------------------
    # Window
    # ------------------------------------------------------------------

    win = Window()

    # Python.NET safe WindowStyle.None
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

    # ------------------------------------------------------------------
    # Outer container
    # ------------------------------------------------------------------

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
    root.RowDefinitions.Add(RowDefinition())
    root.RowDefinitions.Add(RowDefinition())
    outer.Child = root

    # ------------------------------------------------------------------
    # Gradient header
    # ------------------------------------------------------------------

    def grad_header():
        g = GradientStopCollection()
        g.Add(GradientStop(ADA_BLUE, 0.0))
        g.Add(GradientStop(ADA_PINK, 1.0))

        brush = LinearGradientBrush()
        brush.GradientStops = g
        return brush

    header = Border()
    header.Background = grad_header()
    header.CornerRadius = CornerRadius(12, 12, 0, 0)
    Grid.SetRow(header, 0)
    root.Children.Add(header)

    header_grid = Grid()
    header_grid.ColumnDefinitions.Add(ColumnDefinition())
    header_grid.ColumnDefinitions.Add(ColumnDefinition())
    header.Child = header_grid

    title_tb = TextBlock()
    title_tb.Text = str(title or "Choose")
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

    def close_click(sender, args):
        win.Close()

    btn_close.Click += close_click
    Grid.SetColumn(btn_close, 1)
    header_grid.Children.Add(btn_close)

    # Drag window from header
    def drag(sender, e):
        if e.LeftButton == MouseButtonState.Pressed:
            try:
                win.DragMove()
            except Exception:
                pass

    header.MouseLeftButtonDown += drag

    # ------------------------------------------------------------------
    # Body
    # ------------------------------------------------------------------

    body = Border()
    body.Margin = Thickness(24, 20, 24, 24)
    Grid.SetRow(body, 1)
    root.Children.Add(body)

    stack = StackPanel()
    body.Child = stack

    if message:
        msg = TextBlock()
        msg.Text = str(message)
        msg.Margin = Thickness(0, 0, 0, 12)
        msg.Foreground = SolidColorBrush(FG_LIGHT)
        msg.FontSize = 16
        stack.Children.Add(msg)

    grid = Grid()
    stack.Children.Add(grid)

    rows = (len(opts) + columns - 1) // columns

    for _ in range(rows):
        grid.RowDefinitions.Add(RowDefinition())

    for _ in range(columns):
        grid.ColumnDefinitions.Add(ColumnDefinition())

    # ------------------------------------------------------------------
    # Buttons
    # ------------------------------------------------------------------

    def make_btn(label):
        b = Button()
        b.Content = label
        b.Margin = Thickness(6)
        b.MinWidth = 120
        b.Height = 40
        b.Background = SolidColorBrush(ADA_BLUE)
        b.Foreground = SolidColorBrush(Color.FromRgb(255, 255, 255))
        b.BorderThickness = Thickness(0)
        b.HorizontalAlignment = HorizontalAlignment.Stretch

        def click(sender, args):
            choice["value"] = label
            win.Close()

        b.Click += click
        return b

    for i, label in enumerate(opts):
        r = i // columns
        c = i % columns

        btn = make_btn(label)
        Grid.SetRow(btn, r)
        Grid.SetColumn(btn, c)
        grid.Children.Add(btn)

    win.ShowDialog()

    return choice["value"]