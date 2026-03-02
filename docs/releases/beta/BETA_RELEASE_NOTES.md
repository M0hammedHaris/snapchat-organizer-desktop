# Snapchat Organizer Desktop v1.0.0-beta.1

## Beta Release - Wider Testing Phase

This beta release builds on Alpha v1.0.2 with a subscription licensing system, onboarding experience, dynamic theming, and crash reporting.

---

## What's New (since Alpha)

### Subscription Licensing System
- **Free / Pro / Premium** tiers with Stripe integration
- Feature gating based on tier (download limits, tool access)
- Device management (1-3 devices depending on tier)
- Login/Register/Skip workflow on first launch

### Onboarding Carousel
- Guided first-run experience walking users through features
- One-time display with option to revisit from Help menu

### Dynamic Light/Dark Theme
- Auto-detects system appearance (light or dark)
- Real-time monitoring — switches without restart
- 500+ line QSS stylesheets for professional look

### Crash Reporting (Sentry)
- Automatic error capture in both main and background threads
- OS/Python version tagging for faster triage
- No personal data or files are ever sent

### UI/UX Improvements
- Consistent styling across all dialogs
- Tab icons for visual organization
- Improved checkbox visibility in both themes
- Better layout spacing and alignment

---

## Downloads

| Platform | File | Requirements |
|----------|------|-------------|
| macOS | `Snapchat-Organizer-macOS.dmg` | macOS 10.13+ |
| Windows | `Snapchat-Organizer-Windows.zip` | Windows 10/11 |
| Linux | `Snapchat-Organizer-Linux.tar.gz` | Ubuntu 20.04+ |

### Installation Notes

**macOS:** Right-click → Open on first launch (Gatekeeper bypass).  
**Windows:** Extract ZIP first, then "More info" → "Run anyway" on SmartScreen.  
**Linux:** May need `libxcb-xinerama0` and `libxcb-cursor0`.

---

## All Features

- Download Snapchat memories from HTML exports
- Organize chat media by person with 3-tier smart matching
- 6 utility tools (Verify, Dedup, Year, Timestamps, Timezone*, Overlays*)
- Configurable settings with persistence
- Built-in help system (F1)
- Dynamic light/dark theme
- Subscription-based feature gating

*Timezone and Overlay tools are placeholders — coming in a future update.

---

## Known Limitations

- Timezone conversion and overlay compositing tools are not yet functional
- App is not code-signed (security warnings on first launch are expected)
- First launch may be slow due to PyInstaller extraction
- Large exports (100GB+) may be slow to process

---

## Feedback

Please report bugs and share feedback:
- **Issues:** https://github.com/M0hammedHaris/snapchat-organizer-desktop/issues/new
- **Discussions:** https://github.com/M0hammedHaris/snapchat-organizer-desktop/discussions

---

**Version:** 1.0.0-beta.1  
**Release Date:** February 2026  
**Copyright:** © 2026 Mohammed Haris. All rights reserved.
