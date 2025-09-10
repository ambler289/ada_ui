# -*- coding: utf-8 -*-
"""
ADa bootstrap — Option 2 (prefer Tools over Manage)
---------------------------------------------------
Sets import and DLL search order so NumPy 2.x + Shapely 2.x load reliably under
pyRevit CPython (Revit 2024+). Tools > Manage is enforced, central shared cache
(C:/Revit/pyrevit_pkgs/cp312) is added, and any pre-existing thirdparty paths are
removed before ours are inserted.
"""

from __future__ import annotations
import os
import sys
import platform
from pathlib import Path
from typing import Iterable

# ----------------------- tiny logger -----------------------
def _log_path() -> Path:
    return Path.home() / "Desktop" / "ADa_bootstrap.log"

def _log_write(lines: Iterable[str]) -> None:
    try:
        lp = _log_path()
        lp.parent.mkdir(parents=True, exist_ok=True)
        with lp.open("a", encoding="utf-8") as f:
            for line in lines:
                f.write(str(line).rstrip() + "\n")
    except Exception:
        pass

def _log_header(title: str) -> None:
    _log_write(["", "=" * 78, title, "=" * 78])

# --------------------- helpers -----------------------------
def _add_first(p: Path) -> None:
    """Prepend a path to sys.path if it exists."""
    try:
        if p and p.is_dir():
            s = str(p)
            if s not in sys.path:
                sys.path.insert(0, s)
    except Exception:
        pass

def _add_dll_dir(p: Path) -> None:
    """Add a directory to the Windows DLL search path (Py 3.8+)."""
    try:
        if hasattr(os, "add_dll_directory") and p and p.is_dir():
            os.add_dll_directory(str(p))
    except Exception:
        pass

# ------------------- main entry ----------------------------
def ensure_paths() -> None:
    # Detect our Python tag (e.g. cp312) and platform folder
    tag  = "cp{}{}".format(sys.version_info.major, sys.version_info.minor)  # cp312
    plat = "win-amd64-" + tag

    # Resolve %APPDATA%\pyRevit\Extensions
    appdata = Path(os.environ.get("APPDATA", Path.home() / "AppData/Roaming"))
    exts    = appdata / "pyRevit" / "Extensions"

    tools_lib   = exts / "ADa-Tools.extension"  / "lib"
    manage_lib  = exts / "ADa-Manage.extension" / "lib"
    tools_tp    = tools_lib  / "thirdparty"
    manage_tp   = manage_lib / "thirdparty"
    tools_base  = tools_tp   / plat             # e.g. ...\thirdparty\win-amd64-cp312

    # >>> Add central shared cache (NAS/local sync)
    shared_base = Path(r"C:\Revit\pyrevit_pkgs\cp312")

    # 0) Keep stray site-packages out of the way (only if not set)
    os.environ.setdefault("PYTHONNOUSERSITE", "1")

    # 1) Remove any existing thirdparty entries so we control ordering
    def _starts_with_any(s: str, roots: list[Path]) -> bool:
        s_lower = s.lower()
        for r in roots:
            if str(r).lower() and s_lower.startswith(str(r).lower()):
                return True
        return False

    roots_to_strip = [
        tools_tp, tools_tp / "common", tools_base,
        manage_tp, manage_tp / "common", manage_tp / plat,
        shared_base
    ]
    sys.path[:] = [p for p in sys.path if not _starts_with_any(p, roots_to_strip)]

    # 2) Insert **Tools first**, then **Manage**, then shared cache
    _add_first(tools_tp / "common")
    _add_first(tools_base)
    _add_first(tools_lib)

    _add_first(manage_tp / "common")
    _add_first(manage_tp / plat)
    _add_first(manage_lib)

    _add_first(shared_base)

    # 3) Add DLL directories (NumPy + Shapely)
    _add_dll_dir(shared_base)
    _add_dll_dir(shared_base / r"numpy\_core")
    _add_dll_dir(shared_base / r"shapely\.libs")

    # 4) Log snapshot
    _log_header("ADa bootstrap (Tools > Manage > Shared)")
    _log_write([
        "Python: {} ({})".format(platform.python_version(), platform.architecture()[0]),
        "Exec  : {}".format(sys.executable),
        "Tag   : {}".format(tag),
        "Tools lib      : {}".format(tools_lib),
        "Manage lib     : {}".format(manage_lib),
        "Thirdparty base: {}".format(tools_base),
        "Shared base    : {}".format(shared_base),
        "",
        "[sys.path first 20]",
        *sys.path[:20],
    ])

# Run once when imported
try:
    ensure_paths()
except Exception as e:
    _log_header("ADa bootstrap EXCEPTION")
    _log_write([repr(e)])
