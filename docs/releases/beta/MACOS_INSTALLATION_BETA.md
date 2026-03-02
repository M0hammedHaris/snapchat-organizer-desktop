# macOS Installation Guide - Snapchat Organizer Desktop Beta

**Version:** 1.0.0-beta.1  
**Last Updated:** February 2026

---

## Quick Fix

If you see "Apple could not verify..." or "unidentified developer" warning:

### Option 1: Right-Click Open (Recommended)
1. **Right-click** "Snapchat Organizer" in Applications
2. Click **"Open"**
3. Click **"Open"** again in the security dialog
4. App launches! (One-time only)

### Option 2: Terminal Command
```bash
xattr -cr "/Applications/Snapchat Organizer.app"
```
Then double-click to open normally.

### Option 3: System Settings
1. Try to open the app (it will be blocked)
2. Go to **System Settings** → **Privacy & Security**
3. Click **"Open Anyway"** next to the blocked message
4. Enter your password

---

## Full Installation Steps

1. Download `Snapchat-Organizer-macOS.dmg` from the [releases page](https://github.com/M0hammedHaris/snapchat-organizer-desktop/releases)
2. Double-click the DMG to mount it
3. Drag "Snapchat Organizer" to your Applications folder
4. Use one of the security bypass options above (one-time)
5. Launch the app

---

## First Launch

1. **Onboarding Carousel** — Walks you through the app's key features
2. **License Registration** — Register for free or skip to continue with Free tier
3. **Help System** — Press **F1** at any time for step-by-step guidance

---

## Why the Security Warning Appears

macOS Gatekeeper blocks apps that aren't notarized with an Apple Developer certificate ($99/year). This is standard for all indie applications not distributed through the Mac App Store.

**The app is safe:**
- All processing happens locally on your Mac
- No data is uploaded anywhere
- Crash reports (via Sentry) contain only error data, never your files
- Code signing is planned for the production release

---

## Troubleshooting

### "Snapchat Organizer is damaged and can't be opened"
Run in Terminal:
```bash
xattr -cr "/Applications/Snapchat Organizer.app"
```

### App won't open at all
1. Check macOS version (10.13+ required)
2. Try downloading the DMG again
3. Verify the DMG integrity after download

### Slow first launch
Normal for PyInstaller apps — subsequent launches are faster.

---

## Need Help?

- [Create an Issue](https://github.com/M0hammedHaris/snapchat-organizer-desktop/issues/new)
- Check the [Beta Testing Guide](BETA_TESTING_GUIDE.md)
