"""Image generation for task cards."""

import tempfile
import textwrap
from datetime import datetime

from .config import PIL_AVAILABLE, Image, ImageDraw, ImageFont


def create_task_image(task_data):
    """Create task card image with hand-drawn lightning bolts."""
    if not PIL_AVAILABLE:
        print("PIL not available - skipping image generation")
        return None

    try:
        # Image dimensions (optimized for thermal printer)
        width = 576  # 72mm thermal printer width
        
        # Load fonts first to calculate sizes
        # A common sans-serif font on Linux
        title_font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        date_font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

        try:
            title_font = ImageFont.truetype(title_font_path, 80)
            date_font = ImageFont.truetype(date_font_path, 32)
        except:
            print(f"Warning: Could not load {title_font_path} or {date_font_path}. Using default font.")
            title_font = ImageFont.load_default()
            date_font = ImageFont.load_default()

        # Calculate content height
        title_lines = textwrap.wrap(task_data["title"], width=15)
        title_height = len(title_lines) * 95 + 10
        emoji_height = 150
        date_height = 40
        total_padding = 30
        
        height = title_height + emoji_height + date_height + total_padding

        # Create image with white background
        img = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(img)

        # Draw title at the top
        title_y = 10
        
        for i, line in enumerate(title_lines):
            line_bbox = draw.textbbox((0, 0), line, font=title_font)
            line_width = line_bbox[2] - line_bbox[0]
            line_x = (width - line_width) // 2
            draw.text((line_x, title_y + i * 95), line, fill="black", font=title_font)

        # Draw lightning bolt emoji after title
        emoji_y = title_y + len(title_lines) * 95 + 20
        
        # Try to use a font that supports emojis
        emoji_font = None
        font_paths = [
            "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", # Noto Color Emoji (common on Linux)
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Fallback sans-serif with some emoji support
            "arial.ttf",  # Arial fallback (less likely on Linux, but kept for robustness)
        ]
        
        for font_path in font_paths:
            try:
                emoji_font = ImageFont.truetype(font_path, 150)
                break
            except:
                continue
        
        # If no font found, use default
        if emoji_font is None:
            print("Warning: Could not load a suitable emoji font. Using default font.")
            emoji_font = ImageFont.load_default()
        
        if task_data["priority"].upper() == "HIGH":
            # Three lightning bolt emojis
            emoji_text = "⚡ ⚡ ⚡"
        else:
            # Single lightning bolt emoji
            emoji_text = "⚡"
        
        # Calculate position to center the emoji
        emoji_bbox = draw.textbbox((0, 0), emoji_text, font=emoji_font)
        emoji_width = emoji_bbox[2] - emoji_bbox[0]
        emoji_x = (width - emoji_width) // 2
        draw.text((emoji_x, emoji_y), emoji_text, fill="black", font=emoji_font)

        # Draw due date below emoji
        date_y = emoji_y + 100
        due_date = datetime.now().strftime("%B %d")
        # Add ordinal suffix
        day = int(datetime.now().strftime("%d"))
        if 4 <= day <= 20 or 24 <= day <= 30:
            suffix = "th"
        else:
            suffix = ["st", "nd", "rd"][day % 10 - 1]
        
        due_date_text = f"{datetime.now().strftime('%B %d')}{suffix}"
        date_bbox = draw.textbbox((0, 0), due_date_text, font=date_font)
        date_width = date_bbox[2] - date_bbox[0]
        date_x = (width - date_width) // 2
        draw.text((date_x, date_y), due_date_text, fill="black", font=date_font)

        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        img.save(temp_file.name, "PNG")
        temp_file.close()

        print(f"Task card image created: {temp_file.name}")
        return temp_file.name

    except Exception as e:
        print(f"Error creating task card image: {str(e)}")
        return None
