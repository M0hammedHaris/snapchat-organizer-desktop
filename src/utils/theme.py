"""Theme management utility.

This module handles theme detection and application, supporting both
light and dark modes based on system settings.
"""

from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt
# Try to import optional darkdetect library for system theme detection
try:
    import darkdetect
    DARKDETECT_AVAILABLE = True
except ImportError:
    DARKDETECT_AVAILABLE = False
    darkdetect = None  # Set to None for safety

from .logger import get_logger

logger = get_logger(__name__)

# Constants
THEME_DARK = "dark"
THEME_LIGHT = "light"

# Stylesheet paths
STYLES_DIR = Path(__file__).parent.parent.parent / "resources" / "styles"
DARK_STYLESHEET = STYLES_DIR / "dark.qss"
LIGHT_STYLESHEET = STYLES_DIR / "light.qss"


def is_dark_system_theme() -> bool:
    """Check if the system is currently in dark mode.
    
    Returns:
        True if dark mode, False otherwise (defaulting to True if unknown for this app style)
    """
    try:
        # Try asking Qt first (reliable on macOS/Windows in newer Qt versions)
        app = QApplication.instance()
        if app:
            palette = app.palette()
            # Check window text color brightness 
            # (Dark themes usually have light text)
            text_color = palette.color(QPalette.WindowText)
            if text_color.lightness() > 128:
                return True
                
        # Fallback to darkdetect if available
        if DARKDETECT_AVAILABLE and darkdetect.isDark():
            return True
            
    except Exception as e:
        logger.debug(f"Theme detection error: {e}")
        
    return False


def apply_theme(app: QApplication, theme_name: str = None) -> None:
    """Apply the specified theme to the application.
    
    Args:
        app: The QApplication instance
        theme_name: 'dark' or 'light'. If None, auto-detects.
    """
    if theme_name is None:
        theme_name = THEME_DARK if is_dark_system_theme() else THEME_LIGHT
        
    logger.info(f"Applying theme: {theme_name}")
    
    stylesheet_path = DARK_STYLESHEET if theme_name == THEME_DARK else LIGHT_STYLESHEET
    
    try:
        if stylesheet_path.exists():
            with open(stylesheet_path, "r") as f:
                app.setStyleSheet(f.read())
            logger.info(f"Loaded stylesheet from {stylesheet_path}")
            
            # Set a property on the app to track current theme
            app.setProperty("theme", theme_name)
        else:
            logger.warning(f"Stylesheet not found at {stylesheet_path}")
            
    except Exception as e:
        logger.error(f"Failed to apply theme: {e}")


def toggle_theme(app: QApplication) -> str:
    """Toggle between light and dark themes.
    
    Args:
        app: The QApplication instance
        
    Returns:
        The new theme name ('dark' or 'light')
    """
    current_theme = app.property("theme") or THEME_DARK
    new_theme = THEME_LIGHT if current_theme == THEME_DARK else THEME_DARK
    
    apply_theme(app, new_theme)
    return new_theme
