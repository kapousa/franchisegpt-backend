import io
import random
import string

from fastapi import UploadFile, HTTPException
from pdfminer.high_level import extract_text

class FileHelper:
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        return extract_text(file_path)

    @staticmethod
    def extract_text_from_txt(file_path: str) -> str:
        with open(file_path, "r") as f:
            return f.read()


def extract_text_from_uploaded_report(pdf_file: UploadFile):
    """Extracts text from a PDF file."""
    try:
        pdf_content = pdf_file.file.read()
        text_io = io.BytesIO(pdf_content)
        text = extract_text(text_io)  # Corrected Line
        return text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting text from PDF: {e}")


def generate_id(length=14) -> str:
    """
    Generates a random string of specified length containing a mix of numbers and characters.

    Args:
        length: The length of the ID to generate (default: 14).

    Returns:
        A string of the specified length containing a mix of numbers and characters.
    """
    characters = string.ascii_letters + string.digits  # Combine letters (both cases) and digits
    random_id = ''.join(random.choice(characters) for _ in range(length))

    return random_id
