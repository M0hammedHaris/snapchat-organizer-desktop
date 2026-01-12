"""Help dialog with instructions for downloading Snapchat data.

This module provides a comprehensive help dialog that guides users through
the process of requesting and downloading their Snapchat data export.
"""

import logging
from typing import Optional

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QTextBrowser,
    QPushButton,
    QWidget,
)

logger = logging.getLogger(__name__)


class HelpDialog(QDialog):
    """Dialog showing help and instructions for Snapchat data download.
    
    Provides step-by-step instructions for:
    - Requesting Snapchat data export
    - Downloading the export file
    - Extracting and preparing data for the organizer
    """

    def __init__(self, parent: Optional[QWidget] = None, show_dont_show_again: bool = False):
        """Initialize the help dialog.
        
        Args:
            parent: Optional parent widget
            show_dont_show_again: Whether to show "Don't show again" checkbox
        """
        super().__init__(parent)
        self.setWindowTitle("How to Download Snapchat Data")
        self.setMinimumSize(700, 600)
        self._show_dont_show_again = show_dont_show_again
        self.dont_show_again = False
        self._setup_ui()
        logger.info("Help dialog initialized")

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create tab widget for different help sections
        tab_widget = QTabWidget()
        tab_widget.addTab(self._create_download_instructions(), "Download Data")
        tab_widget.addTab(self._create_prepare_instructions(), "Prepare Data")
        tab_widget.addTab(self._create_tips_widget(), "Tips & Tricks")

        layout.addWidget(tab_widget)

        # Don't show again checkbox (if enabled)
        if self._show_dont_show_again:
            from PySide6.QtWidgets import QCheckBox
            self.dont_show_checkbox = QCheckBox("Don't show this again on startup")
            self.dont_show_checkbox.stateChanged.connect(self._on_dont_show_changed)
            layout.addWidget(self.dont_show_checkbox)

        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setDefault(True)
        close_btn.clicked.connect(self.accept)
        close_btn.setMinimumWidth(100)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def _on_dont_show_changed(self, state):
        """Handle don't show again checkbox state change.
        
        Args:
            state: Checkbox state
        """
        from PySide6.QtCore import Qt
        self.dont_show_again = (state == Qt.CheckState.Checked)
        logger.info(f"Don't show again: {self.dont_show_again}")

    def _create_download_instructions(self) -> QWidget:
        """Create widget with Snapchat data download instructions.
        
        Returns:
            Widget containing download instructions
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)

        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(self._get_download_html())

        layout.addWidget(browser)
        return widget

    def _create_prepare_instructions(self) -> QWidget:
        """Create widget with data preparation instructions.
        
        Returns:
            Widget containing preparation instructions
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)

        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(self._get_prepare_html())

        layout.addWidget(browser)
        return widget

    def _create_tips_widget(self) -> QWidget:
        """Create widget with tips and troubleshooting.
        
        Returns:
            Widget containing tips
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)

        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(self._get_tips_html())

        layout.addWidget(browser)
        return widget

    def _get_download_html(self) -> str:
        """Get HTML content for download instructions.
        
        Returns:
            HTML formatted download instructions
        """
        return """
        <html>
        <head>
            <style>
                body { 
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif; 
                    padding: 20px;
                    background: #ffffff;
                    color: #2c3e50;
                }
                h1 { 
                    color: #2c3e50; 
                    font-size: 24px; 
                    margin-bottom: 10px;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                }
                h2 { 
                    color: #34495e; 
                    font-size: 18px; 
                    margin-top: 20px; 
                    margin-bottom: 10px; 
                }
                h3 { 
                    color: #7f8c8d; 
                    font-size: 16px; 
                    margin-top: 15px; 
                    margin-bottom: 8px; 
                }
                .step { 
                    background: #ecf0f1; 
                    padding: 15px; 
                    margin: 10px 0; 
                    border-radius: 8px; 
                    border-left: 4px solid #3498db;
                }
                .step-number { 
                    display: inline-block; 
                    background: #3498db; 
                    color: white; 
                    width: 30px; 
                    height: 30px; 
                    line-height: 30px; 
                    text-align: center; 
                    border-radius: 50%; 
                    font-weight: bold; 
                    margin-right: 10px;
                }
                .important { 
                    background: #fff9e6; 
                    padding: 10px; 
                    border-left: 4px solid #f39c12; 
                    margin: 10px 0;
                    border-radius: 4px;
                }
                a { 
                    color: #3498db; 
                    text-decoration: none; 
                    font-weight: 500;
                }
                a:hover { 
                    text-decoration: underline;
                    color: #2980b9;
                }
                code { 
                    background: #e8eaf6; 
                    padding: 2px 6px; 
                    border-radius: 3px; 
                    font-family: 'Courier New', monospace;
                    color: #5e35b1;
                }
                ul { line-height: 1.8; }
                li { margin: 8px 0; }
                strong { color: #2c3e50; }
            </style>
        </head>
        <body>
            <h1>📥 How to Download Your Snapchat Data</h1>
            
            <div class="important">
                <strong>⏱️ Important:</strong> Snapchat typically takes <strong>24-72 hours</strong> to prepare your data export. 
                Plan accordingly and request your data in advance.
            </div>

            <h2>Step-by-Step Instructions</h2>

            <div class="step">
                <span class="step-number">1</span>
                <strong>Log in to Snapchat Accounts Portal</strong><br>
                Visit <a href="https://accounts.snapchat.com/" target="_blank">accounts.snapchat.com</a> and log in with your Snapchat credentials.
            </div>

            <div class="step">
                <span class="step-number">2</span>
                <strong>Navigate to My Data</strong><br>
                Click on <strong>"My Data"</strong> in the left sidebar or go directly to 
                <a href="https://accounts.snapchat.com/accounts/downloadmydata" target="_blank">Download My Data</a>.
            </div>

            <div class="step">
                <span class="step-number">3</span>
                <strong>Select Data to Download</strong><br>
                <ul>
                    <li>Choose <strong>"Select All"</strong> to download everything, or</li>
                    <li>Customize your export by selecting specific data types:
                        <ul>
                            <li>✅ <strong>Chat History</strong> (required for organizing chat media)</li>
                            <li>✅ <strong>Memories</strong> (photos and videos)</li>
                            <li>✅ <strong>Snap History</strong> (metadata about your snaps)</li>
                            <li>Optional: Stories, Friends, Location History, etc.</li>
                        </ul>
                    </li>
                </ul>
            </div>

            <div class="step">
                <span class="step-number">4</span>
                <strong>Choose File Format</strong><br>
                Select <strong>HTML</strong> format (recommended) or JSON format. This app supports both formats.
            </div>

            <div class="step">
                <span class="step-number">5</span>
                <strong>Submit Request</strong><br>
                Click <strong>"Submit Request"</strong> button at the bottom of the page.
            </div>

            <div class="step">
                <span class="step-number">6</span>
                <strong>Wait for Email Notification</strong><br>
                Snapchat will send you an email to your registered email address when your data is ready. 
                This usually takes <strong>24-72 hours</strong>, but can sometimes take up to a week for large accounts.
            </div>

            <div class="step">
                <span class="step-number">7</span>
                <strong>Download the ZIP File</strong><br>
                <ul>
                    <li>Click the link in the email from Snapchat</li>
                    <li>You'll be redirected to the download page</li>
                    <li>Click <strong>"Download My Data"</strong></li>
                    <li>Save the ZIP file to a location you'll remember (e.g., Downloads folder)</li>
                </ul>
            </div>

            <div class="step">
                <span class="step-number">8</span>
                <strong>Extract the ZIP File</strong><br>
                <ul>
                    <li><strong>macOS:</strong> Double-click the ZIP file</li>
                    <li><strong>Windows:</strong> Right-click → Extract All</li>
                    <li><strong>Linux:</strong> Use file manager or <code>unzip filename.zip</code></li>
                </ul>
                This will create a folder named <code>mydata~YYYY-MM-DD</code>.
            </div>

            <div class="important">
                <strong>✅ You're Ready!</strong> Once extracted, use this folder with the Snapchat Organizer Desktop app:
                <ul>
                    <li><strong>Download Tab:</strong> Select the <code>memories_history.html</code> file</li>
                    <li><strong>Organize Tab:</strong> Select the extracted folder containing <code>chat_history.json</code></li>
                </ul>
            </div>

            <h2>📂 What's Inside the Export?</h2>
            
            <p>Your Snapchat data export contains:</p>
            <ul>
                <li><code>index.html</code> - Overview of your data</li>
                <li><code>memories_history.html</code> - List of all your saved memories with download links</li>
                <li><code>chat_history.json</code> - All your chat conversations and metadata</li>
                <li><code>snap_history.json</code> - Information about snaps you've sent/received</li>
                <li><code>friends.json</code> - Your friends list</li>
                <li>Other JSON files with various account data</li>
            </ul>
        </body>
        </html>
        """

    def _get_prepare_html(self) -> str:
        """Get HTML content for data preparation instructions.
        
        Returns:
            HTML formatted preparation instructions
        """
        return """
        <html>
        <head>
            <style>
                body { 
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif; 
                    padding: 20px;
                    background: #ffffff;
                    color: #2c3e50;
                }
                h1 { 
                    color: #2c3e50; 
                    font-size: 24px; 
                    margin-bottom: 10px;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                }
                h2 { 
                    color: #34495e; 
                    font-size: 18px; 
                    margin-top: 20px; 
                    margin-bottom: 10px; 
                }
                .feature-box { 
                    background: #ecf0f1; 
                    padding: 15px; 
                    margin: 10px 0; 
                    border-radius: 8px;
                    border-left: 4px solid #27ae60;
                }
                .feature-title { 
                    font-weight: bold; 
                    color: #2c3e50; 
                    margin-bottom: 8px;
                    font-size: 16px;
                }
                .important { 
                    background: #e8f5e9; 
                    padding: 10px; 
                    border-left: 4px solid #27ae60; 
                    margin: 10px 0;
                    border-radius: 4px;
                }
                ul { line-height: 1.8; }
                li { margin: 8px 0; }
                code { 
                    background: #e8eaf6; 
                    padding: 2px 6px; 
                    border-radius: 3px; 
                    font-family: 'Courier New', monospace;
                    color: #5e35b1;
                }
                strong { color: #2c3e50; }
            </style>
        </head>
        <body>
            <h1>🔧 Preparing Your Data for Organization</h1>
            
            <h2>Using the Download Tab</h2>
            <div class="feature-box">
                <div class="feature-title">📥 Download Memories</div>
                <ol>
                    <li>Select the <code>memories_history.html</code> file from your extracted Snapchat data</li>
                    <li>Choose an output directory where memories will be downloaded</li>
                    <li>Configure options:
                        <ul>
                            <li><strong>Download Delay:</strong> Time between requests (2-5 seconds recommended)</li>
                            <li><strong>Apply GPS:</strong> Embed location metadata if available</li>
                            <li><strong>Apply Overlays:</strong> Composite Snapchat overlays on photos</li>
                            <li><strong>Convert Timezone:</strong> Convert GPS to local timezone</li>
                        </ul>
                    </li>
                    <li>Click <strong>"Start Download"</strong></li>
                </ol>
            </div>

            <h2>Using the Organize Tab</h2>
            <div class="feature-box">
                <div class="feature-title">📂 Organize Chat Media</div>
                <ol>
                    <li>Select your Snapchat export folder (the one with <code>chat_history.json</code>)</li>
                    <li>Choose an output directory for organized files</li>
                    <li>Configure matching settings:
                        <ul>
                            <li><strong>3-Tier Matching:</strong> Media ID → Contact → Timestamp proximity</li>
                            <li><strong>Time Window:</strong> How close timestamps need to be (default: 2 hours)</li>
                            <li><strong>Minimum Score:</strong> Confidence threshold for matches (default: 45%)</li>
                        </ul>
                    </li>
                    <li>Click <strong>"Start Organization"</strong></li>
                </ol>
            </div>

            <h2>Using the Tools Tab</h2>
            <div class="feature-box">
                <div class="feature-title">🛠️ Utility Tools</div>
                <p>After downloading and organizing, use these tools to maintain your media library:</p>
                <ul>
                    <li><strong>Verify Files:</strong> Check for corrupted images/videos</li>
                    <li><strong>Remove Duplicates:</strong> Find and remove duplicate media using SHA256 hashing</li>
                    <li><strong>Organize by Year:</strong> Sort media into year folders based on EXIF dates</li>
                    <li><strong>Fix Timestamps:</strong> Sync EXIF dates to file modification times</li>
                </ul>
            </div>

            <div class="important">
                <strong>💡 Tip:</strong> The app processes everything <strong>locally on your computer</strong>. 
                No data is ever uploaded to the internet. Your privacy is 100% protected.
            </div>

            <h2>📊 Expected Results</h2>
            <p>After organization, your media will be structured like:</p>
            <pre style="background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto;">
output_folder/
├── Contact Name 1/
│   ├── 2023-01-15_photo.jpg
│   ├── 2023-02-20_video.mp4
│   └── ...
├── Contact Name 2/
│   ├── 2023-03-10_photo.jpg
│   └── ...
└── Unmatched/
    └── (media that couldn't be matched to contacts)
            </pre>
        </body>
        </html>
        """

    def _get_tips_html(self) -> str:
        """Get HTML content for tips and troubleshooting.
        
        Returns:
            HTML formatted tips
        """
        return """
        <html>
        <head>
            <style>
                body { 
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif; 
                    padding: 20px;
                    background: #ffffff;
                    color: #2c3e50;
                }
                h1 { 
                    color: #2c3e50; 
                    font-size: 24px; 
                    margin-bottom: 10px;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                }
                h2 { 
                    color: #34495e; 
                    font-size: 18px; 
                    margin-top: 20px; 
                    margin-bottom: 10px; 
                }
                .tip { 
                    background: #e8f5e9; 
                    padding: 12px; 
                    margin: 10px 0; 
                    border-radius: 8px; 
                    border-left: 4px solid #27ae60;
                }
                .warning { 
                    background: #fff9e6; 
                    padding: 12px; 
                    margin: 10px 0; 
                    border-radius: 8px; 
                    border-left: 4px solid #f39c12;
                }
                .error { 
                    background: #ffebee; 
                    padding: 12px; 
                    margin: 10px 0; 
                    border-radius: 8px; 
                    border-left: 4px solid #e74c3c;
                }
                ul { line-height: 1.8; }
                li { margin: 8px 0; }
                code { 
                    background: #e8eaf6; 
                    padding: 2px 6px; 
                    border-radius: 3px; 
                    font-family: 'Courier New', monospace;
                    color: #5e35b1;
                }
                strong { color: #2c3e50; }
            </style>
        </head>
        <body>
            <h1>💡 Tips & Troubleshooting</h1>
            
            <h2>Best Practices</h2>
            
            <div class="tip">
                <strong>✅ Use a Wired Connection</strong><br>
                When downloading memories, use a wired internet connection if possible. Large downloads can be interrupted on Wi-Fi.
            </div>

            <div class="tip">
                <strong>✅ Download During Off-Peak Hours</strong><br>
                Snapchat's servers may be slower during peak hours. Try downloading late at night or early morning.
            </div>

            <div class="tip">
                <strong>✅ Keep Your Computer Awake</strong><br>
                Prevent your computer from sleeping during downloads. On macOS, you can use <code>caffeinate</code> command.
            </div>

            <div class="tip">
                <strong>✅ Start with a Test Run</strong><br>
                Test the organize function on a small subset of files first to verify settings before processing your entire library.
            </div>

            <h2>Common Issues</h2>

            <div class="warning">
                <strong>⚠️ "Download request failed" errors</strong><br>
                <strong>Solution:</strong> Increase the download delay to 3-5 seconds. Snapchat may rate-limit rapid requests.
            </div>

            <div class="warning">
                <strong>⚠️ Some files couldn't be matched to contacts</strong><br>
                <strong>Solution:</strong> This is normal. Media sent in group chats or without metadata will be placed in the "Unmatched" folder.
                You can adjust the matching threshold and time window in settings.
            </div>

            <div class="warning">
                <strong>⚠️ "Permission denied" errors</strong><br>
                <strong>Solution:</strong> Make sure you have write permissions for the output directory. 
                Try selecting a different folder or running the app with appropriate permissions.
            </div>

            <div class="error">
                <strong>🚫 "Invalid Snapchat export" error</strong><br>
                <strong>Solution:</strong> Make sure you've extracted the ZIP file and selected the correct folder/file:
                <ul>
                    <li>Download tab: Select <code>memories_history.html</code> file</li>
                    <li>Organize tab: Select folder containing <code>chat_history.json</code></li>
                </ul>
            </div>

            <h2>Performance Tips</h2>

            <div class="tip">
                <strong>⚡ Free Up Disk Space</strong><br>
                Ensure you have at least 2x the size of your Snapchat data export available as free disk space.
            </div>

            <div class="tip">
                <strong>⚡ Close Other Applications</strong><br>
                For best performance during processing, close memory-intensive applications like web browsers with many tabs.
            </div>

            <div class="tip">
                <strong>⚡ Use SSD Storage</strong><br>
                If possible, save your output to an SSD (solid-state drive) rather than a traditional hard drive for faster processing.
            </div>

            <h2>Privacy & Security</h2>

            <div class="tip">
                <strong>🔒 100% Local Processing</strong><br>
                All data processing happens entirely on your computer. Nothing is uploaded to the internet or any server.
            </div>

            <div class="tip">
                <strong>🔒 Delete Export After Processing</strong><br>
                Once you've organized your media, you can safely delete the original Snapchat ZIP export and extracted folder 
                to save disk space and protect your privacy.
            </div>

            <div class="warning">
                <strong>⚠️ Keep Backups</strong><br>
                Always keep a backup of your organized media. Consider using Time Machine (macOS), File History (Windows), 
                or cloud storage services.
            </div>

            <h2>Need More Help?</h2>
            <p>
                If you encounter issues not covered here, check the application logs at:<br>
                <code>~/.snapchat-organizer/logs/app.log</code>
            </p>
        </body>
        </html>
        """
