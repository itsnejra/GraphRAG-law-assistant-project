import fitz  # PyMuPDF

def process_pdf(pdf_path):
    """
    Ekstrahuje tekst iz PDF fajla koristeći PyMuPDF (fitz).
    """
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text
