import os

from escpos.printer import Usb 
# """ Seiko Epson Corp. Receipt Printer (EPSON TM-T88III) """
p = Usb(0x0416, 0x5011, out_ep=0x01, profile="TM-T88III")

def print_image_to_printer(image_obj):
    if image_obj:
        # The escpos library's image method can accept a PIL Image object directly
        p.image(image_obj)
        p.cut()
    return

def print_text(text):
   p.text(text)
   p.cut()
