#!/usr/bin/env python3
"""
Generate app icon for Snapchat Organizer Desktop.

Creates a simple but recognizable icon with the Snapchat ghost
and organization elements (folders, arrows).
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    """Create application icon in multiple sizes."""
    
    # Sizes for macOS .icns file
    sizes = [16, 32, 64, 128, 256, 512, 1024]
    
    # Create resources/icons directory if it doesn't exist
    icon_dir = os.path.join(os.path.dirname(__file__), "..", "resources", "icons")
    os.makedirs(icon_dir, exist_ok=True)
    
    # Create the base icon at largest size
    size = 1024
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Snapchat yellow background (rounded square)
    margin = size // 8
    draw.rounded_rectangle(
        [(margin, margin), (size - margin, size - margin)],
        radius=size // 6,
        fill='#FFFC00'  # Snapchat yellow
    )
    
    # Draw a simplified ghost shape in white
    ghost_width = size // 2
    ghost_height = int(ghost_width * 1.3)
    ghost_x = (size - ghost_width) // 2
    ghost_y = (size - ghost_height) // 2 - size // 12
    
    # Ghost body (rounded rectangle)
    draw.rounded_rectangle(
        [(ghost_x, ghost_y), (ghost_x + ghost_width, ghost_y + ghost_height)],
        radius=ghost_width // 3,
        fill='white'
    )
    
    # Ghost arms (circles on sides)
    arm_radius = ghost_width // 8
    # Left arm
    draw.ellipse(
        [(ghost_x - arm_radius, ghost_y + ghost_height // 3),
         (ghost_x + arm_radius, ghost_y + ghost_height // 3 + arm_radius * 2)],
        fill='white'
    )
    # Right arm
    draw.ellipse(
        [(ghost_x + ghost_width - arm_radius, ghost_y + ghost_height // 3),
         (ghost_x + ghost_width + arm_radius, ghost_y + ghost_height // 3 + arm_radius * 2)],
        fill='white'
    )
    
    # Ghost eyes (black circles)
    eye_radius = ghost_width // 12
    eye_y = ghost_y + ghost_height // 4
    # Left eye
    draw.ellipse(
        [(ghost_x + ghost_width // 3 - eye_radius, eye_y),
         (ghost_x + ghost_width // 3 + eye_radius, eye_y + eye_radius * 2)],
        fill='black'
    )
    # Right eye
    draw.ellipse(
        [(ghost_x + 2 * ghost_width // 3 - eye_radius, eye_y),
         (ghost_x + 2 * ghost_width // 3 + eye_radius, eye_y + eye_radius * 2)],
        fill='black'
    )
    
    # Add folder icon overlay at bottom right to indicate "organizer"
    folder_size = size // 4
    folder_x = size - margin - folder_size - size // 20
    folder_y = size - margin - folder_size - size // 20
    
    # Folder tab
    draw.rectangle(
        [(folder_x, folder_y),
         (folder_x + folder_size // 2, folder_y + folder_size // 6)],
        fill='#0066FF',  # Blue folder
        outline='#0052CC',
        width=3
    )
    
    # Folder body
    draw.rounded_rectangle(
        [(folder_x, folder_y + folder_size // 6),
         (folder_x + folder_size, folder_y + folder_size)],
        radius=folder_size // 12,
        fill='#0066FF',
        outline='#0052CC',
        width=3
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
    
    # On macOS, we'll need to convert to .icns using iconutil
    print("\n🍎 For macOS .icns file, run:")
    print(f"   iconutil -c icns {icon_dir}")

if __name__ == "__main__":
    create_icon()
