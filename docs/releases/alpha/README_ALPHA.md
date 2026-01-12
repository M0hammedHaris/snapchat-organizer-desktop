# 🎯 Snapchat Organizer Desktop - Quick Start

**Version:** 1.0.0-alpha  
**Platform:** macOS, Windows, Linux  
**Status:** Alpha Testing

> **Organize your Snapchat memories and chat media with ease!**

---

## ⚡ Quick Install (3 Steps)

```bash
# 1. Create virtual environment
python3 -m venv .venv

# 2. Activate it
source .venv/bin/activate  # macOS/Linux
# OR
.venv\Scripts\activate     # Windows

# 3. Install and run
pip install -r requirements.txt
python src/main.py
```

---

## 🎁 What You Get

✅ **Download** Snapchat memories from HTML exports  
✅ **Organize** chat media by person/conversation  
✅ **Remove** duplicate files automatically  
✅ **Verify** image integrity  
✅ **Fix** timestamps and organize by year  
✅ **100% Local** - Your data never leaves your computer

---

## 📖 Full Documentation

For detailed instructions, troubleshooting, and testing checklist:

👉 **[Read the Alpha Testing Guide](ALPHA_TESTING_GUIDE.md)**

---

## 🐛 Found a Bug?

**[Report it here](https://github.com/M0hammedHaris/snapchat-organizer-desktop/issues)**

Please include:
- What you were doing
- What happened
- What you expected
- Log file from `~/.snapchat-organizer/logs/app.log`

---

## 💬 Getting Help

- **First-time users**: Press `F1` in the app for built-in help
- **Settings**: Press `Ctrl+,` (or `Cmd+,` on Mac)
- **Questions**: Check [ALPHA_TESTING_GUIDE.md](ALPHA_TESTING_GUIDE.md)

---

## 📋 Before You Start

### You'll Need:
1. **Python 3.11+** - [Download here](https://www.python.org/downloads/)
2. **Your Snapchat data export** - [How to get it](https://support.snapchat.com/en-US/a/download-my-data)

### First Time?
1. Request your Snapchat data (Settings → My Data → Submit Request)
2. Wait 1-3 days for email from Snapchat
3. Download and extract the ZIP file
4. Launch this app and follow the help dialog

---

## 🚀 Features Overview

### 📥 Download Tab
Download Snapchat memories from `memories_history.html`

**Options:**
- Adjustable delay between requests
- Resume interrupted downloads
- GPS metadata embedding
- Custom overlays
- Filter by year

### 📂 Organize Tab
Organize chat media by person using smart matching

**Features:**
- 3-tier matching algorithm
- Configurable time window and confidence scores
- Detailed matching reports
- Copy or move files

### 🛠️ Tools Tab
6 utility tools for media management

**Available:**
- ✅ Verify Files (check for corruption)
- ✅ Remove Duplicates (SHA256-based)
- ✅ Organize by Year (EXIF-aware)
- ✅ Fix Timestamps (sync EXIF → file date)
- ⏳ Convert Timezone (coming soon)
- ⏳ Apply Overlays (coming soon)

---

## ⚙️ System Requirements

**Minimum:**
- Python 3.11 or higher
- 4GB RAM
- 1GB free disk space

**Recommended:**
- Python 3.12
- 8GB RAM
- SSD for faster processing

**Tested On:**
- macOS 12+ (Monterey, Ventura, Sonoma)
- Windows 10/11
- Ubuntu 20.04+

---

## 📁 Project Structure

```
snapchat-organizer-desktop/
├── src/                    # Application source code
│   ├── gui/               # PySide6 UI components
│   ├── core/              # Business logic
│   └── utils/             # Utilities and config
├── tests/                 # Test suite
├── docs/                  # Documentation
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── ALPHA_TESTING_GUIDE.md # Detailed user guide
```

---

## 🔒 Privacy & Security

- ✅ **100% offline** - No internet required after installation
- ✅ **No telemetry** - We don't collect any data
- ✅ **No cloud uploads** - Your files stay on your computer
- ✅ **Open for review** - Source code available to testers

---

## 🎯 Roadmap

### Phase 1: MVP (COMPLETE ✅)
- [x] Download tab with HTML parsing
- [x] Organize tab with smart matching
- [x] Tools tab with 4 working tools
- [x] Settings persistence
- [x] Help system & first-run experience

### Phase 2: Polish (In Progress)
- [ ] License system (trial + pro tiers)
- [ ] Complete timezone conversion tool
- [ ] Complete overlay application tool
- [ ] Results viewer widget
- [ ] Performance optimizations

### Phase 3: Distribution
- [ ] macOS app bundle (.app)
- [ ] Windows installer (.exe)
- [ ] Code signing & notarization
- [ ] Auto-update mechanism
- [ ] Public release on ProductHunt

---

## 👥 Credits

**Developed by:** Mohammed Haris  
**Company:** Mac Hive  
**License:** Proprietary - All Rights Reserved

---

## 📞 Contact

- **Issues:** [GitHub Issues](https://github.com/M0hammedHaris/snapchat-organizer-desktop/issues)
- **Email:** [Your Email]
- **Feedback:** We'd love to hear from you!

---

## ⚖️ License

© 2026 Mohammed Haris. All Rights Reserved.

This is proprietary software currently in alpha testing. Unauthorized distribution or modification is prohibited.

---

**🙏 Thank you for alpha testing! Your feedback matters.**

---

### Quick Links

📖 [Full Testing Guide](ALPHA_TESTING_GUIDE.md)  
🐛 [Report Issues](https://github.com/M0hammedHaris/snapchat-organizer-desktop/issues)  
📊 [Development Progress](PROGRESS.md)  
💻 [Technical Documentation](docs/)

---

**Last Updated:** January 12, 2026
