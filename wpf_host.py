# -*- coding: utf-8 -*-
import os, clr
clr.AddReference("PresentationFramework")
clr.AddReference("PresentationCore")
clr.AddReference("WindowsBase")

from System import Uri, UriKind
from System.IO import FileStream, FileMode, FileAccess, FileShare
from System.Windows.Markup import XamlReader
from System.Windows import ResourceDictionary
from System.Windows.Interop import WindowInteropHelper

__ADA_UI_VERSION__ = "6.0.0"

def _load_window(xaml_path):
    if not os.path.exists(xaml_path):
        raise IOError("Dialog XAML not found: %s" % xaml_path)
    fs = FileStream(xaml_path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite)
    try:
        return XamlReader.Load(fs)
    finally:
        fs.Close()

def _merge_dict(win, path):
    if os.path.exists(path):
        rd = ResourceDictionary()
        rd.Source = Uri(os.path.abspath(path), UriKind.Absolute)
        win.Resources.MergedDictionaries.Add(rd)

def show_dialog(dialog_xaml, theme_root=None, init=None, owner_handle=None):
    win = _load_window(dialog_xaml)
    if theme_root:
        _merge_dict(win, os.path.join(theme_root, "Theme.xaml"))
        _merge_dict(win, os.path.join(theme_root, "Controls.xaml"))
    local = os.path.dirname(dialog_xaml)
    _merge_dict(win, os.path.join(local, "Theme.xaml"))
    _merge_dict(win, os.path.join(local, "Controls.xaml"))
    if owner_handle:
        WindowInteropHelper(win).Owner = owner_handle
    if init:
        init(win)
    result = win.ShowDialog()
    return (bool(result), win)
