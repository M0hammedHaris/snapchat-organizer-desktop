"""Onboarding dialog - Welcome carousel shown on first launch.

Shows a series of slides with app screenshots and descriptions to help
new users understand the application's features and workflow.
"""

import logging
from pathlib import Path
from typing import List, Tuple

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont

from ..utils.config import APP_NAME

logger = logging.getLogger(__name__)

# Path to app screenshots
SCREENSHOTS_DIR = Path(__file__).parent.parent.parent / "app-screenshots"


def _get_slides() -> List[Tuple[str, str, str]]:
    """Return list of (title, description, image_filename) for each slide."""
    return [
        (
            "Welcome to Snapchat Organizer",
            "Your all-in-one desktop tool for downloading, organizing,\n"
            "and managing your Snapchat memories — 100% private and local.",
            None,  # No image for welcome slide
        ),
        (
            "Download Memories",
            "Import your Snapchat data export and download all your\n"
            "memories with a single click. Supports images and videos.",
            "light-mode-download-memories.png",
        ),
        (
            "Organize Chat Media",
            "Automatically sort your chat media by contact.\n"
            "Each person's photos and videos in their own folder.",
            "light-mode-organize-chat-media-1.png",
        ),
        (
            "Powerful Tools",
            "Organize files by year, fix timestamps, remove duplicates,\n"
            "apply overlays, and more — all from the Tools tab.",
            "light-mode-tools.png",
        ),
        (
            "You're All Set!",
            "Sign in or create an account to get started.\n"
            "Free tier includes 100 downloads per month.",
            None,  # No image for final slide
        ),
    ]


class OnboardingDialog(QDialog):
    """Welcome carousel dialog shown on first app launch."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Welcome to {APP_NAME}")
        self.setMinimumSize(680, 520)
        self.setMaximumSize(800, 620)
        self.setModal(True)

        self._slides = _get_slides()
        self._current_index = 0

        self._setup_ui()
        self._show_slide(0)

    def _setup_ui(self):
        """Build the dialog layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 24, 30, 20)
        layout.setSpacing(12)

        # ── Slide content area ──
        self._title_label = QLabel()
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        self._title_label.setFont(title_font)
        self._title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._title_label)

        self._desc_label = QLabel()
        desc_font = QFont()
        desc_font.setPointSize(13)
        self._desc_label.setFont(desc_font)
        self._desc_label.setAlignment(Qt.AlignCenter)
        self._desc_label.setWordWrap(True)
        self._desc_label.setStyleSheet("color: gray; margin-bottom: 8px;")
        layout.addWidget(self._desc_label)

        # Screenshot image
        self._image_label = QLabel()
        self._image_label.setAlignment(Qt.AlignCenter)
        self._image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._image_label.setMinimumHeight(280)
        layout.addWidget(self._image_label, stretch=1)

        # ── Dot indicators ──
        self._dots_layout = QHBoxLayout()
        self._dots_layout.setAlignment(Qt.AlignCenter)
        self._dots_layout.setSpacing(8)
        self._dot_labels: List[QLabel] = []
        for i in range(len(self._slides)):
            dot = QLabel()
            dot.setFixedSize(10, 10)
            dot.setStyleSheet(self._dot_style(active=False))
            self._dots_layout.addWidget(dot)
            self._dot_labels.append(dot)
        layout.addLayout(self._dots_layout)

        # ── Navigation buttons ──
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(12)

        self._skip_btn = QPushButton("Skip")
        self._skip_btn.setFlat(True)
        self._skip_btn.setStyleSheet("color: gray;")
        self._skip_btn.clicked.connect(self.accept)
        nav_layout.addWidget(self._skip_btn)

        nav_layout.addStretch()

        self._back_btn = QPushButton("Back")
        self._back_btn.setMinimumWidth(80)
        self._back_btn.clicked.connect(self._go_back)
        nav_layout.addWidget(self._back_btn)

        self._next_btn = QPushButton("Next")
        self._next_btn.setMinimumWidth(80)
        self._next_btn.setMinimumHeight(34)
        self._next_btn.setDefault(True)
        self._next_btn.clicked.connect(self._go_next)
        nav_layout.addWidget(self._next_btn)

        layout.addLayout(nav_layout)

    def _show_slide(self, index: int):
        """Display a specific slide."""
        self._current_index = index
        title, desc, image_file = self._slides[index]

        self._title_label.setText(title)
        self._desc_label.setText(desc)

        # Load image
        if image_file:
            image_path = SCREENSHOTS_DIR / image_file
            if image_path.exists():
                pixmap = QPixmap(str(image_path))
                scaled = pixmap.scaled(
                    600, 340,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
                self._image_label.setPixmap(scaled)
            else:
                self._image_label.setText("(Screenshot not found)")
                self._image_label.setStyleSheet("color: gray;")
        else:
            self._image_label.clear()
            # Show a welcome/final icon placeholder
            if index == 0:
                self._image_label.setText("")
            else:
                self._image_label.setText("")

        # Update dots
        for i, dot in enumerate(self._dot_labels):
            dot.setStyleSheet(self._dot_style(active=(i == index)))

        # Update button states
        self._back_btn.setVisible(index > 0)
        is_last = index == len(self._slides) - 1
        self._next_btn.setText("Get Started" if is_last else "Next")
        self._skip_btn.setVisible(not is_last)

    def _go_next(self):
        """Advance to the next slide or close."""
        if self._current_index < len(self._slides) - 1:
            self._show_slide(self._current_index + 1)
        else:
            self.accept()

    def _go_back(self):
        """Go back to the previous slide."""
        if self._current_index > 0:
            self._show_slide(self._current_index - 1)

    @staticmethod
    def _dot_style(active: bool) -> str:
        """Return stylesheet for a dot indicator."""
        color = "#2196F3" if active else "#CCCCCC"
        return (
            f"background-color: {color}; "
            f"border-radius: 5px; "
            f"min-width: 10px; max-width: 10px; "
            f"min-height: 10px; max-height: 10px;"
        )
