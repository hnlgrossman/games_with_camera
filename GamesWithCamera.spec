# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src\\main.py'],
    pathex=['src'],
    binaries=[('C:\\projects\\games_with_camera\\.venv\\lib\\site-packages\\vgamepad\\win\\vigem\\client\\x64\\ViGEmClient.dll', 'vgamepad/win/vigem/client/x64')],
    datas=[('moves_voices', 'moves_voices'), ('C:\\projects\\games_with_camera\\.venv\\lib\\site-packages\\mediapipe\\modules\\pose_landmark', 'mediapipe/modules/pose_landmark'), ('C:\\projects\\games_with_camera\\.venv\\lib\\site-packages\\mediapipe\\modules\\pose_detection', 'mediapipe/modules/pose_detection')],
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
    [],
    exclude_binaries=True,
    name='GamesWithCamera',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GamesWithCamera',
)
