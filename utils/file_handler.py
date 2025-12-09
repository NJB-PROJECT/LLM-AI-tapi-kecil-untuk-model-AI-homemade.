import os
import io
from pypdf import PdfReader
from docx import Document
from PIL import Image
import base64

def extract_text_from_pdf(file_bytes):
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def extract_text_from_docx(file_bytes):
    try:
        doc = Document(io.BytesIO(file_bytes))
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        return f"Error reading DOCX: {str(e)}"

def extract_text_from_txt(file_bytes):
    try:
        return file_bytes.decode("utf-8")
    except Exception as e:
        return f"Error reading TXT: {str(e)}"

def encode_image_to_base64(image_file):
    """
    Converts a PIL Image or file-like object to base64 string.
    """
    try:
        if isinstance(image_file, bytes):
             image = Image.open(io.BytesIO(image_file))
        else:
             image = Image.open(image_file)

        buffered = io.BytesIO()
        image.save(buffered, format="PNG") # Default to PNG
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return img_str
    except Exception as e:
        print(f"Error encoding image: {e}")
        return None
