# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['jobreach/cli.py'],
    pathex=[],
    binaries=[],
    datas=[('jobreach/credentials/google_client_secret.json', 'jobreach/credentials')],
    hiddenimports=['jobreach'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='jobreach',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
)
