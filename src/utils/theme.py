from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt, QObject, Signal, QTimer
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


class ThemeManager(QObject):
    """Manages application theme and monitors system theme changes."""
    
    theme_changed = Signal(str)
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super(ThemeManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize theme manager."""
        if self._initialized:
            return
            
        super().__init__()
        self._current_theme = None
        self._timer = QTimer()
        self._timer.timeout.connect(self._check_system_theme)
        self._initialized = True
        logger.debug("ThemeManager initialized")
        
    def start_monitoring(self, interval_ms: int = 1000):
        """Start monitoring system theme changes.
        
        Args:
            interval_ms: Check interval in milliseconds
        """
        self._timer.start(interval_ms)
        logger.debug(f"Started monitoring system theme (interval: {interval_ms}ms)")
        
    def stop_monitoring(self):
        """Stop monitoring system theme changes."""
        self._timer.stop()
        logger.debug("Stopped monitoring system theme")
        
    def _check_system_theme(self):
        """Check if system theme has changed."""
        system_is_dark = is_dark_system_theme()
        expected_theme = THEME_DARK if system_is_dark else THEME_LIGHT
        
        if self._current_theme != expected_theme:
            logger.info(f"System theme changed to {expected_theme}")
            app = QApplication.instance()
            if app:
                self.apply_theme(app, expected_theme)

    def apply_theme(self, app: QApplication, theme_name: str = None) -> None:
        """Apply the specified theme to the application.
        
        Args:
            app: The QApplication instance
            theme_name: 'dark' or 'light'. If None, auto-detects.
        """
        if theme_name is None:
            theme_name = THEME_DARK if is_dark_system_theme() else THEME_LIGHT
            
        if self._current_theme == theme_name:
            return
            
        logger.info(f"Applying theme: {theme_name}")
        
        stylesheet_path = DARK_STYLESHEET if theme_name == THEME_DARK else LIGHT_STYLESHEET
        
        try:
            if stylesheet_path.exists():
                with open(stylesheet_path, "r") as f:
                    app.setStyleSheet(f.read())
                logger.info(f"Loaded stylesheet from {stylesheet_path}")
                
                # Set a property on the app to track current theme
                app.setProperty("theme", theme_name)
                self._current_theme = theme_name
                self.theme_changed.emit(theme_name)
            else:
                logger.warning(f"Stylesheet not found at {stylesheet_path}")
                
        except Exception as e:
            logger.error(f"Failed to apply theme: {e}")


def is_dark_system_theme() -> bool:
    """Check if the system is currently in dark mode.
    
    Returns:
        True if dark mode, False otherwise (defaulting to True if unknown for this app style)
    """
    try:
        # Fallback to darkdetect if available (most reliable for macOS/Windows)
        if DARKDETECT_AVAILABLE and darkdetect.isDark():
            return True
            
        # Try asking Qt as backup
        app = QApplication.instance()
        if app:
            palette = app.palette()
            # Check window text color brightness 
            # (Dark themes usually have light text)
            text_color = palette.color(QPalette.WindowText)
            if text_color.lightness() > 128:
                return True
            
    except Exception as e:
        logger.debug(f"Theme detection error: {e}")
        
    return False


# Global convenience function
def apply_theme(app: QApplication, theme_name: str = None) -> None:
    """Convenience wrapper for ThemeManager.apply_theme."""
    manager = ThemeManager()
    manager.apply_theme(app, theme_name)

