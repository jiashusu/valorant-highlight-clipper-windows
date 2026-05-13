# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
from shutil import which

project = Path.cwd()

datas = [
    (str(project / "assets" / "valorant_clipper"), "assets/valorant_clipper"),
]
binaries = []

for tool in ("ffmpeg", "ffprobe", "ffplay"):
    filename = f"{tool}.exe"
    candidates = [
        project / "ffmpeg" / filename,
        project / "vendor" / "ffmpeg" / filename,
    ]
    resolved = next((path for path in candidates if path.exists()), None)
    if resolved is None:
        found = which(filename) or which(tool)
        resolved = Path(found) if found else None
    if resolved:
        binaries.append((str(resolved), "ffmpeg"))

a = Analysis(
    [str(project / "windows" / "launcher.py")],
    pathex=[str(project / "src")],
    binaries=binaries,
    datas=datas,
    hiddenimports=[
        "numpy.core.multiarray",
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["fastapi", "uvicorn", "starlette", "pydantic", "tkinter", "PIL.ImageTk"],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="ValorantHighlightClipper",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
