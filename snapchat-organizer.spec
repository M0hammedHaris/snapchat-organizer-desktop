# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Snapchat Organizer Desktop
Builds a standalone macOS .app bundle
"""

import sys
from pathlib import Path

block_cipher = None

# Get project root
project_root = Path.cwd()

a = Analysis(
    ['src/main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        # Include resources
        ('resources/icons/*.png', 'resources/icons'),
        ('resources/icons/*.icns', 'resources/icons'),
        ('resources/icons/*.ico', 'resources/icons'),
        # Include documentation
        ('docs/releases/alpha/ALPHA_TESTING_GUIDE.md', 'docs'),
        ('docs/releases/alpha/README_ALPHA.md', 'docs'),
        ('README.md', '.'),
        ('LICENSE', '.'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'sqlalchemy.sql.default_comparator',
        'PIL._tkinter_finder',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Snapchat Organizer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icons/icon.icns' if sys.platform == 'darwin' else 'resources/icons/icon.ico',
    version='file_version_info.txt' if sys.platform == 'win32' else None,
    uac_admin=False,  # Don't request admin privileges
    uac_uiaccess=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Snapchat Organizer',
)

# macOS .app bundle
app = BUNDLE(
    coll,
    name='Snapchat Organizer.app',
    icon='resources/icons/icon.icns',
    bundle_identifier='com.mohammedharis.snapchat-organizer',
    version='1.0.0-alpha',
    info_plist={
        'CFBundleName': 'Snapchat Organizer',
        'CFBundleDisplayName': 'Snapchat Organizer',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0-alpha',
        'CFBundleExecutable': 'Snapchat Organizer',
        'CFBundleIdentifier': 'com.mohammedharis.snapchat-organizer',
        'CFBundleInfoDictionaryVersion': '6.0',
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': '????',
        'LSMinimumSystemVersion': '10.13.0',
        'NSHighResolutionCapable': True,
        'NSHumanReadableCopyright': 'Copyright © 2026 Mohammed Haris. All rights reserved.',
        'LSApplicationCategoryType': 'public.app-category.utilities',
    },
)
