def extract_image_text(path):
    try:
        from PIL import Image
        import pytesseract

        with Image.open(path) as image:
            return pytesseract.image_to_string(image).strip()
    except pytesseract.TesseractNotFoundError as exc:
        raise ValueError(
            "Tesseract OCR is not installed or not in PATH. Install Tesseract to parse image resumes."
        ) from exc
    except Exception as exc:
        raise ValueError(f"Could not parse image resume: {exc}") from exc

