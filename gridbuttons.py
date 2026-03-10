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
        HorizontalAlignment, ResizeMode
    )
    from System.Windows.Controls import (  # type: ignore
        Grid, Button, TextBlock, Border, RowDefinition, ColumnDefinition
    )
    from System.Windows.Media import (  # type: ignore
        SolidColorBrush, Color
    )
    from System.Windows import CornerRadius  # type: ignore

    ADA_BLUE = Color.FromRgb(0x5C, 0x7C, 0xFA)
    BG_DARK = Color.FromRgb(0x1F, 0x23, 0x2B)
    FG_LIGHT = Color.FromRgb(0xE8, 0xEA, 0xED)

    opts = [str(x) for x in (options or [])]
    if not opts:
        return None

    columns = max(1, int(columns or 1))

    choice = {"value": None}

    win = Window()
    win.Title = str(title or "Choose")
    win.WindowStartupLocation = WindowStartupLocation.CenterScreen
    win.SizeToContent = SizeToContent.WidthAndHeight
    win.ResizeMode = ResizeMode.NoResize

    outer = Border()
    outer.Background = SolidColorBrush(BG_DARK)
    outer.CornerRadius = CornerRadius(10)
    outer.Padding = Thickness(20)

    root = Grid()
    root.RowDefinitions.Add(RowDefinition())  # header/message
    root.RowDefinitions.Add(RowDefinition())  # button grid
    outer.Child = root

    # Title / message
    header = TextBlock()
    header.Text = str(message or "")
    header.Margin = Thickness(0, 0, 0, 12)
    header.Foreground = SolidColorBrush(FG_LIGHT)
    header.FontSize = 16
    Grid.SetRow(header, 0)
    root.Children.Add(header)

    # Grid of buttons
    grid = Grid()
    Grid.SetRow(grid, 1)
    root.Children.Add(grid)

    rows = (len(opts) + columns - 1) // columns

    for _ in range(rows):
        grid.RowDefinitions.Add(RowDefinition())

    for _ in range(columns):
        grid.ColumnDefinitions.Add(ColumnDefinition())

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

    win.Content = outer
    win.ShowDialog()

    return choice["value"]