# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Snapchat Organizer Desktop
Builds standalone executables for macOS and Windows.

Windows notes:
  - UPX is DISABLED to prevent python3xx.dll and Qt DLL corruption
  - App name uses no spaces to avoid path issues with Windows temp dirs
  - Distributed as onedir (folder) mode
"""

import sys
from pathlib import Path

block_cipher = None

# Get project root
project_root = Path.cwd()

# Platform-specific settings
is_windows = sys.platform == 'win32'
is_macos = sys.platform == 'darwin'

# Windows: disable UPX entirely — it corrupts python3xx.dll and PySide6 DLLs,
# causing "Failed to load Python DLL" errors on end-user machines.
use_upx = False if is_windows else True

# Windows: use name without spaces to avoid path issues when extracting
# to directories with spaces (e.g. C:\Users\HP\AppData\Local\Temp\...)
app_name = 'SnapchatOrganizer' if is_windows else 'Snapchat Organizer'

# Windows: explicitly collect Visual C++ runtime DLLs that python311.dll depends on.
# Without these, end-users without VC++ Redistributable get "Failed to load Python DLL".
extra_binaries = []
if is_windows:
    import sysconfig
    python_dir = Path(sys.executable).parent
    # Collect MSVC runtime DLLs from Python's installation directory
    for pattern in ['vcruntime*.dll', 'msvcp*.dll', 'ucrtbase.dll', 'api-ms-win-*.dll']:
        for dll in python_dir.glob(pattern):
            extra_binaries.append((str(dll), '.'))
    # Also check the DLLs directory (common in embeddable Python)
    dlls_dir = python_dir / 'DLLs'
    if dlls_dir.exists():
        for pattern in ['vcruntime*.dll', 'msvcp*.dll', 'ucrtbase.dll']:
            for dll in dlls_dir.glob(pattern):
                extra_binaries.append((str(dll), '.'))

a = Analysis(
    ['src/main.py'],
    pathex=[str(project_root)],
    binaries=extra_binaries,
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
        'PySide6.QtNetwork',
        'sqlalchemy.sql.default_comparator',
        'PIL._tkinter_finder',
        'sentry_sdk',
        'sentry_sdk.integrations',
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
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=use_upx,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icons/icon.icns' if is_macos else 'resources/icons/icon.ico',
    version='file_version_info.txt' if is_windows else None,
    uac_admin=False,  # Don't request admin privileges
    uac_uiaccess=False,
)

# UPX exclusions for safety — even if UPX is enabled (macOS), never compress
# these critical binaries
upx_excludes = [
    'python3*.dll',
    'python*.dll',
    'Qt*.dll',
    'PySide6/*.pyd',
    'PySide6/*.dll',
    'shiboken6/*.pyd',
    'shiboken6/*.dll',
    'api-ms-win-*.dll',
    'ucrtbase.dll',
    'vcruntime*.dll',
    'msvcp*.dll',
]

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=use_upx,
    upx_exclude=upx_excludes,
    name=app_name,
)

# macOS .app bundle (only relevant when building on macOS)
if is_macos:
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
