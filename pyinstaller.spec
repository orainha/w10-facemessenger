# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

analysis = Analysis(
    ['./w10-facemessenger/main.py'],
    binaries = [ ('./w10-facemessenger/hindsight.exe', '.'), ('./w10-facemessenger/undark.exe', '.') ],
    datas = [ ('./w10-facemessenger/templates', 'templates') ],
    hiddenimports = [],
    hookspath = [],
    runtime_hooks = [],
    excludes = [],
    win_no_prefer_redirects = False,
    win_private_assemblies = False,
    cipher = block_cipher,
    noarchive = False
)

pyz = PYZ(
    analysis.pure,
    analysis.zipped_data,
    cipher = block_cipher
)

exe = EXE(
    pyz,
    analysis.scripts,
    analysis.binaries,
    analysis.zipfiles,
    analysis.datas,
    [],
    name = 'w10-facemessenger',
    debug = False,
    bootloader_ignore_signals = False,
    strip = False,
    upx = True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console = True
)