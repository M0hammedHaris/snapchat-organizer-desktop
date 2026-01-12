# 🍎 macOS Installation & First Launch

**Quick Fix:** If you see "Apple could not verify..." warning:

## ✅ Solution (Choose One)

### Option 1: Right-Click Open (Recommended)
1. **Right-click** "Snapchat Organizer" in Applications
2. Click **"Open"**
3. Click **"Open"** again in the security dialog
4. App will now run! (Only need to do this once)

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

## 📦 Full Installation Steps

1. Download `Snapchat-Organizer-macOS.dmg`
2. Double-click the DMG to open it
3. Drag "Snapchat Organizer" to Applications folder
4. Use one of the security bypass options above
5. Launch the app!

---

## ❓ Why This Happens

This warning appears because the app isn't code-signed with an Apple Developer certificate. This is normal for free/open-source apps. The app is safe - it's just Apple's way of protecting users from unknown developers.

---

## 🆘 Still Having Issues?

Check the full troubleshooting guide:
- [MACOS_GATEKEEPER_FIX.md](docs/releases/alpha/MACOS_GATEKEEPER_FIX.md)
- Create an issue: https://github.com/M0hammedHaris/snapchat-organizer-desktop/issues

---

**Happy organizing! 📸**
