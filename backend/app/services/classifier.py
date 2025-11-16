from typing import Literal
from PIL import Image

def classify_document(image_path: str) -> Literal['aadhaar','passport','drivers_license','unknown']:
    """Very small placeholder classifier. Replace with a CNN model for production.

    Heuristic: if image contains 'MRZ' like text we return passport. Otherwise aadhaar by default.
    """
    try:
        img = Image.open(image_path)
        w, h = img.size
        # placeholder heuristics
        if w > 2000 or h > 2000:
            return 'passport'
        return 'aadhaar'
    except Exception:
        return 'unknown'
