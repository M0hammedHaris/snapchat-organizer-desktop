# macOS Gatekeeper Issue Fix

**Issue:** "Apple could not verify Snapchat Organizer is free of malware"  
**Cause:** App is not code-signed  
**Solutions:** Multiple approaches below

---

## 🚨 Immediate Solution for Users

### Method 1: Right-Click Open (Easiest)

1. **Locate the app** in Finder (in Applications or Downloads)
2. **Right-click** (or Control-click) on "Snapchat Organizer.app"
3. Click **"Open"** from the menu
4. A dialog will appear with "Open" button - click it
5. App will now run and be trusted permanently

### Method 2: System Settings Override

1. Try to open the app normally (double-click)
2. When blocked, click **"OK"**
3. Open **System Settings** → **Privacy & Security**
4. Scroll down to find "Snapchat Organizer was blocked..."
5. Click **"Open Anyway"**
6. Confirm with your password
7. The app will now open

### Method 3: Remove Quarantine Attribute (Terminal)

```bash
# Remove the quarantine flag from the downloaded app
xattr -cr "/Applications/Snapchat Organizer.app"

# Then double-click to open normally
```

---

## 🔧 Long-Term Fix for Developer

### Option A: Ad-hoc Code Signing (Free, Quick)

This signs the app locally so it won't be blocked by Gatekeeper on your machine:

```bash
# Sign with ad-hoc signature
codesign --force --deep --sign - "dist/Snapchat Organizer.app"

# Verify signing
codesign -dv "dist/Snapchat Organizer.app"
```

**Pros:** Free, immediate  
**Cons:** Only works on YOUR Mac, users still see warning

### Option B: Apple Developer Code Signing (Recommended)

**Cost:** $99/year for Apple Developer Program  
**Setup Time:** 1-2 hours  
**Benefits:** Users can download and run without warnings

#### Steps:

1. **Join Apple Developer Program**
   - https://developer.apple.com/programs/
   - Cost: $99/year
   - Wait for approval (usually 24-48 hours)

2. **Create Developer ID Certificate**
   ```bash
   # Request certificate in Xcode or Keychain Access
   # Download from developer.apple.com
   # Install in Keychain
   ```

3. **Update build script to sign the app**
   ```bash
   # Sign the app bundle
   codesign --force --deep \
     --sign "Developer ID Application: Your Name (TEAM_ID)" \
     --options runtime \
     --timestamp \
     "dist/Snapchat Organizer.app"
   
   # Notarize with Apple (required for macOS 10.15+)
   xcrun notarytool submit "dist/Snapchat Organizer.dmg" \
     --apple-id "your@email.com" \
     --team-id "TEAM_ID" \
     --password "app-specific-password"
   
   # Staple notarization ticket
   xcrun stapler staple "dist/Snapchat Organizer.app"
   ```

4. **Verify**
   ```bash
   # Check signature
   codesign -dv "dist/Snapchat Organizer.app"
   
   # Check notarization
   spctl -a -vv "dist/Snapchat Organizer.app"
   ```

### Option C: Auto-updater with Code Signing (Future)

For production release, integrate Sparkle or similar:
- Automatic updates
- Built-in code signing verification
- Better user experience

---

## 📝 Update Build Script

Add ad-hoc signing to `scripts/build_macos.sh`:

```bash
# After PyInstaller build succeeds:

echo "🔐 Signing the app bundle..."
codesign --force --deep --sign - "dist/Snapchat Organizer.app"

if [ $? -eq 0 ]; then
    echo "✅ App signed successfully (ad-hoc)"
else
    echo "⚠️  Signing failed, but build is complete"
fi
```

---

## 🎯 Recommendations

### For Alpha Testing (Current)
✅ **Use Method 1 (Right-Click Open)** and include instructions in README  
✅ Add ad-hoc signing to build script for local testing  
❌ Don't pay $99 yet - wait until ready for public release

### For Beta Testing
✅ Consider Apple Developer Program  
✅ Implement proper code signing + notarization  
✅ Test on multiple Macs to ensure compatibility

### For Production Release
✅ **Required:** Apple Developer Program + notarization  
✅ Consider auto-updater framework  
✅ Submit to Mac App Store (optional)

---

## 📧 Updated User Instructions

Add this to your alpha tester emails:

```markdown
### 🍎 macOS Users: First Launch Instructions

Due to Apple's security policies, you'll need to do this on first launch:

1. Download the .dmg file
2. Open it and drag "Snapchat Organizer" to Applications
3. **Right-click** the app in Applications
4. Choose **"Open"** from the menu
5. Click **"Open"** in the dialog that appears

After this one-time step, you can open the app normally!

Alternatively, run this command in Terminal:
```bash
xattr -cr "/Applications/Snapchat Organizer.app"
```

Then double-click to open.
```

---

## 🔗 Resources

- [Apple Code Signing Guide](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)
- [PyInstaller macOS Signing](https://pyinstaller.org/en/stable/usage.html#macos-code-signing)
- [Notarization Overview](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution/customizing_the_notarization_workflow)

---

**Last Updated:** January 12, 2026
