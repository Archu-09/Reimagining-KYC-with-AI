import tempfile
import os
from PIL import Image, ImageDraw
import pytest

from app.services import forgery


def _make_clean_image(path: str):
    img = Image.new('RGB', (400, 200), color=(240, 240, 240))
    d = ImageDraw.Draw(img)
    d.text((10, 10), "TEST DOCUMENT CLEAN", fill=(10, 10, 10))
    img.save(path, format='JPEG')


def _make_tampered_image(path: str):
    img = Image.new('RGB', (400, 200), color=(240, 240, 240))
    d = ImageDraw.Draw(img)
    d.text((10, 10), "TEST DOCUMENT CLEAN", fill=(10, 10, 10))
    # add a tampered rectangle (simulate pasted signature)
    d.rectangle([250, 50, 360, 120], fill=(20, 20, 20))
    img.save(path, format='JPEG')


def test_ela_scores_differ():
    with tempfile.TemporaryDirectory() as td:
        clean = os.path.join(td, 'clean.jpg')
        tampered = os.path.join(td, 'tampered.jpg')
        _make_clean_image(clean)
        _make_tampered_image(tampered)

        s_clean = forgery.ela_score(clean)
        s_tampered = forgery.ela_score(tampered)

        assert isinstance(s_clean, float)
        assert isinstance(s_tampered, float)
        assert s_tampered >= s_clean


def test_paste_heuristic_detects_tamper():
    with tempfile.TemporaryDirectory() as td:
        clean = os.path.join(td, 'clean.jpg')
        tampered = os.path.join(td, 'tampered.jpg')
        _make_clean_image(clean)
        _make_tampered_image(tampered)

        p_clean = forgery.detect_pasted_regions_heurstic(clean)
        p_tampered = forgery.detect_pasted_regions_heurstic(tampered)

        assert 'suspiciousness' in p_clean
        assert 'suspiciousness' in p_tampered
        assert p_tampered['suspiciousness'] >= p_clean['suspiciousness']


def test_microtext_fallback_or_detection():
    with tempfile.TemporaryDirectory() as td:
        img = os.path.join(td, 'clean.jpg')
        _make_clean_image(img)
        res = forgery.detect_microtext(img)
        assert isinstance(res, dict)


def test_run_forgery_checks_returns_report():
    with tempfile.TemporaryDirectory() as td:
        img = os.path.join(td, 'clean.jpg')
        _make_clean_image(img)
        rpt = forgery.run_forgery_checks(img)
        assert isinstance(rpt, dict)
        assert 'ela_score' in rpt
        assert 'flags' in rpt
