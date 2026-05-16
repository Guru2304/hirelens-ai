from pathlib import Path

from werkzeug.utils import secure_filename

from config.constants import ALLOWED_EXTENSIONS
from parsers.docx_parser import extract_docx_text
from parsers.image_parser import extract_image_text
from parsers.pdf_parser import extract_pdf_text


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def safe_filename(filename):
    return secure_filename(filename or "resume")


def extract_text_by_type(path):
    suffix = Path(path).suffix.lower().lstrip(".")
    if suffix == "pdf":
        return extract_pdf_text(path)
    if suffix == "docx":
        return extract_docx_text(path)
    if suffix in {"png", "jpg", "jpeg"}:
        return extract_image_text(path)
    raise ValueError("Unsupported file type.")


def delete_file(path):
    try:
        Path(path).unlink(missing_ok=True)
    except Exception:
        pass

