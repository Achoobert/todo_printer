import os
import tempfile
from io import BytesIO
from weasyprint import HTML
import pymupdf as fitz # Import PyMuPDF as fitz
from PIL import Image


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


def html_convert_to_image(html):
    """Converts HTML into an image and prints it to the receipt printer."""
    temp_image_path = None
    try:
        return html_to_image_weasyprint_pymupdf(html)

    except Exception as e:
        print(f"Error processing or printing HTML image: {e}")


def create_text_image(input_text):
   with open("text_template.html", "r") as f:
      tiny = f.read()
   todo_text = tiny.replace("TEXTINPUT", input_text)
   return html_convert_to_image(todo_text)