#!/usr/bin/env python3
"""
Generate app icon for Snapchat Organizer Desktop.

Creates a modern, professional icon with the Snapchat ghost
and folder organization badge.
"""

from PIL import Image, ImageDraw
import os

def create_icon():
    """Create application icon in multiple sizes with improved design."""
    
    # Sizes for macOS .icns file
    sizes = [16, 32, 64, 128, 256, 512, 1024]
    
    # Create resources/icons directory if it doesn't exist
    icon_dir = os.path.join(os.path.dirname(__file__), "..", "resources", "icons")
    os.makedirs(icon_dir, exist_ok=True)
    
    # Create the base icon at largest size
    size = 1024
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Modern gradient background (Snapchat yellow with rounded corners)
    margin = size // 8
    # Add subtle shadow/depth effect
    shadow_offset = size // 40
    draw.rounded_rectangle(
        [(margin + shadow_offset, margin + shadow_offset), 
         (size - margin + shadow_offset, size - margin + shadow_offset)],
        radius=size // 5,
        fill='#00000020'  # Semi-transparent black shadow
    )
    
    # Main background on top of shadow
    draw.rounded_rectangle(
        [(margin, margin), (size - margin, size - margin)],
        radius=size // 5,
        fill='#FFFC00'  # Snapchat yellow
    )
    
    # Draw a modern, simplified ghost shape
    ghost_width = int(size * 0.5)
    ghost_height = int(ghost_width * 1.2)
    ghost_x = (size - ghost_width) // 2
    ghost_y = int((size - ghost_height) // 2 - size * 0.05)
    
    # Ghost head and body (large circle/ellipse)
    head_radius = ghost_width // 2
    
    # Main body ellipse
    draw.ellipse(
        [(ghost_x, ghost_y),
         (ghost_x + ghost_width, ghost_y + int(ghost_width * 1.4))],
        fill='white'
    )
    
    # Wavy bottom (3 bumps for classic ghost look)
    wave_y = ghost_y + ghost_height
    wave_width = ghost_width // 3
    for i in range(3):
        wave_x = ghost_x + i * wave_width
        draw.ellipse(
            [(wave_x, wave_y - wave_width // 3),
             (wave_x + wave_width, wave_y + wave_width // 3)],
            fill='white'
        )
    
    # Cover the straight bottom with yellow to create wavy edge
    draw.rectangle(
        [(ghost_x, wave_y + wave_width // 4),
         (ghost_x + ghost_width, wave_y + wave_width)],
        fill='#FFFC00'
    )
    
    # Draw cute eyes (black ovals)
    eye_width = ghost_width // 8
    eye_height = ghost_width // 6
    eye_y = ghost_y + ghost_height // 3
    
    # Left eye
    draw.ellipse(
        [(ghost_x + ghost_width // 3 - eye_width, eye_y),
         (ghost_x + ghost_width // 3 + eye_width, eye_y + eye_height)],
        fill='black'
    )
    # Right eye
    draw.ellipse(
        [(ghost_x + 2 * ghost_width // 3 - eye_width, eye_y),
         (ghost_x + 2 * ghost_width // 3 + eye_width, eye_y + eye_height)],
        fill='black'
    )
    
    # Add a modern folder badge in bottom-right corner
    badge_size = int(size * 0.28)
    badge_x = size - margin - badge_size - int(size * 0.03)
    badge_y = size - margin - badge_size - int(size * 0.03)
    
    # White circle background for badge (with shadow)
    draw.ellipse(
        [(badge_x - 4, badge_y - 4),
         (badge_x + badge_size + 4, badge_y + badge_size + 4)],
        fill='#00000030'  # Shadow
    )
    
    draw.ellipse(
        [(badge_x, badge_y),
         (badge_x + badge_size, badge_y + badge_size)],
        fill='white'
    )
    
    # Folder icon inside the badge
    folder_margin = badge_size // 4
    folder_x = badge_x + folder_margin
    folder_y = badge_y + folder_margin + badge_size // 12
    folder_width = badge_size - 2 * folder_margin
    folder_height = int(folder_width * 0.7)
    
    # Folder tab (modern style)
    tab_width = folder_width // 2
    tab_height = folder_height // 5
    draw.rounded_rectangle(
        [(folder_x, folder_y - tab_height // 2),
         (folder_x + tab_width, folder_y + tab_height)],
        radius=tab_height // 2,
        fill='#0066FF'
    )
    
    # Folder body (modern rounded style)
    draw.rounded_rectangle(
        [(folder_x, folder_y),
         (folder_x + folder_width, folder_y + folder_height)],
        radius=folder_height // 6,
        fill='#0066FF'
    )
    
    # Add a subtle highlight on folder for depth
    highlight_y = folder_y + folder_height // 6
    draw.rounded_rectangle(
        [(folder_x + folder_width // 8, highlight_y),
         (folder_x + folder_width - folder_width // 8, highlight_y + 2)],
        radius=1,
        fill='#3388FF'
    )
    
    # Save PNG versions
    for icon_size in sizes:
        resized = img.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
        resized.save(os.path.join(icon_dir, f"icon_{icon_size}x{icon_size}.png"))
    
    # Save main icon.png (512x512 for general use)
    img_512 = img.resize((512, 512), Image.Resampling.LANCZOS)
    img_512.save(os.path.join(icon_dir, "icon.png"))
    
    # Save ICO for Windows (contains multiple sizes)
    ico_path = os.path.join(icon_dir, "icon.ico")
    img.save(
        ico_path,
        format='ICO',
        sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    )
    
    print("✅ Icons created successfully!")
    print(f"📂 Location: {icon_dir}")
    print(f"📦 Created: {len(sizes)} PNG files + icon.png + icon.ico")
    print(f"🎨 Design: Snapchat ghost + folder organizer badge")
    print(f"🎨 Style: Modern, clean, professional")
    print("\n🍎 Note: macOS .icns will be created separately")

if __name__ == "__main__":
    create_icon()
