import logging
from typing import Dict

try:
    import easyocr
except Exception:
    easyocr = None

from PIL import Image
from app.services import forgery

logger = logging.getLogger(__name__)


def extract_fields(image_path: str, doc_type: str) -> Dict[str, str]:
    """Run OCR on the provided document and return a best-effort dict of fields.

    This is a simplified extractor. For production, map OCR outputs to structured fields using templates per document.
    """
    text = ""
    if easyocr:
        try:
            reader = easyocr.Reader(['en'], gpu=False)
            results = reader.readtext(image_path, detail=0)
            text = "\n".join(results)
        except Exception as e:
            logger.warning("EasyOCR failed: %s", e)
    else:
        logger.warning("EasyOCR not installed, returning empty OCR result.")

    # very naive extraction
    fields = {
        "name": "",
        "dob": "",
        "document_number": "",
        "address": "",
        "raw_text": text,
        "microtext": None,
    }

    # naive heuristics: find lines with numbers for document_number
    for line in text.splitlines():
        l = line.strip()
        if not l:
            continue
        if any(ch.isdigit() for ch in l) and len(l) >= 6 and not fields['document_number']:
            fields['document_number'] = l
        if 'dob' in l.lower() or 'birth' in l.lower():
            fields['dob'] = l
        # name heuristics (placeholder)
        if l.isupper() and len(l.split()) <= 4 and not fields['name']:
            fields['name'] = l
    try:
        micro = forgery.detect_microtext(image_path)
        fields['microtext'] = micro
    except Exception:
        fields['microtext'] = {'method': 'error'}

    return fields
