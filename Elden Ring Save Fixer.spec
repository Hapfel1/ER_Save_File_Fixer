# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['elden_ring_save_fixer_gui.py'],
    pathex=[],
    binaries=[],
    datas=[('elden_ring_save_parser.py', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='Elden Ring Save Fixer',
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
    manifest='elden_ring_save_fixer.manifest',
    version='version_info.txt',
)
