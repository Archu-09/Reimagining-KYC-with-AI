import re
from typing import Dict, Any

_MRZ_AVAILABLE = False
try:
    from mrz.checker import passport as mrz_passport_check
    from mrz.mrz import MRZ
    _MRZ_AVAILABLE = True
except Exception:
    _MRZ_AVAILABLE = False


def mrz_validate(text: str) -> bool:
    # Use python-mrz if available, otherwise fallback to simple check
    if _MRZ_AVAILABLE:
        try:
            # try to parse MRZ block
            mrz_obj = MRZ(text)
            return mrz_obj.valid
        except Exception:
            return False
    return "<" in text and len(text) > 20


def _verhoeff_compute_checksum(num_str: str) -> int:
    # Implementation of Verhoeff algorithm for checksum digit
    # Tables from Verhoeff algorithm
    d = [
        [0,1,2,3,4,5,6,7,8,9],
        [1,2,3,4,0,6,7,8,9,5],
        [2,3,4,0,1,7,8,9,5,6],
        [3,4,0,1,2,8,9,5,6,7],
        [4,0,1,2,3,9,5,6,7,8],
        [5,9,8,7,6,0,4,3,2,1],
        [6,5,9,8,7,1,0,4,3,2],
        [7,6,5,9,8,2,1,0,4,3],
        [8,7,6,5,9,3,2,1,0,4],
        [9,8,7,6,5,4,3,2,1,0]
    ]
    p = [
        [0,1,2,3,4,5,6,7,8,9],
        [1,5,7,6,2,8,3,0,9,4],
        [5,8,0,3,7,9,6,1,4,2],
        [8,9,1,6,0,4,3,5,2,7],
        [9,4,5,3,1,2,6,8,7,0],
        [4,2,8,6,5,7,3,9,0,1],
        [2,7,9,3,8,0,6,4,1,5],
        [7,0,4,6,9,1,3,2,5,8]
    ]
    inv = [0,4,3,2,1,5,6,7,8,9]

    c = 0
    for i, ch in enumerate(reversed(num_str)):
        c = d[c][p[(i % 8)][int(ch)]]
    return inv[c]


def aadhaar_checksum(number: str) -> bool:
    # Aadhaar format: 12 digits where last digit is Verhoeff checksum.
    digits = re.sub(r"\D", "", number or "")
    if not re.fullmatch(r"\d{12}", digits):
        return False
    core = digits[:-1]
    checksum = int(digits[-1])
    try:
        expected = _verhoeff_compute_checksum(core)
        return checksum == expected
    except Exception:
        return False


def run_validations(image_path: str, doc_type: str, fields: Dict[str, Any]) -> Dict[str, Any]:
    results = {}
    raw = fields.get('raw_text', '')
    if doc_type == 'passport':
        results['mrz_ok'] = mrz_validate(raw)
        # attempt to parse MRZ if available
        if _MRZ_AVAILABLE:
            try:
                parsed = MRZ(raw)
                results['mrz_parsed'] = parsed.to_dict()
            except Exception:
                results['mrz_parsed'] = None
    if doc_type == 'aadhaar':
        doc_no = fields.get('document_number', '')
        results['aadhaar_format_ok'] = aadhaar_checksum(doc_no)
    # stub for QR and hologram detection
    results['qr_found'] = False
    results['hologram_detected'] = False
    return results
