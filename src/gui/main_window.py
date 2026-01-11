"""Main application window with tabbed interface.

This module provides the main window for Snapchat Organizer Desktop,
featuring a tabbed interface for Download, Organize, and Tools functionality.
"""

from typing import Optional
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QMessageBox,
    QMenuBar,
    QMenu,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon

from ..utils.config import (
    APP_NAME,
    APP_VERSION,
    WINDOW_MIN_WIDTH,
    WINDOW_MIN_HEIGHT,
    WINDOW_DEFAULT_WIDTH,
    WINDOW_DEFAULT_HEIGHT,
)
from ..utils.logger import get_logger

logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """Main application window with tabbed interface."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the main window.
        
        Args:
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        
        logger.info(f"Initializing {APP_NAME} v{APP_VERSION}")
        
        self._setup_ui()
        self._create_menu_bar()
        
        logger.debug("Main window initialized")
    
    def _setup_ui(self):
        """Set up the user interface."""
        # Window properties
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(QSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT))
        self.resize(QSize(WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT))
        
        # Central widget with layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(False)
        self.tab_widget.setTabPosition(QTabWidget.North)
        layout.addWidget(self.tab_widget)
        
        # Create placeholder tabs (will be replaced with actual implementations)
        self._add_placeholder_tabs()
        
        logger.debug("UI setup complete")
    
    def _add_placeholder_tabs(self):
        """Add placeholder tabs for development."""
        # Download Tab
        download_placeholder = QWidget()
        download_layout = QVBoxLayout(download_placeholder)
        from PySide6.QtWidgets import QLabel
        download_layout.addWidget(
            QLabel("Download Tab - Coming soon...")
        )
        self.tab_widget.addTab(download_placeholder, "📥 Download Memories")
        
        # Organize Tab
        organize_placeholder = QWidget()
        organize_layout = QVBoxLayout(organize_placeholder)
        organize_layout.addWidget(
            QLabel("Organize Tab - Coming soon...")
        )
        self.tab_widget.addTab(organize_placeholder, "📁 Organize Chat Media")
        
        # Tools Tab
        tools_placeholder = QWidget()
        tools_layout = QVBoxLayout(tools_placeholder)
        tools_layout.addWidget(
            QLabel("Tools Tab - Coming soon...")
        )
        self.tab_widget.addTab(tools_placeholder, "🔧 Tools")
    
    def add_tab(self, widget: QWidget, title: str, index: Optional[int] = None):
        """Add a tab to the tab widget.
        
        Args:
            widget: Widget to add as tab content
            title: Tab title
            index: Optional index to insert tab at
        """
        if index is None:
            self.tab_widget.addTab(widget, title)
        else:
            self.tab_widget.insertTab(index, widget, title)
        
        logger.debug(f"Added tab: {title}")
    
    def remove_tab(self, index: int):
        """Remove a tab from the tab widget.
        
        Args:
            index: Index of tab to remove
        """
        widget = self.tab_widget.widget(index)
        self.tab_widget.removeTab(index)
        
        if widget:
            widget.deleteLater()
        
        logger.debug(f"Removed tab at index {index}")
    
    def _create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        # Settings action
        settings_action = QAction("&Settings", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self._show_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        # Documentation action
        docs_action = QAction("&Documentation", self)
        docs_action.setShortcut("F1")
        docs_action.triggered.connect(self._show_documentation)
        help_menu.addAction(docs_action)
        
        help_menu.addSeparator()
        
        # About action
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
        
        logger.debug("Menu bar created")
    
    def _show_settings(self):
        """Show settings dialog."""
        logger.info("Settings dialog requested")
        QMessageBox.information(
            self,
            "Settings",
            "Settings dialog coming soon!",
        )
    
    def _show_documentation(self):
        """Show documentation."""
        logger.info("Documentation requested")
        QMessageBox.information(
            self,
            "Documentation",
            f"{APP_NAME} Documentation\n\n"
            "Documentation will be available at:\n"
            "https://github.com/M0hammedHaris/snapchat-organizer-desktop",
        )
    
    def _show_about(self):
        """Show about dialog."""
        logger.info("About dialog requested")
        QMessageBox.about(
            self,
            f"About {APP_NAME}",
            f"<h2>{APP_NAME}</h2>"
            f"<p>Version {APP_VERSION}</p>"
            f"<p>Desktop application for downloading and organizing "
            f"Snapchat memories locally.</p>"
            f"<p><b>Features:</b></p>"
            f"<ul>"
            f"<li>Download memories from HTML exports</li>"
            f"<li>Organize chat media by contact</li>"
            f"<li>Apply overlays to recreate Snapchat look</li>"
            f"<li>Preserve GPS metadata</li>"
            f"<li>100% private - all local processing</li>"
            f"</ul>"
            f"<p>© 2026 Mohammed Haris</p>",
        )
    
    def closeEvent(self, event):
        """Handle window close event.
        
        Args:
            event: Close event
        """
        logger.info("Application closing")
        
        # TODO: Check if any operations are in progress
        # For now, just accept the close event
        event.accept()
