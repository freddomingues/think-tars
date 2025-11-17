import io
from pypdf import PdfReader

def extract_text_from_pdf_bytes(file_bytes: bytes) -> str:
    """Extrai texto de bytes de um arquivo PDF."""
    reader = PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        content = page.extract_text()
        if content:
            text += content + "\n"
    return text
