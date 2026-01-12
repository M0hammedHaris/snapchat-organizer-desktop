# Windows Installation Guide - Snapchat Organizer Desktop

**Version:** 1.0.0-alpha  
**Last Updated:** January 12, 2026  
**Target:** Windows 10/11 Users

---

## 🛡️ Understanding Windows SmartScreen

When you first run Snapchat Organizer Desktop, **Windows Defender SmartScreen may show a warning**. This is completely normal and expected for new applications that aren't yet widely distributed.

### Why does this happen?

- **The app is unsigned**: Code signing certificates cost $300-500/year. As an alpha release, we haven't purchased one yet.
- **Low download count**: Windows SmartScreen uses "reputation" - apps with few downloads trigger warnings.
- **This is NOT a virus**: The app is completely safe. All processing happens locally on your computer, and nothing is uploaded to the internet.

### ✅ This app is safe because:

1. **Open source code**: You can review all code on [GitHub](https://github.com/M0hammedHaris/snapchat-organizer-desktop)
2. **No network activity**: The app doesn't connect to the internet (except for downloading memories from Snapchat HTML files)
3. **Local processing only**: All your data stays on your computer
4. **Created by a verified developer**: Mohammed Haris ([@M0hammedHaris](https://github.com/M0hammedHaris))

---

## 📦 Installation Steps

### Step 1: Download the Application

1. Go to the [GitHub Releases page](https://github.com/M0hammedHaris/snapchat-organizer-desktop/releases/tag/v1.0.0-alpha)
2. Download **`Snapchat-Organizer-Windows.zip`** (~120-150 MB)
3. Save it to your Downloads folder

### Step 2: Extract the ZIP File

1. **Right-click** on `Snapchat-Organizer-Windows.zip`
2. Select **"Extract All..."**
3. Choose a destination (e.g., `C:\Program Files\Snapchat Organizer\`)
4. Click **"Extract"**

### Step 3: Bypass Windows SmartScreen (First Run Only)

When you first double-click `Snapchat Organizer.exe`, you'll see this screen:

```
Windows protected your PC
Microsoft Defender SmartScreen prevented an unrecognized app from starting.
Running this app might put your PC at risk.
```

**Don't worry! Here's how to proceed:**

#### Method 1: Click "More info" (Recommended)

1. Click **"More info"** on the SmartScreen dialog
2. A new button will appear: **"Run anyway"**
3. Click **"Run anyway"**
4. The app will launch!

**Screenshot:**
```
┌─────────────────────────────────────────┐
│  Windows protected your PC              │
│                                         │
│  Microsoft Defender SmartScreen         │
│  prevented an unrecognized app from     │
│  starting. Running this app might       │
│  put your PC at risk.                   │
│                                         │
│  More info                    [Don't run]│
└─────────────────────────────────────────┘
                    ↓ Click here

┌─────────────────────────────────────────┐
│  Windows protected your PC              │
│                                         │
│  App: Snapchat Organizer.exe            │
│  Publisher: Unknown publisher           │
│                                         │
│  [Run anyway]               [Don't run] │
└─────────────────────────────────────────┘
                    ↓ Then click here
```

#### Method 2: Add to Windows Defender Exclusions

If you prefer to bypass SmartScreen permanently:

1. Open **Windows Security** (press `Win + I` → Update & Security → Windows Security)
2. Go to **Virus & threat protection**
3. Click **Manage settings** under "Virus & threat protection settings"
4. Scroll down to **Exclusions**
5. Click **Add or remove exclusions**
6. Click **Add an exclusion** → **Folder**
7. Select the folder where you extracted the app
8. Click **Select Folder**

Now Windows Defender will trust the app!

### Step 4: Create a Desktop Shortcut (Optional)

1. Navigate to the extracted folder
2. **Right-click** on `Snapchat Organizer.exe`
3. Select **Send to** → **Desktop (create shortcut)**
4. Now you can launch the app from your desktop!

### Step 5: Pin to Start Menu or Taskbar (Optional)

**Pin to Start:**
1. Right-click `Snapchat Organizer.exe`
2. Select **Pin to Start**

**Pin to Taskbar:**
1. Right-click `Snapchat Organizer.exe`
2. Select **Pin to taskbar**

---

## 🚀 First Launch

Once the app launches successfully:

1. **Help dialog will appear automatically** on first run
   - This shows step-by-step instructions for downloading your Snapchat data
   - You can also access it anytime by pressing **F1**

2. **Explore the three main tabs:**
   - **📥 Download Memories**: Download memories from Snapchat HTML exports
   - **📁 Organize Chat Media**: Organize chat media by person with smart matching
   - **🔧 Tools**: 6 utility tools for media management

3. **Configure settings** (optional):
   - Press **Ctrl+,** to open Settings
   - Customize paths, delays, and processing options
   - All settings persist between sessions

---

## ❓ Troubleshooting

### Issue: "Cannot find Python"

**Solution:** This is a standalone build - **no Python installation required!** If you see this error, you may be trying to run the source code instead of the built executable.

- Make sure you're running `Snapchat Organizer.exe` from the extracted folder
- NOT running any `.py` files

### Issue: "App won't start" or crashes immediately

**Solution:**

1. Try running as Administrator:
   - Right-click `Snapchat Organizer.exe`
   - Select **"Run as administrator"**

2. Check Windows Event Viewer for errors:
   - Press `Win + X` → **Event Viewer**
   - Go to **Windows Logs** → **Application**
   - Look for recent errors from "Snapchat Organizer"

3. Check antivirus software:
   - Some antivirus programs (Norton, McAfee, Avast) may block the app
   - Add the app folder to your antivirus exclusions

### Issue: "VCRUNTIME140.dll is missing"

**Solution:** Install Microsoft Visual C++ Redistributable

1. Download from [Microsoft's website](https://aka.ms/vs/17/release/vc_redist.x64.exe)
2. Run the installer
3. Restart your computer
4. Try launching the app again

### Issue: App is very slow or unresponsive

**Solution:**

1. **First launch is always slower** (PyInstaller apps extract files on first run)
2. **Subsequent launches will be faster**
3. If processing large Snapchat exports (100GB+), expect longer processing times
4. Check Task Manager to ensure your disk isn't at 100% usage

### Issue: "Windows Defender blocked this app"

**Solution:** Follow **Step 3** above to bypass SmartScreen

---

## 🔒 Security & Privacy

### What data does the app access?

- **Snapchat export files** (memories_history.html, chat_history.json, etc.)
- **Local media files** (photos/videos from your Snapchat export)
- **Application logs** (stored in `%APPDATA%\Snapchat-Organizer\logs\`)
- **Configuration file** (stored in `%APPDATA%\Snapchat-Organizer\config.json`)

### What data is uploaded/sent?

**Nothing!** The app operates **100% offline**:
- No telemetry or analytics
- No crash reporting to external servers
- No license validation (alpha version is free)
- No internet connection required (except for the Download tab which fetches media from Snapchat URLs in your export)

### Can I run this on an air-gapped computer?

**Yes!** The app doesn't require internet connectivity for most features:
- ✅ **Organize Chat Media**: Works offline
- ✅ **Tools (Verify, Dedup, Year, Timestamp)**: Works offline
- ⚠️ **Download Memories**: Requires internet to download media from Snapchat URLs
- ⚠️ **Tools (Timezone, Overlays)**: Coming in Phase 2

---

## 🔮 Future Plans

### Code Signing (Phase 3)

We plan to code sign the Windows build in Phase 3:

- **Timeline**: 2-3 months
- **Cost**: ~$300-500/year for certificate
- **Benefit**: No more SmartScreen warnings!
- **Provider**: Likely DigiCert or Sectigo

Once code signed, Windows will:
- Show "Verified publisher: Mohammed Haris"
- No SmartScreen warning on first launch
- Increased trust and security

### Installer (Phase 3)

We're also planning to create a proper installer:

- **Tool**: NSIS or Inno Setup
- **Features**:
  - Automatic installation to Program Files
  - Start Menu shortcuts
  - Desktop shortcut
  - Uninstaller
  - Automatic updates
- **Timeline**: 2-3 months

---

## 📞 Getting Help

### Still having issues?

1. **Check the Help menu** in the app (F1)
2. **Read the Alpha Testing Guide**: See `docs/releases/alpha/ALPHA_TESTING_GUIDE.md`
3. **Create a GitHub Issue**: [Report a bug](https://github.com/M0hammedHaris/snapchat-organizer-desktop/issues/new)
4. **Email the developer**: [Your email address]

When reporting issues, please include:
- Windows version (e.g., Windows 11 22H2)
- Error message (if any)
- Steps to reproduce
- Screenshots (if applicable)

---

## ✅ Installation Checklist

- [ ] Downloaded `Snapchat-Organizer-Windows.zip`
- [ ] Extracted to a permanent location (not in Downloads folder)
- [ ] Bypassed Windows SmartScreen warning
- [ ] App launched successfully
- [ ] Reviewed the Help dialog (F1)
- [ ] Configured settings (Ctrl+,) if needed
- [ ] Created desktop shortcut (optional)
- [ ] Ready to organize Snapchat memories! 🎉

---

## 🎉 You're All Set!

Snapchat Organizer Desktop is now installed and ready to use. Enjoy organizing your memories!

**Pro Tip:** Press **F1** anytime for step-by-step instructions on downloading your Snapchat data.

---

**Last Updated:** January 12, 2026  
**Version:** 1.0.0-alpha  
**Maintained by:** [@M0hammedHaris](https://github.com/M0hammedHaris)
