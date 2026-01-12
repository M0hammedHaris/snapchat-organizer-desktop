# First-Run Experience Implementation

## Overview
Implemented a comprehensive first-run detection system that automatically displays the help dialog when users launch the application for the first time. This improves user onboarding by guiding them through the Snapchat data download process.

## Features Implemented

### 1. First-Run Detection System
**Location:** `src/utils/config.py`

Added the following functionality:

- **FIRST_RUN_MARKER**: File marker at `~/.snapchat-organizer/.first_run_complete`
- **CONFIG_FILE**: JSON config at `~/.snapchat-organizer/config.json`

#### Functions:
```python
is_first_run() -> bool
    """Check if this is the first time running the application."""

mark_first_run_complete() -> None
    """Mark the first run as complete."""

should_show_help_on_startup() -> bool
    """Check if help dialog should be shown on startup."""

set_show_help_on_startup(show: bool) -> None
    """Set whether to show help dialog on startup."""
```

### 2. Main Window Integration
**Location:** `src/gui/main_window.py`

#### Changes:
- Imported first-run detection functions from config
- Added `_check_first_run()` method to handle first-run logic
- Uses `QTimer.singleShot(500, ...)` to show help dialog after window is fully initialized
- Help dialog shown with "Don't show this again" checkbox on first run
- Regular help access (F1 key) shows help without the checkbox

#### Code Flow:
```
1. Main window initializes
2. QTimer waits 500ms for window to fully render
3. _check_first_run() is called
4. If first run or user preference is set:
   - Show HelpDialog with checkbox
   - Save user preference if "don't show again" is checked
   - Mark first run as complete
```

### 3. Help Dialog Enhancement
**Location:** `src/gui/help_dialog.py`

#### Changes:
- Added `show_dont_show_again` parameter to constructor
- Conditionally displays "Don't show this again on startup" checkbox
- Added `_on_dont_show_changed()` handler to track checkbox state
- `dont_show_again` attribute accessible after dialog closes

#### Color Scheme Update:
Updated all HTML content to use professional blue/gray palette:

**Primary Colors:**
- Primary Blue: `#3498db` (buttons, accents, borders)
- Dark Text: `#2c3e50` (headings, body text)
- Medium Text: `#34495e` (subheadings)
- Light Gray: `#7f8c8d` (tertiary text)
- Light Background: `#ecf0f1` (cards, steps)

**Semantic Colors:**
- Success/Tip: `#27ae60` (green)
- Warning: `#f39c12` (orange)
- Error/Critical: `#e74c3c` (red)

## Testing

### Automated Tests
Created `test_first_run.py` to verify all functionality:

```bash
python test_first_run.py
```

**Test Coverage:**
1. ✅ First run detection (before marker exists)
2. ✅ Mark first run complete (creates marker file)
3. ✅ Default behavior after first run (don't show help)
4. ✅ User opts to show help again (config file updated)
5. ✅ User opts not to show help (config file updated)

All tests passed successfully! ✅

### Manual Testing Steps

1. **Test First Run:**
   ```bash
   # Remove marker and config to simulate fresh install
   rm ~/.snapchat-organizer/.first_run_complete
   rm ~/.snapchat-organizer/config.json
   
   # Launch app
   python -m src.main
   ```
   - Help dialog should appear automatically after 500ms
   - Checkbox should be visible: "Don't show this again on startup"

2. **Test "Don't Show Again":**
   - Check the checkbox
   - Close dialog
   - Restart app
   - Help dialog should NOT appear

3. **Test Manual Help Access:**
   - Press F1 or use Help → How to Download Snapchat Data
   - Help dialog should appear WITHOUT checkbox
   - Can be accessed anytime regardless of first-run status

## Files Modified

### Core Implementation
1. **src/utils/config.py** (+78 lines)
   - Added FIRST_RUN_MARKER and CONFIG_FILE constants
   - Added 4 new functions for first-run detection and config management

2. **src/gui/main_window.py** (+24 lines)
   - Imported first-run detection functions
   - Added QTimer-based first-run check
   - Added `_check_first_run()` method with preference handling

3. **src/gui/help_dialog.py** (+20 lines, ~100 color updates)
   - Added conditional checkbox display
   - Updated all HTML color schemes from yellow to blue/gray
   - Added state tracking for "don't show again" preference

### Testing
4. **test_first_run.py** (new file, 109 lines)
   - Comprehensive test suite for first-run functionality
   - 5 test cases covering all scenarios

## User Experience Flow

### First Launch (New User)
```
1. User launches app
2. Main window appears
3. After 500ms delay:
   → Help dialog opens automatically
   → Shows comprehensive Snapchat download guide
   → Displays "Don't show this again" checkbox
4. User reads guide and closes dialog
5. If checkbox was checked:
   → Preference saved to config.json
   → Help won't show on next startup
6. First run marked complete (.first_run_complete created)
```

### Subsequent Launches (Returning User)
```
1. User launches app
2. Main window appears
3. No automatic help dialog (unless user re-enabled it)
4. Help still accessible via:
   - Press F1
   - Menu: Help → How to Download Snapchat Data
```

### Re-enabling Help on Startup
```
1. User can manually edit config.json:
   {
     "show_help_on_startup": true
   }
2. Or use Settings dialog (future enhancement)
```

## Configuration Files

### ~/.snapchat-organizer/.first_run_complete
- Empty marker file
- Presence indicates app has been run before
- Deletion simulates fresh install for testing

### ~/.snapchat-organizer/config.json
```json
{
  "show_help_on_startup": false
}
```
- Persistent user preferences
- `show_help_on_startup`: Controls automatic help display
- Future settings will be added to this file

## Benefits

1. **Improved Onboarding**: New users immediately see how to get their Snapchat data
2. **Non-Intrusive**: One-time display with opt-out option
3. **Always Accessible**: Help always available via F1 or menu
4. **Persistent Preferences**: User choice is remembered across sessions
5. **Clean Implementation**: No external dependencies, uses Qt's built-in timer
6. **Testable**: Comprehensive test suite ensures reliability

## Future Enhancements

1. **Settings Dialog Integration**: Add toggle in Settings → General tab
2. **Welcome Wizard**: Multi-step onboarding for new users
3. **Tips of the Day**: Optional tips shown on startup
4. **Version-Specific Help**: Show help when major updates are available

## Technical Notes

### Why QTimer.singleShot?
Using a 500ms delay ensures:
- Main window is fully rendered and visible
- Dialog appears smoothly without UI glitches
- Event loop is properly initialized
- Works consistently across different platforms (macOS, Windows, Linux)

### Config File Format
JSON was chosen for:
- Human-readable and editable
- Native Python support (no extra dependencies)
- Easy to extend with new settings
- Compatible with future web-based config tools

### Thread Safety
All config operations are synchronous and called from the main thread, ensuring no race conditions.

## Conclusion

The first-run experience implementation is complete and fully tested. It provides a smooth onboarding experience while respecting user preferences and maintaining clean code architecture. The system is ready for production use and can be easily extended with additional features in future phases.

**Status**: ✅ Complete and Tested
**Version**: 1.0.0-alpha
**Last Updated**: 2024-01-09
