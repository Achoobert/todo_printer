from escpos.printer import Usb 
from src.image_generator import create_task_image
import os

# """ Seiko Epson Corp. Receipt Printer (EPSON TM-T88III) """
p = Usb(0x0416, 0x5011, out_ep=0x01, profile="TM-T88III")

def print_task(title, priority):
    task_data = {
        "title": title,
        "priority": priority
    }

    # Create the task image
    image_path = create_task_image(task_data)

    if image_path:
        p.image(image_path)
        p.cut()
        os.remove(image_path) # Clean up the temporary image file
    else:
        p.text(f"[ ] {title} ({priority})\n")