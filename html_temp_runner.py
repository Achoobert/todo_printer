import os
import tempfile
from io import BytesIO
from weasyprint import HTML
import pymupdf as fitz # Import PyMuPDF as fitz
from PIL import Image

from escpos.printer import Usb 
# """ Seiko Epson Corp. Receipt Printer (EPSON TM-T88III) """
p = Usb(0x0416, 0x5011, out_ep=0x01, profile="TM-T88III")

def html_to_image_weasyprint_pymupdf(html_content, output_width=576):
    """Convert HTML to image using WeasyPrint and PyMuPDF."""
    temp_img_path = None
    try:
        # 1. Convert HTML to PDF in memory using WeasyPrint
        html = HTML(string=html_content)
        pdf_bytes = html.write_pdf()

        # 2. Open the in-memory PDF with PyMuPDF
        pdf_document = fitz.open("pdf", pdf_bytes)
        first_page = pdf_document[0] # Get the first page

        # 3. Render PDF page to a Pillow Image
        # Calculate the zoom factor to achieve the desired output_width
        # WeasyPrint's default DPI is 96.
        # PyMuPDF's get_pixmap renders at 72 DPI by default.
        # To get a specific width, we need to adjust the zoom.
        # Let's assume a standard A4 width for calculation if not specified in HTML/CSS
        # A common approach is to render at a high DPI and then resize if needed.
        # Or, calculate zoom based on desired output_width.
        
        # For a thermal printer, we want a fixed width.
        # Let's render at a high resolution and then resize to 576px.
        zoom_factor = 5 # Render at 2x resolution initially
        mat = fitz.Matrix(zoom_factor, zoom_factor)
        pix = first_page.get_pixmap(matrix=mat)

        # Convert to Pillow Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Resize to the desired output_width (576px) while maintaining aspect ratio
        if img.width != output_width:
            aspect_ratio = img.height / img.width
            new_height = int(output_width * aspect_ratio)
            img = img.resize((output_width, new_height), Image.LANCZOS)

        # Save to temporary file
        temp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        img.save(temp_img.name, "PNG")
        temp_img.close()
        temp_img_path = temp_img.name

        print(f"HTML converted to image with WeasyPrint and PyMuPDF: {temp_img_path}")
        return temp_img_path

    except Exception as e:
        print(f"Error converting HTML to image with WeasyPrint and PyMuPDF: {str(e)}")
        return None
    finally:
        if temp_img_path and not os.path.exists(temp_img_path):
            if os.path.exists(temp_img_path):
                os.remove(temp_img_path)


def create_task_html_image(html_content):
    """Create task card image from HTML using available method."""
    return html_to_image_weasyprint_pymupdf(html_content)

def print_html(html):
    """Converts HTML into an image and prints it to the receipt printer."""
    temp_image_path = None
    try:
        temp_image_path = create_task_html_image(html)

        if temp_image_path:
            # Open the image and convert to a format suitable for the printer
            img = Image.open(temp_image_path)
            # The printer expects a 1-bit (black and white) image.
            # Convert to '1' mode (1-bit pixels, black and white, stored with 0 as black and 1 as white).
            # Dithering helps to preserve details when converting to black and white.
            img = img.convert("1", dither=Image.FLOYDSTEINBERG)

            p.image(img)
            p.cut()
            print(f"Html-Image printed successfully.")
        else:
            print("Failed to generate image from HTML.")

    except Exception as e:
        print(f"Error processing or printing HTML image: {e}")
    finally:
        if temp_image_path and os.path.exists(temp_image_path):
            os.remove(temp_image_path) # Clean up the temporary image file


def main():
    with open("templates/lazy_gm.html", "r") as f:
    #with open("templates/playerlist.html", "r") as f:
        tiny = f.read()
    rpg_groups = ["Crusaders","Wildcards","Saga","Dealers",]
    for group_name in rpg_groups:
        todo_text = tiny.replace("TABLE_NAME", group_name)
        print_html(todo_text)

main()
