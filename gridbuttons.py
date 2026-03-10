# -*- coding: utf-8 -*-
from __future__ import annotations

def choose_grid_buttons(options, title="Choose", message="", columns=3):
    """
    Compact ADa themed grid button chooser.

    options : list[str]
    columns : number of columns in grid layout
    returns : selected label or None
    """

    import clr #type: ignore
    clr.AddReference("PresentationFramework")
    clr.AddReference("PresentationCore")
    clr.AddReference("WindowsBase")

    from System.Windows import Window, WindowStartupLocation, Thickness, SizeToContent #type: ignore
    from System.Windows.Controls import Grid, Button, TextBlock, Border #type: ignore
    from System.Windows.Media import SolidColorBrush, Color #type: ignore
    from System.Windows import CornerRadius #type: ignore

    ADA_BLUE = Color.FromRgb(0x5C, 0x7C, 0xFA)
    BG_DARK = Color.FromRgb(0x1F, 0x23, 0x2B)

    choice = {"value": None}

    win = Window()
    win.Title = title
    win.WindowStartupLocation = WindowStartupLocation.CenterScreen
    win.SizeToContent = SizeToContent.WidthAndHeight

    outer = Border()
    outer.Background = SolidColorBrush(BG_DARK)
    outer.CornerRadius = CornerRadius(10)
    outer.Padding = Thickness(20)

    root = Grid()
    outer.Child = root

    # title
    header = TextBlock()
    header.Text = message
    header.Margin = Thickness(0,0,0,10)
    root.Children.Add(header)

    grid = Grid()
    root.Children.Add(grid)

    rows = int((len(options) + columns - 1) / columns)

    for r in range(rows):
        grid.RowDefinitions.Add(Grid.RowDefinition())

    for c in range(columns):
        grid.ColumnDefinitions.Add(Grid.ColumnDefinition())

    def make_btn(label):
        b = Button()
        b.Content = label
        b.Margin = Thickness(4)
        b.Background = SolidColorBrush(ADA_BLUE)

        def click(sender, args):
            choice["value"] = label
            win.Close()

        b.Click += click
        return b

    for i, label in enumerate(options):
        r = i // columns
        c = i % columns

        btn = make_btn(label)
        Grid.SetRow(btn, r)
        Grid.SetColumn(btn, c)

        grid.Children.Add(btn)

    win.Content = outer
    win.ShowDialog()

    return choice["value"]