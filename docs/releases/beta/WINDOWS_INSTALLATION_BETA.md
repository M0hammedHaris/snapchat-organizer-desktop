# Windows Installation Guide - Snapchat Organizer Desktop Beta

**Version:** 1.0.0-beta.1  
**Last Updated:** February 2026  
**Target:** Windows 10/11

---

## Understanding Windows SmartScreen

When you first run Snapchat Organizer Desktop, **Windows Defender SmartScreen may show a warning**. This is normal for new applications that aren't code-signed.

### Why does this happen?
- Code signing certificates cost $300-500/year (planned for production)
- Windows SmartScreen uses reputation — new apps with few downloads trigger warnings
- **This is NOT a virus** — all processing happens locally on your PC

---

## Installation Steps

### Step 1: Download
1. Go to the [GitHub Releases page](https://github.com/M0hammedHaris/snapchat-organizer-desktop/releases)
2. Download **`Snapchat-Organizer-Windows.zip`** (~150 MB)

### Step 2: Extract the ZIP

> **IMPORTANT: You MUST extract the ZIP before running the app!**  
> Do NOT run the .exe from inside the ZIP — it will fail with DLL errors.

1. **Right-click** on `Snapchat-Organizer-Windows.zip`
2. Select **"Extract All..."**
3. Choose a simple path like `C:\SnapchatOrganizer\`
   - Avoid paths with spaces (e.g., `C:\Program Files\`)
4. Click **"Extract"**

### Step 3: Run the App
1. Open the extracted folder
2. Double-click **`SnapchatOrganizer.exe`**

### Step 4: Bypass SmartScreen (First Run Only)

You'll see: "Windows protected your PC"

1. Click **"More info"**
2. Click **"Run anyway"**
3. The app launches! (One-time only)

```
┌─────────────────────────────────────────┐
│  Windows protected your PC              │
│                                         │
│  More info                    [Don't run]│
└─────────────────────────────────────────┘
                    ↓ Click "More info"

┌─────────────────────────────────────────┐
│  App: SnapchatOrganizer.exe             │
│  Publisher: Mohammed Haris              │
│                                         │
│  [Run anyway]               [Don't run] │
└─────────────────────────────────────────┘
                    ↓ Click "Run anyway"
```

### Step 5: Desktop Shortcut (Optional)
1. Right-click `SnapchatOrganizer.exe`
2. Select **Send to** → **Desktop (create shortcut)**

---

## First Launch

1. **Onboarding Carousel** — Guided walkthrough of app features
2. **License Registration** — Register for free or skip to use Free tier
3. **Main App** — Three tabs: Download, Organize, Tools
4. Press **F1** for help at any time

---

## Troubleshooting

### "Failed to load Python DLL" or "Cannot find Python"
- **Cause:** Running the .exe from inside the ZIP without extracting
- **Fix:** Extract the ZIP first, then run from the extracted folder

### "VCRUNTIME140.dll not found"
- **Cause:** Missing Visual C++ Runtime
- **Fix:** Download [VC++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe) from Microsoft

### App crashes on startup
1. Make sure you extracted to a path without special characters
2. Try running as administrator (right-click → Run as administrator)
3. Check if antivirus is blocking the app

### Slow first launch
Normal for PyInstaller apps — the first launch extracts bundled files. Subsequent launches are faster.

---

## Security & Privacy

- **No network activity** except downloading Snapchat memories (when you initiate it)
- **All processing is local** — your files never leave your computer
- **Crash reports** via Sentry contain only error information, never your personal files
- **Open source** — all code is reviewable on [GitHub](https://github.com/M0hammedHaris/snapchat-organizer-desktop)

---

## Need Help?

- [Create an Issue](https://github.com/M0hammedHaris/snapchat-organizer-desktop/issues/new)
- Check the [Beta Testing Guide](BETA_TESTING_GUIDE.md)
