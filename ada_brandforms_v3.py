
# ada_brandforms_v4.py — branded WPF dialogs for pyRevit (CPython3)
# Defaults baked in: maxw=1100 and position="center" (owner-centered)
# - Autosize + width clamp so long messages wrap
# - DPI-safe bottom row (Auto), layout rounding, min button sizes
# - Optional top-center placement with `position="top-center"`
# - Named elements + FindName (no brittle Children indexing)
# - Fallback to pyRevit forms, then WinForms shim if WPF is unavailable

BRAND = {"BLUE": "#5C7CFA", "PINK": "#F759C0", "BG": "#1F222A", "FG": "#FFFFFF"}

# Try WPF
try:
    import clr as _clr
    _clr.AddReference("WindowsBase"); _clr.AddReference("PresentationCore"); _clr.AddReference("PresentationFramework")
    from System.Windows.Markup import XamlReader
    from System.Windows.Media import SolidColorBrush, Color
    from System.Windows import WindowStartupLocation, Thickness, SystemParameters
    from System.Windows.Controls import Button, TextBlock, TextBox, ListBox, StackPanel
    from System.Windows.Interop import WindowInteropHelper
    from System.Diagnostics import Process
    _WPF = True
except Exception:
    _WPF = False


def _hex_to_color(h):
    h = h.strip().lstrip("#")
    if len(h) == 6:
        r,g,b,a = int(h[:2],16), int(h[2:4],16), int(h[4:6],16), 255
    elif len(h) == 8:
        a,r,g,b = int(h[:2],16), int(h[2:4],16), int(h[4:6],16), int(h[6:8],16)
    else:
        r=g=b=0; a=255
    return Color.FromArgb(a,r,g,b)


if _WPF:
    ADABLUE = _hex_to_color(BRAND["BLUE"]); ADAPINK = _hex_to_color(BRAND["PINK"]); FGCOLOR = _hex_to_color(BRAND["FG"])

    def _chrome(win):
        try:
            win.ResizeMode = 2  # CanResizeWithGrip
            win.SnapsToDevicePixels = True
            win.UseLayoutRounding = True
        except: pass

    def _set_owner_and_position(win, position="center", top_offset=24):
        """Center relative to Revit main window by default; support 'top-center' too."""
        try:
            WindowInteropHelper(win).Owner = Process.GetCurrentProcess().MainWindowHandle
            if position in ("center", None):
                win.WindowStartupLocation = WindowStartupLocation.CenterOwner
            elif position in ("top", "top-center"):
                win.WindowStartupLocation = WindowStartupLocation.Manual
                # place at top center after layout pass
                def _on_loaded(s, e):
                    wa = SystemParameters.WorkArea
                    s.Left = (wa.Width - s.ActualWidth) / 2 + wa.Left
                    s.Top  = wa.Top + float(top_offset or 0)
                win.Loaded += _on_loaded
            else:
                win.WindowStartupLocation = WindowStartupLocation.CenterOwner
        except:
            # fallback if owner can't be set
            if position in ("top", "top-center"):
                win.WindowStartupLocation = WindowStartupLocation.Manual
                def _on_loaded(s, e):
                    wa = SystemParameters.WorkArea
                    s.Left = (wa.Width - s.ActualWidth) / 2 + wa.Left
                    s.Top  = wa.Top + float(top_offset or 0)
                win.Loaded += _on_loaded
            else:
                win.WindowStartupLocation = WindowStartupLocation.CenterScreen

    def _size_attrs(autosize, minw, minh, maxw, maxh, width, height):
        if autosize and (width is None and height is None):
            return 'SizeToContent="WidthAndHeight" MinWidth="{:d}" MinHeight="{:d}" MaxWidth="{:d}" MaxHeight="{:d}"'.format(minw, minh, maxw, maxh)
        # force dimensions
        w = width  if width  is not None else minw
        h = height if height is not None else minh
        return 'Width="{:d}" Height="{:d}" MinWidth="{:d}" MinHeight="{:d}" MaxWidth="{:d}" MaxHeight="{:d}"'.format(w,h,minw,minh,maxw,maxh)

    class BrandForms(object):
        @staticmethod
        def alert(message, title="Message", yes=False, no=False, ok=False, cancel=False, *, autosize=True,
                  minw=560, minh=260, maxw=1100, maxh=900, width=None, height=None, position="center", top_offset=24):
            if yes and no: btns = [("Yes","yes"), ("No","no")]
            elif ok and cancel: btns = [("OK","ok"), ("Cancel","cancel")]
            elif ok or not any([yes,no,cancel]): btns = [("OK","ok")]
            else: btns = [("Cancel","cancel")]

            size_attr = _size_attrs(autosize, minw, minh, maxw, maxh, width, height)
            # Clamp content width so long messages wrap before window hits MaxWidth
            xaml = u"""
            <Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
                    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
                    Title="{title}" {size_attr} Background="{bg}" WindowStyle="SingleBorderWindow"
                    SnapsToDevicePixels="True" UseLayoutRounding="True">
              <Grid Margin="0">
                <Grid.RowDefinitions>
                  <RowDefinition Height="64"/>
                  <RowDefinition Height="*"/>
                  <RowDefinition Height="Auto"/>
                </Grid.RowDefinitions>
                <Border Grid.Row="0" CornerRadius="6,6,0,0">
                  <Border.Background>
                    <LinearGradientBrush StartPoint="0,0" EndPoint="1,0">
                      <GradientStop Color="{blue}" Offset="0"/>
                      <GradientStop Color="{pink}" Offset="1"/>
                    </LinearGradientBrush>
                  </Border.Background>
                </Border>
                <TextBlock Grid.Row="0" Margin="16,18,16,0" VerticalAlignment="Center"
                           Text="{title}" Foreground="{fg}" FontSize="18" FontWeight="SemiBold"
                           TextTrimming="CharacterEllipsis"/>
                <ScrollViewer Grid.Row="1" Margin="16,16,16,8" VerticalScrollBarVisibility="Auto" MaxWidth="{maxw}">
                  <TextBlock TextWrapping="Wrap" Foreground="{fg}" FontSize="14">{message}</TextBlock>
                </ScrollViewer>
                <StackPanel x:Name="ButtonBar" Grid.Row="2" Orientation="Horizontal" HorizontalAlignment="Right" Margin="0,6,16,16"/>
              </Grid>
            </Window>
            """.format(title=title, message=message, size_attr=size_attr, blue=BRAND["BLUE"], pink=BRAND["PINK"],
                       bg=BRAND["BG"], fg=BRAND["FG"], maxw=int(maxw))

            win = XamlReader.Parse(xaml); _chrome(win); _set_owner_and_position(win, position, top_offset)
            panel = win.FindName("ButtonBar")
            result = [None]
            for i,(text,token) in enumerate(btns):
                b = Button(); b.Content = text; b.Margin = Thickness(8,8,0,8); b.Padding = Thickness(18,6,18,6)
                b.MinWidth = 110; b.MinHeight = 36
                b.Foreground = SolidColorBrush(FGCOLOR)
                b.Background = SolidColorBrush(ADABLUE if i==0 else ADAPINK)
                def _click(s,e, tok=token): result[0]=tok; win.Close()
                b.Click += _click; panel.Children.Add(b)
            win.ShowDialog()
            if result[0] in ("yes","ok"): return True
            if result[0] in ("no","cancel"): return False
            return None

        @staticmethod
        def ask_for_string(prompt="", default=None, title="Input", *, autosize=True,
                           minw=600, minh=260, maxw=1100, maxh=900, width=None, height=None, position="center", top_offset=24):
            size_attr = _size_attrs(autosize, minw, minh, maxw, maxh, width, height)
            xaml = u"""
            <Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
                    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
                    Title="{title}" {size_attr} Background="{bg}" WindowStyle="SingleBorderWindow"
                    SnapsToDevicePixels="True" UseLayoutRounding="True">
              <Grid Margin="0">
                <Grid.RowDefinitions>
                  <RowDefinition Height="64"/>
                  <RowDefinition Height="*"/>
                  <RowDefinition Height="Auto"/>
                </Grid.RowDefinitions>
                <Border Grid.Row="0" CornerRadius="6,6,0,0">
                  <Border.Background>
                    <LinearGradientBrush StartPoint="0,0" EndPoint="1,0">
                      <GradientStop Color="{blue}" Offset="0"/>
                      <GradientStop Color="{pink}" Offset="1"/>
                    </LinearGradientBrush>
                  </Border.Background>
                </Border>
                <TextBlock Grid.Row="0" Margin="16,18,16,0" VerticalAlignment="Center"
                           Text="{title}" Foreground="{fg}" FontSize="18" FontWeight="SemiBold"
                           TextTrimming="CharacterEllipsis"/>
                <StackPanel Grid.Row="1" Margin="16,16,16,8" MaxWidth="{maxw}">
                  <TextBlock TextWrapping="Wrap" Foreground="{fg}" FontSize="14" Margin="0,0,0,8">{prompt}</TextBlock>
                  <TextBox x:Name="InputBox" Text="{default}" FontSize="14" Padding="8" HorizontalAlignment="Stretch"/>
                </StackPanel>
                <StackPanel x:Name="ButtonBar" Grid.Row="2" Orientation="Horizontal" HorizontalAlignment="Right" Margin="0,6,16,16">
                  <Button x:Name="OkBtn" Content="OK" Margin="8" Padding="18,6" MinWidth="110" MinHeight="36"/>
                  <Button x:Name="CancelBtn" Content="Cancel" Margin="8" Padding="18,6" MinWidth="110" MinHeight="36"/>
                </StackPanel>
              </Grid>
            </Window>
            """.format(title=title, prompt=prompt, default=default or "", size_attr=size_attr, blue=BRAND["BLUE"],
                       pink=BRAND["PINK"], bg=BRAND["BG"], fg=BRAND["FG"], maxw=int(maxw))

            win = XamlReader.Parse(xaml); _chrome(win); _set_owner_and_position(win, position, top_offset)
            okb = win.FindName("OkBtn"); cb = win.FindName("CancelBtn"); box = win.FindName("InputBox")
            okb.Foreground = SolidColorBrush(FGCOLOR); cb.Foreground = SolidColorBrush(FGCOLOR)
            okb.Background = SolidColorBrush(ADABLUE); cb.Background = SolidColorBrush(ADAPINK)
            result = [None]
            def _ok(s,e): result[0] = box.Text; win.Close()
            def _cancel(s,e): result[0] = None; win.Close()
            okb.Click += _ok; cb.Click += _cancel
            win.ShowDialog(); return result[0]

        class SelectFromList(object):
            @staticmethod
            def show(options, title="Select", button_name="OK", multiselect=False, width=760, height=520, *, autosize=False,
                     minw=620, minh=360, maxw=1100, maxh=900, position="center", top_offset=24):
                if not options: return None
                # For lists we default to fixed size, but allow autosize/clamp with maxw/maxh
                size_attr = _size_attrs(autosize, minw, minh, maxw, maxh, width if not autosize else None, height if not autosize else None)
                sel = "Extended" if multiselect else "Single"
                xaml = u"""
                <Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
                        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
                        Title="{title}" {size_attr} Background="{bg}" WindowStyle="SingleBorderWindow"
                        SnapsToDevicePixels="True" UseLayoutRounding="True">
                  <Grid Margin="0">
                    <Grid.RowDefinitions>
                      <RowDefinition Height="64"/>
                      <RowDefinition Height="*"/>
                      <RowDefinition Height="Auto"/>
                    </Grid.RowDefinitions>
                    <Border Grid.Row="0" CornerRadius="6,6,0,0">
                      <Border.Background>
                        <LinearGradientBrush StartPoint="0,0" EndPoint="1,0">
                          <GradientStop Color="{blue}" Offset="0"/>
                          <GradientStop Color="{pink}" Offset="1"/>
                        </LinearGradientBrush>
                      </Border.Background>
                    </Border>
                    <TextBlock Grid.Row="0" Margin="16,18,16,0" VerticalAlignment="Center"
                               Text="{title}" Foreground="{fg}" FontSize="18" FontWeight="SemiBold"
                               TextTrimming="CharacterEllipsis"/>
                    <ListBox x:Name="LB" Grid.Row="1" Margin="16,16,16,8" SelectionMode="{sel}" MaxWidth="{maxw}"/>
                    <StackPanel x:Name="ButtonBar" Grid.Row="2" Orientation="Horizontal" HorizontalAlignment="Right" Margin="0,6,16,16">
                      <Button x:Name="OkBtn" Content="{button}" Margin="8" Padding="18,6" MinWidth="110" MinHeight="36"/>
                      <Button x:Name="CancelBtn" Content="Cancel" Margin="8" Padding="18,6" MinWidth="110" MinHeight="36"/>
                    </StackPanel>
                  </Grid>
                </Window>
                """.format(title=title, sel=sel, button=button_name, size_attr=size_attr, blue=BRAND["BLUE"],
                           pink=BRAND["PINK"], bg=BRAND["BG"], fg=BRAND["FG"], maxw=int(maxw))

                win = XamlReader.Parse(xaml); _chrome(win); _set_owner_and_position(win, position, top_offset)
                lb = win.FindName("LB"); okb = win.FindName("OkBtn"); cb = win.FindName("CancelBtn")
                okb.Foreground = SolidColorBrush(FGCOLOR); cb.Foreground = SolidColorBrush(FGCOLOR)
                okb.Background = SolidColorBrush(ADABLUE); cb.Background = SolidColorBrush(ADAPINK)

                for it in options: lb.Items.Add(it)

                result=[None]
                def _ok(s,e):
                    if lb.SelectionMode.ToString()=="Single": result[0] = lb.SelectedItem
                    else: result[0] = [i for i in lb.SelectedItems]
                    win.Close()
                def _cancel(s,e): result[0] = None; win.Close()
                okb.Click += _ok; cb.Click += _cancel  # ensure handler added (idempotent)
                win.ShowDialog(); return result[0]

    forms = BrandForms
__brandforms_version__ = 'v4.1'
    FORMS_BRANDED = True

else:
    # Fallbacks
    try:
        from pyrevit import forms as _pyforms
        forms = _pyforms; FORMS_BRANDED = False
    except Exception:
        import clr
        clr.AddReference("System"); clr.AddReference("System.Drawing"); clr.AddReference("System.Windows.Forms"); clr.AddReference("RevitAPIUI")
        from System.Drawing import Size, Point
        from System.Windows.Forms import Application, Form, Label, Button, DialogResult, ListBox, SelectionMode, TextBox
        from Autodesk.Revit.UI import TaskDialog, TaskDialogCommonButtons, TaskDialogResult
        def _taskdialog(msg, title="Message", buttons="OK"):
            td = TaskDialog(title); td.MainInstruction=title; td.MainContent=msg
            mapbtn={"OK":TaskDialogCommonButtons.Ok,"OKCancel":TaskDialogCommonButtons.Ok|TaskDialogCommonButtons.Cancel,"YesNo":TaskDialogCommonButtons.Yes|TaskDialogCommonButtons.No,
                    "YesNoCancel":TaskDialogCommonButtons.Yes|TaskDialogCommonButtons.No|TaskDialogCommonButtons.Cancel}
            td.CommonButtons = mapbtn.get(buttons, TaskDialogCommonButtons.Ok)
            res = td.Show()
            return {TaskDialogResult.Ok:"ok", TaskDialogResult.Close:"ok", TaskDialogResult.Cancel:"cancel",
                    TaskDialogResult.Yes:"yes", TaskDialogResult.No:"no"}.get(res)
        class _Shim(object):
            @staticmethod
            def alert(message, title="Message", yes=False, no=False, ok=False, cancel=False):
                if yes and no: r=_taskdialog(message,title,"YesNo");  return True if r=="yes" else False if r=="no" else None
                if ok and cancel: r=_taskdialog(message,title,"OKCancel"); return True if r=="ok" else False if r=="cancel" else None
                if ok or not any([yes,no,cancel]): _taskdialog(message,title,"OK"); return True
                if cancel and not ok: r=_taskdialog(message,title,"OKCancel"); return False if r=="cancel" else True
            @staticmethod
            def ask_for_string(prompt="", default=None, title="Input"):
                from System.Windows.Forms import Form, Label, TextBox, Button, DialogResult
                f=Form(); f.Text=title; f.Width=560; f.Height=220
                l=Label(); l.Text=prompt; l.SetBounds(10,10,520,40); f.Controls.Add(l)
                t=TextBox(); t.Text=default or ""; t.SetBounds(10,55,520,24); f.Controls.Add(t)
                ok=Button(); ok.Text="OK"; ok.SetBounds(360,150,80,24); ok.DialogResult=DialogResult.OK; f.Controls.Add(ok)
                ca=Button(); ca.Text="Cancel"; ca.SetBounds(450,150,80,24); ca.DialogResult=DialogResult.Cancel; f.Controls.Add(ca)
                if f.ShowDialog()==DialogResult.OK: return t.Text
                return None
            class SelectFromList(object):
                @staticmethod
                def show(options, title="Select", button_name="OK", multiselect=False, width=640, height=420):
                    from System.Windows.Forms import Form, ListBox, SelectionMode, Button, DialogResult
                    f=Form(); f.Text=title; f.Width=int(width); f.Height=int(height)
                    lb=ListBox(); lb.SelectionMode=SelectionMode.MultiExtended if multiselect else SelectionMode.One; lb.SetBounds(10,10,width-30,height-80)
                    for it in options: lb.Items.Add(it); f.Controls.Add(lb)
                    ok=Button(); ok.Text=button_name; ok.SetBounds(width-200,height-60,80,24); ok.DialogResult=DialogResult.OK; f.Controls.Add(ok)
                    ca=Button(); ca.Text="Cancel"; ca.SetBounds(width-110,height-60,80,24); ca.DialogResult=DialogResult.Cancel; f.Controls.Add(ca)
                    return [lb.Items[i] for i in range(lb.Items.Count) if lb.GetSelected(i)] if f.ShowDialog()==DialogResult.OK else None
        forms = _Shim; FORMS_BRANDED = False
