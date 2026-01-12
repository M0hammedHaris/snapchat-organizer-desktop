# Distribution Package Instructions for Alpha Testing

**Created:** January 12, 2026  
**Target:** Friends & Family Alpha Testing  
**Version:** 1.0.0-alpha

---

## 📦 How to Package for Distribution

### Option 1: Simple ZIP Distribution (Recommended for Alpha)

This is the easiest way to share the app with friends for testing.

```bash
# 1. Navigate to project root
cd /path/to/snapchat-organizer-desktop

# 2. Create a clean distribution package
zip -r snapchat-organizer-alpha.zip \
  src/ \
  docs/ \
  tests/ \
  resources/ \
  requirements.txt \
  README_ALPHA.md \
  ALPHA_TESTING_GUIDE.md \
  LICENSE \
  -x "*.pyc" \
  -x "__pycache__/*" \
  -x ".git/*" \
  -x ".venv/*" \
  -x "*.log"

# 3. The file snapchat-organizer-alpha.zip is ready to share!
```

---

## 📧 Sharing Instructions for Your Friends

### Email Template

```
Subject: Alpha Test - Snapchat Organizer Desktop

Hey [Friend's Name]!

I've been working on a desktop app to organize Snapchat memories and 
chat media, and I'd love your help testing it!

🎯 What it does:
- Downloads Snapchat memories from data exports
- Organizes chat media by person
- Removes duplicates and verifies file integrity
- Fixes timestamps and organizes by year

📦 Attached: snapchat-organizer-alpha.zip

📖 Getting Started:
1. Extract the ZIP file
2. Open the extracted folder
3. Read README_ALPHA.md for installation steps
4. Follow ALPHA_TESTING_GUIDE.md for detailed instructions

⚙️ Requirements:
- Python 3.11 or higher (https://www.python.org/downloads/)
- macOS, Windows, or Linux
- Your Snapchat data export (instructions in the guide)

⏱️ Time Estimate:
- Setup: 5-10 minutes
- Testing: 30-60 minutes
- Feedback: 10 minutes

🐛 Found issues? Create a GitHub issue or email me directly!

Thanks for helping make this better! 🙏

Best,
[Your Name]
```

---

## 📋 What's Included in the Package

```
snapchat-organizer-alpha.zip
├── src/                          # Application source code
│   ├── gui/                     # User interface
│   ├── core/                    # Backend logic
│   ├── workers/                 # Background threads
│   └── utils/                   # Utilities & config
├── docs/                        # Technical documentation
├── tests/                       # Test suite
├── resources/                   # Icons & resources (empty for now)
├── requirements.txt             # Python dependencies
├── README_ALPHA.md              # Quick start guide
├── ALPHA_TESTING_GUIDE.md       # Detailed user manual
└── LICENSE                      # License file
```

---

## 🎯 Pre-Distribution Checklist

Before sending to testers:

### Code Quality
- [x] All Phase 1 features complete
- [x] Settings persistence working
- [x] First-run experience tested
- [x] Error handling in place
- [x] Logging configured
- [ ] Remove debug print statements (if any)

### Documentation
- [x] README_ALPHA.md created
- [x] ALPHA_TESTING_GUIDE.md created
- [x] Installation instructions clear
- [x] Troubleshooting section complete
- [x] Testing checklist provided

### Files & Structure
- [x] .gitignore configured (excludes .venv, __pycache__, logs)
- [x] requirements.txt up to date
- [x] No sensitive data in source code
- [ ] Test on fresh machine (if possible)

### User Experience
- [x] Help dialog shows on first run
- [x] Settings persist across sessions
- [x] Default tab is Download
- [x] All tabs functional
- [ ] App icon (optional - can add later)

---

## 🖥️ Platform-Specific Notes

### macOS Users

Include these additional notes:

```markdown
### macOS Security Note

When you first run the app, macOS may show a security warning 
because it's not signed. To run it:

1. Go to System Preferences → Security & Privacy
2. Click "Open Anyway" next to the blocked message
3. Or use Terminal: `python3 src/main.py`

This is normal for alpha software. A signed version will be 
available in the public release.
```

### Windows Users

Include these notes:

```markdown
### Windows Setup

1. Install Python 3.11 from python.org
   - ✅ Check "Add Python to PATH" during installation
2. Open Command Prompt (cmd.exe)
3. Navigate to extracted folder:
   ```
   cd C:\path\to\snapchat-organizer-desktop
   ```
4. Follow installation steps in README_ALPHA.md

Note: Windows Defender may flag the app initially. This is a 
false positive - the app is safe and doesn't access the internet.
```

### Linux Users

Include these notes:

```markdown
### Linux Setup

1. Install Python 3.11+ from your package manager:
   ```bash
   sudo apt update
   sudo apt install python3.11 python3.11-venv
   ```

2. Install Qt dependencies:
   ```bash
   sudo apt install libxcb-xinerama0 libxcb-cursor0
   ```

3. Follow standard installation steps in README_ALPHA.md
```

---

## 📊 Tracking Alpha Testing

### Create a Feedback Spreadsheet

Track who's testing and their feedback:

| Tester Name | Platform | Date Sent | Date Started | Status | Issues Reported | Rating |
|-------------|----------|-----------|--------------|--------|-----------------|--------|
| John Doe    | macOS    | Jan 12    | Jan 13       | Testing| 2               | -      |
| Jane Smith  | Windows  | Jan 12    | -            | Pending| -               | -      |

### Feedback Collection

Create a simple Google Form or GitHub Issue template:

**Questions to Ask:**
1. What platform did you use? (macOS/Windows/Linux)
2. Did installation go smoothly? (Yes/No/Issues)
3. Which features did you test? (Check all: Download/Organize/Tools)
4. What worked well?
5. What was confusing or broken?
6. What features are you most excited about?
7. Would you pay for this? If yes, how much?
8. Overall rating (1-5 stars)
9. Any other comments?

---

## 🚀 Distribution Channels

### For Friends & Family (Private Alpha)

1. **Email** - Send ZIP file directly (if <25MB)
2. **Google Drive** - Share link with edit permissions disabled
3. **Dropbox** - Create shared link
4. **WeTransfer** - For larger files
5. **GitHub Release** - Create a private pre-release

### Example: GitHub Private Release

```bash
# 1. Create a git tag
git tag v1.0.0-alpha
git push origin v1.0.0-alpha

# 2. Go to GitHub → Releases → Draft a new release
# 3. Select tag: v1.0.0-alpha
# 4. Title: "Alpha Release - Private Testing"
# 5. Description:
```

**Release Description Template:**

```markdown
# Snapchat Organizer Desktop v1.0.0-alpha

**⚠️ ALPHA VERSION - PRIVATE TESTING ONLY**

This is a private alpha release for invited testers only. 
Please do not share this software publicly.

## What's New
- ✅ Download memories from HTML exports
- ✅ Organize chat media by person
- ✅ 4 utility tools (verify, dedup, year, timestamp)
- ✅ Settings persistence
- ✅ First-run help experience

## Installation
See README_ALPHA.md in the ZIP file

## Providing Feedback
Please create issues in this repo or email me directly

## Known Limitations
- Timezone conversion tool not yet implemented
- Overlay application tool not yet implemented
- No app icon yet
- Large files (>100GB) may be slow

**Thank you for testing! 🙏**
```

---

## 🎁 Optional: Create a Landing Page

For a more professional distribution:

### Simple HTML Landing Page

```html
<!DOCTYPE html>
<html>
<head>
  <title>Snapchat Organizer Desktop - Alpha</title>
  <style>
    body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
    .hero { text-align: center; padding: 40px 0; }
    .cta-button { background: #3498db; color: white; padding: 15px 30px; 
                  text-decoration: none; border-radius: 5px; display: inline-block; }
    .feature { margin: 20px 0; }
  </style>
</head>
<body>
  <div class="hero">
    <h1>📸 Snapchat Organizer Desktop</h1>
    <p>Organize your Snapchat memories and chat media with ease</p>
    <a href="snapchat-organizer-alpha.zip" class="cta-button">
      Download Alpha (v1.0.0)
    </a>
  </div>
  
  <h2>Features</h2>
  <div class="feature">✅ Download memories from exports</div>
  <div class="feature">✅ Organize chat media by person</div>
  <div class="feature">✅ Remove duplicates automatically</div>
  <div class="feature">✅ Fix timestamps & organize by year</div>
  
  <h2>Requirements</h2>
  <ul>
    <li>Python 3.11 or higher</li>
    <li>macOS, Windows, or Linux</li>
    <li>Your Snapchat data export</li>
  </ul>
  
  <h2>Need Help?</h2>
  <p>Check the included ALPHA_TESTING_GUIDE.md or contact me!</p>
</body>
</html>
```

Host this on:
- GitHub Pages (free)
- Netlify (free)
- Your own domain

---

## 📞 Support Plan for Alpha Testers

Be prepared to help testers:

### 1. Be Responsive
- Check email/messages daily
- Respond to questions within 24 hours
- Be patient with non-technical users

### 2. Common Issues & Fixes

**"Python not found"**
```bash
# Solution: Install Python 3.11+ from python.org
```

**"No module named PySide6"**
```bash
# Solution: Activate venv and reinstall dependencies
source .venv/bin/activate
pip install -r requirements.txt
```

**"App won't start"**
```bash
# Solution: Run from terminal to see errors
cd snapchat-organizer-desktop
python src/main.py
```

### 3. Escalation Path
1. Check ALPHA_TESTING_GUIDE.md first
2. Search existing GitHub issues
3. Create new GitHub issue
4. Email you directly (for urgent matters)

---

## 📈 Success Metrics for Alpha

Track these metrics:

- **Installation Success Rate**: % who successfully installed
- **Feature Usage**: Which features are most used
- **Bug Reports**: Number and severity of bugs found
- **User Satisfaction**: Average rating from feedback
- **Completion Rate**: % who completed testing checklist
- **Retention**: % who use it more than once

---

## 🎯 Next Steps After Alpha

1. **Collect Feedback** (1-2 weeks)
2. **Fix Critical Bugs** (prioritize by severity)
3. **Iterate on UX** (based on user confusion)
4. **Add Polish** (Phase 2 features)
5. **Prepare Beta** (wider distribution)
6. **Plan Public Launch** (ProductHunt, etc.)

---

## ✅ Final Pre-Send Checklist

Before hitting send:

- [ ] ZIP file created and tested (can extract & run)
- [ ] README_ALPHA.md reviewed for clarity
- [ ] ALPHA_TESTING_GUIDE.md complete
- [ ] Email template personalized
- [ ] Feedback collection method ready (form/issues)
- [ ] Support plan in place (you're ready to help)
- [ ] Tested on at least one platform yourself
- [ ] Git repo up to date and backed up
- [ ] Excited to get feedback! 🎉

---

**You're ready to distribute! Good luck with alpha testing! 🚀**
