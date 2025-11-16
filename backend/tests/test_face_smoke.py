#!/usr/bin/env python3
"""
Smoke test for face matching service.

To run:
1. Install dependencies: pip install -r requirements.txt (torch + facenet-pytorch are optional but recommended)
2. python3 tests/test_face_smoke.py <path_to_id_image> <path_to_selfie>

Without real images, this will just verify the function signatures and fallback behavior.
"""

import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)

def test_face_matching():
    from app.services import face_service

    print("✓ face_service imported successfully")

    # Test 1: Check that functions exist
    assert hasattr(face_service, "match_faces"), "match_faces function missing"
    assert hasattr(face_service, "liveness_check"), "liveness_check function missing"
    print("✓ All functions present")

    # Test 2: Test with dummy paths (will fallback gracefully)
    dummy_id = "/tmp/dummy_id.jpg"
    dummy_selfie = "/tmp/dummy_selfie.jpg"
    
    # Create dummy image files if they don't exist
    try:
        from PIL import Image
        if not Path(dummy_id).exists():
            img = Image.new('RGB', (160, 160), color='red')
            img.save(dummy_id)
        if not Path(dummy_selfie).exists():
            img = Image.new('RGB', (160, 160), color='blue')
            img.save(dummy_selfie)
        print(f"✓ Created dummy images at {dummy_id} and {dummy_selfie}")
    except Exception as e:
        print(f"⚠ Could not create dummy images: {e}")

    try:
        result = face_service.match_faces(dummy_id, dummy_selfie)
        assert isinstance(result, dict), "match_faces should return dict"
        assert "similarity" in result, "Result missing 'similarity'"
        assert "match" in result, "Result missing 'match'"
        assert "method" in result, "Result missing 'method'"
        print(f"✓ match_faces returned: {result}")
    except FileNotFoundError:
        print("⚠ Dummy images not found; skipping face matching test")
    except Exception as e:
        print(f"✗ match_faces failed: {e}")
        return False

    try:
        result = face_service.liveness_check(dummy_selfie)
        assert isinstance(result, dict), "liveness_check should return dict"
        assert "liveness_score" in result, "Result missing 'liveness_score'"
        print(f"✓ liveness_check returned: {result}")
    except FileNotFoundError:
        print("⚠ Dummy image not found; skipping liveness test")
    except Exception as e:
        print(f"✗ liveness_check failed: {e}")
        return False

    print("\n✓ All smoke tests passed!")
    return True


if __name__ == "__main__":
    try:
        success = test_face_matching()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"✗ Smoke test failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
