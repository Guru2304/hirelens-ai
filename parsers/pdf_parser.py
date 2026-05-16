def extract_pdf_text(path):
    try:
        import fitz

        text_parts = []
        with fitz.open(path) as document:
            for page in document:
                text_parts.append(page.get_text("text"))
        return "\n".join(text_parts).strip()
    except Exception as exc:
        raise ValueError(f"Could not parse PDF file: {exc}") from exc

