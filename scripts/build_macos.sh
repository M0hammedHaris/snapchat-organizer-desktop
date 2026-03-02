#!/bin/bash
# Build script for Snapchat Organizer Desktop
# Creates a standalone .app bundle for macOS

set -e  # Exit on error

echo "🔨 Building Snapchat Organizer Desktop for macOS..."
echo ""

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "❌ PyInstaller not found. Installing..."
    pip install pyinstaller>=6.0.0
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/
rm -rf dist/

# Build the app
echo "📦 Building application..."
pyinstaller snapchat-organizer.spec --clean --noconfirm

# Check if build was successful
if [ -d "dist/Snapchat Organizer.app" ]; then
    echo ""
    echo "✅ Build successful!"
    echo "📂 Location: dist/Snapchat Organizer.app"
    echo ""
    
    # Ad-hoc code signing (prevents Gatekeeper warnings on your Mac)
    echo "🔐 Signing app bundle..."
    codesign --force --deep --sign - "dist/Snapchat Organizer.app" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo "✅ App signed (ad-hoc)"
    else
        echo "⚠️  Signing skipped (codesign not available)"
    fi
    echo ""
    
    # Get size
    SIZE=$(du -sh "dist/Snapchat Organizer.app" | cut -f1)
    echo "📊 Size: $SIZE"
    echo ""
    
    # Create DMG (optional)
    read -p "Create DMG installer? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📀 Creating DMG..."
        
        # Create temporary directory for DMG contents
        mkdir -p dist/dmg
        cp -R "dist/Snapchat Organizer.app" dist/dmg/
        
        # Create DMG
        hdiutil create -volname "Snapchat Organizer" \
                       -srcfolder dist/dmg \
                       -ov -format UDZO \
                       "dist/Snapchat-Organizer-1.0.0-beta.1.dmg"
        
        rm -rf dist/dmg
        
        echo "✅ DMG created: dist/Snapchat-Organizer-1.0.0-beta.1.dmg"
    fi
    
    echo ""
    echo "🎉 Build complete!"
    echo ""
    echo "To test the app:"
    echo "  open 'dist/Snapchat Organizer.app'"
    echo ""
    
else
    echo "❌ Build failed. Check the error messages above."
    exit 1
fi
