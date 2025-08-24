# ada_brandforms_v5.py  — ADa-branded dialogs with custom window chrome
import clr
clr.AddReference("PresentationCore")
clr.AddReference("PresentationFramework")
clr.AddReference("WindowsBase")

from System.Windows import Window, WindowStartupLocation, Thickness, HorizontalAlignment, VerticalAlignment, SizeToContent #type:ignore
from System.Windows.Controls import Grid, RowDefinition, ColumnDefinition, TextBlock, Button, Border, StackPanel #type:ignore
from System.Windows.Media import SolidColorBrush, LinearGradientBrush, GradientStop, GradientStopCollection #type:ignore
from System.Windows.Media import Color, Colors #type:ignore
from System.Windows.Input import MouseButtonState, Key #type:ignore
from System.Windows.Shell import WindowChrome #type:ignore
from System import String #type:ignore

ADA_BLUE = Color.FromRgb(0x5C,0x7C,0xFA)   # #5C7CFA
ADA_PINK = Color.FromRgb(0xF7,0x59,0xC0)   # #F759C0
BG_DARK  = Color.FromRgb(0x1F,0x23,0x2B)   # dark body
FG_LIGHT = Color.FromRgb(0xE8,0xEA,0xED)

def _grad_header():
    gs = GradientStopCollection()
    gs.Add(GradientStop(SolidColorBrush(ADA_BLUE).Color, 0.0))
    gs.Add(GradientStop(SolidColorBrush(ADA_PINK).Color, 1.0))
    return LinearGradientBrush(gs, 0)

class _AdaDialog(Window):
    def __init__(self, title, body_text, buttons):
        Window.__init__(self)
        # ---- remove OS chrome, keep shadow via WindowChrome
        self.WindowStyle = 0      # None
        self.ResizeMode = 0       # NoResize
        wc = WindowChrome()
        wc.CaptionHeight = 0
        wc.CornerRadius = Thickness(8).TopLeft   # simple rounded corners
        wc.ResizeBorderThickness = Thickness(6)
        wc.UseAeroCaptionButtons = False
        WindowChrome.SetWindowChrome(self, wc)

        self.Title = str(title or "")
        self.SizeToContent = SizeToContent.WidthAndHeight
        self.WindowStartupLocation = WindowStartupLocation.CenterScreen
        self.Background = SolidColorBrush(BG_DARK)
        self.Padding = Thickness(0)
        self._result = None

        root = Grid()
        root.RowDefinitions.Add(RowDefinition())  # header
        root.RowDefinitions[0].Height = Thickness(60).Bottom  # fixed 60px
        root.RowDefinitions.Add(RowDefinition())  # body
        root.RowDefinitions.Add(RowDefinition())  # buttons
        self.Content = root

        # Header
        header = Border(Background=_grad_header(), CornerRadius=Thickness(8,8,0,0).TopLeft)
        Grid.SetRow(header, 0)
        headerGrid = Grid()
        headerGrid.ColumnDefinitions.Add(ColumnDefinition())
        headerGrid.ColumnDefinitions.Add(ColumnDefinition())
        header.Child = headerGrid
        root.Children.Add(header)

        title_tb = TextBlock(Text=str(title or ""), Margin=Thickness(20,14,20,0),
                             Foreground=SolidColorBrush(FG_LIGHT), FontSize=22)
        title_tb.VerticalAlignment = VerticalAlignment.Center
        Grid.SetColumn(title_tb, 0)
        headerGrid.Children.Add(title_tb)

        btn_close = Button(Content="✕", Width=36, Height=28, Margin=Thickness(0,10,10,0))
        btn_close.HorizontalAlignment = HorizontalAlignment.Right
        btn_close.VerticalAlignment = VerticalAlignment.Center
        btn_close.Background = SolidColorBrush(ADA_PINK)
        btn_close.Foreground = SolidColorBrush(Colors.White)
        btn_close.BorderThickness = Thickness(0)
        btn_close.Cursor = None
        btn_close.Click += lambda s,e: self._close(False)
        Grid.SetColumn(btn_close, 1)
        headerGrid.Children.Add(btn_close)

        # Allow dragging by header
        def _drag(sender, e):
            if e.LeftButton == MouseButtonState.Pressed:
                try: self.DragMove()
                except: pass
        header.MouseLeftButtonDown += _drag

        # Body
        body_border = Border(Margin=Thickness(24,20,24,0), Background=SolidColorBrush(BG_DARK))
        Grid.SetRow(body_border, 1)
        root.Children.Add(body_border)
        body_tb = TextBlock(Text=str(body_text or ""), TextWrapping=0x2,  # Wrap
                            Foreground=SolidColorBrush(FG_LIGHT), FontSize=16)
        body_border.Child = body_tb

        # Buttons
        btn_row = Border(Margin=Thickness(24,18,24,20), Background=SolidColorBrush(BG_DARK))
        Grid.SetRow(btn_row, 2)
        root.Children.Add(btn_row)

        btn_panel = StackPanel(Orientation=0, HorizontalAlignment=HorizontalAlignment.Right)
        btn_row.Child = btn_panel

        def make_btn(label, is_primary=False):
            b = Button(Content=String(label), Width=110, Height=36, Margin=Thickness(8,0,0,0))
            b.BorderThickness = Thickness(0)
            if is_primary:
                b.Background = SolidColorBrush(ADA_BLUE)
                b.Foreground = SolidColorBrush(Colors.White)
            else:
                b.Background = SolidColorBrush(ADA_PINK)
                b.Foreground = SolidColorBrush(Colors.White)
            return b

        for i, lab in enumerate(buttons):
            b = make_btn(lab, is_primary=(i==0))
            b.Click += (lambda s,e,lab=lab: self._close(lab))
            btn_panel.Children.Add(b)

        # Keyboard: ESC cancels, Enter = primary
        def _key(sender, e):
            if e.Key == Key.Escape:
                self._close(False)
            elif e.Key == Key.Enter:
                self._close(buttons[0] if buttons else True)
        self.KeyDown += _key

    def _close(self, value):
        self._result = value
        try: self.DialogResult = True
        except: pass
        self.Close()

def alert(msg, title="Message", buttons=("OK",)):
    dlg = _AdaDialog(title, msg, list(buttons))
    dlg.ShowDialog()
    return dlg._result

def ask_yes_no(msg, title="Confirm"):
    res = alert(msg, title, buttons=("Yes","No"))
    return True if res == "Yes" else False
