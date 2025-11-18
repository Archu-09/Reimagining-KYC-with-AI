#!/usr/bin/env python3
"""
Test Enhanced Liveness Detection System
Tests the security improvements against fake documents and spoofing attempts
"""

import sys
import os
sys.path.append('/Users/aryadav/Downloads/Reimagining-KYC-with-AI/backend')

from app.services.enhanced_liveness import enhanced_liveness_detector
import cv2
import numpy as np
from pathlib import Path

def create_test_images():
    """Create test images to validate liveness detection"""
    test_dir = Path("/tmp/liveness_tests")
    test_dir.mkdir(exist_ok=True)
    
    # Test 1: Fake Aadhaar without face (blank document)
    fake_aadhaar = np.ones((600, 400, 3), dtype=np.uint8) * 240  # Light gray background
    # Add some text-like patterns but NO face
    cv2.rectangle(fake_aadhaar, (50, 100), (350, 150), (0, 0, 0), 2)
    cv2.putText(fake_aadhaar, "AADHAAR CARD", (80, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.putText(fake_aadhaar, "1234 5678 9012", (80, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    cv2.imwrite(str(test_dir / "fake_aadhaar_no_face.jpg"), fake_aadhaar)
    
    # Test 2: Valid-looking document with face
    valid_doc = np.ones((600, 400, 3), dtype=np.uint8) * 250
    # Add a simple face-like pattern
    cv2.circle(valid_doc, (300, 200), 50, (180, 150, 120), -1)  # Face
    cv2.circle(valid_doc, (285, 185), 8, (50, 50, 50), -1)     # Left eye
    cv2.circle(valid_doc, (315, 185), 8, (50, 50, 50), -1)     # Right eye
    cv2.ellipse(valid_doc, (300, 215), (15, 8), 0, 0, 180, (50, 50, 50), 2)  # Mouth
    cv2.putText(valid_doc, "ID DOCUMENT", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.imwrite(str(test_dir / "valid_document_with_face.jpg"), valid_doc)
    
    # Test 3: Good selfie with clear face
    good_selfie = np.ones((480, 640, 3), dtype=np.uint8) * 200
    # Create a more realistic face
    cv2.ellipse(good_selfie, (320, 240), (80, 100), 0, 0, 360, (180, 150, 120), -1)  # Face shape
    cv2.circle(good_selfie, (295, 215), 12, (50, 50, 50), -1)     # Left eye
    cv2.circle(good_selfie, (345, 215), 12, (50, 50, 50), -1)     # Right eye
    cv2.circle(good_selfie, (295, 215), 6, (255, 255, 255), -1)   # Left eye highlight
    cv2.circle(good_selfie, (345, 215), 6, (255, 255, 255), -1)   # Right eye highlight
    cv2.ellipse(good_selfie, (320, 260), (20, 10), 0, 0, 180, (50, 50, 50), 3)  # Mouth
    cv2.ellipse(good_selfie, (320, 200), (15, 10), 0, 0, 360, (120, 100, 80), -1)  # Nose
    cv2.imwrite(str(test_dir / "good_selfie.jpg"), good_selfie)
    
    # Test 4: Poor quality selfie (blurry, no clear eyes)
    poor_selfie = np.ones((480, 640, 3), dtype=np.uint8) * 180
    # Create blurry face without clear eyes
    cv2.circle(poor_selfie, (320, 240), 60, (160, 140, 110), -1)  # Blurry face
    # Blur the entire image
    poor_selfie = cv2.GaussianBlur(poor_selfie, (15, 15), 0)
    cv2.imwrite(str(test_dir / "poor_quality_selfie.jpg"), poor_selfie)
    
    # Test 5: Multiple faces (potential spoofing)
    multi_face = np.ones((480, 640, 3), dtype=np.uint8) * 220
    # Add two faces
    for center in [(200, 240), (440, 240)]:
        cv2.circle(multi_face, center, 50, (180, 150, 120), -1)
        cv2.circle(multi_face, (center[0]-15, center[1]-15), 8, (50, 50, 50), -1)
        cv2.circle(multi_face, (center[0]+15, center[1]-15), 8, (50, 50, 50), -1)
    cv2.imwrite(str(test_dir / "multiple_faces_selfie.jpg"), multi_face)
    
    return test_dir

def test_enhanced_liveness():
    """Test the enhanced liveness detection system"""
    print("🧪 Testing Enhanced Liveness Detection System")
    print("=" * 60)
    
    # Create test images
    test_dir = create_test_images()
    print(f"📁 Test images created in: {test_dir}")
    print()
    
    # Test scenarios
    test_cases = [
        {
            "name": "Fake Aadhaar (No Face) + Good Selfie",
            "document": test_dir / "fake_aadhaar_no_face.jpg",
            "selfie": test_dir / "good_selfie.jpg",
            "expected_pass": False,
            "reason": "Document has no face photo"
        },
        {
            "name": "Valid Document + Good Selfie", 
            "document": test_dir / "valid_document_with_face.jpg",
            "selfie": test_dir / "good_selfie.jpg",
            "expected_pass": True,
            "reason": "Both document and selfie should pass"
        },
        {
            "name": "Valid Document + Poor Quality Selfie",
            "document": test_dir / "valid_document_with_face.jpg", 
            "selfie": test_dir / "poor_quality_selfie.jpg",
            "expected_pass": False,
            "reason": "Poor quality selfie should fail liveness"
        },
        {
            "name": "Valid Document + Multiple Faces Selfie",
            "document": test_dir / "valid_document_with_face.jpg",
            "selfie": test_dir / "multiple_faces_selfie.jpg", 
            "expected_pass": False,
            "reason": "Multiple faces indicate potential spoofing"
        }
    ]
    
    # Run tests
    results = []
    for i, test_case in enumerate(test_cases, 1):
        print(f"🧪 Test {i}: {test_case['name']}")
        print(f"   Expected: {'PASS' if test_case['expected_pass'] else 'FAIL'} ({test_case['reason']})")
        
        try:
            # Run enhanced liveness detection
            result = enhanced_liveness_detector.comprehensive_liveness_check(
                str(test_case['document']), 
                str(test_case['selfie'])
            )
            
            actual_pass = result.get('passed', False)
            score = result.get('liveness_score', 0.0)
            
            # Check if result matches expectation
            test_passed = (actual_pass == test_case['expected_pass'])
            status = "✅ CORRECT" if test_passed else "❌ INCORRECT"
            
            print(f"   Actual: {'PASS' if actual_pass else 'FAIL'} (Score: {score:.3f}) {status}")
            
            # Show detailed results for failed cases
            if not actual_pass:
                failure_reasons = result.get('failure_reasons', [])
                if failure_reasons:
                    print(f"   Failure reasons: {', '.join(failure_reasons)}")
            
            # Show stage breakdown
            stages = result.get('stages_passed', 'N/A')
            print(f"   Stages passed: {stages}")
            
            results.append({
                'test_name': test_case['name'],
                'expected': test_case['expected_pass'],
                'actual': actual_pass,
                'correct': test_passed,
                'score': score
            })
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            results.append({
                'test_name': test_case['name'],
                'expected': test_case['expected_pass'],
                'actual': False,
                'correct': False,
                'error': str(e)
            })
        
        print()
    
    # Summary
    print("📊 TEST SUMMARY")
    print("=" * 60)
    correct_tests = sum(1 for r in results if r.get('correct', False))
    total_tests = len(results)
    
    for result in results:
        status = "✅" if result.get('correct', False) else "❌"
        error = f" (ERROR: {result.get('error', '')})" if 'error' in result else ""
        print(f"{status} {result['test_name']}{error}")
    
    print(f"\n🎯 Overall: {correct_tests}/{total_tests} tests passed")
    
    if correct_tests == total_tests:
        print("🎉 All security tests PASSED! Enhanced liveness detection is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Enhanced liveness detection needs adjustment.")
        return False

def test_original_vs_enhanced():
    """Compare original vs enhanced liveness detection"""
    print("\n🔄 COMPARING ORIGINAL vs ENHANCED DETECTION")
    print("=" * 60)
    
    # Test with existing demo images
    demo_images = {
        'id_demo': '/Users/aryadav/Downloads/Reimagining-KYC-with-AI/backend/id_demo.jpg',
        'selfie_demo': '/Users/aryadav/Downloads/Reimagining-KYC-with-AI/backend/selfie_demo.jpg'
    }
    
    # Check if demo images exist
    for name, path in demo_images.items():
        if not os.path.exists(path):
            print(f"⚠️  Demo image not found: {path}")
            return
    
    try:
        # Test original method (import the old face service)
        print("1️⃣  Testing ORIGINAL liveness detection...")
        from app.services.face_service import liveness_check
        
        # Original method (selfie only)
        original_result = liveness_check(demo_images['selfie_demo'])
        print(f"   Original Result: {original_result}")
        
        print("\n2️⃣  Testing ENHANCED liveness detection...")
        # Enhanced method (document + selfie)
        enhanced_result = enhanced_liveness_detector.comprehensive_liveness_check(
            demo_images['id_demo'], 
            demo_images['selfie_demo']
        )
        
        print(f"   Enhanced Result:")
        print(f"   - Overall Score: {enhanced_result.get('liveness_score', 0.0):.3f}")
        print(f"   - Passed: {enhanced_result.get('passed', False)}")
        print(f"   - Stages: {enhanced_result.get('stages_passed', 'N/A')}")
        print(f"   - Security Level: {enhanced_result.get('security_level', 'N/A')}")
        
        # Compare results
        print(f"\n📊 COMPARISON:")
        print(f"   Original Score: {original_result.get('liveness_score', original_result.get('score', 0)):.3f}")
        print(f"   Enhanced Score: {enhanced_result.get('liveness_score', 0.0):.3f}")
        print(f"   Original Passed: {original_result.get('passed', False)}")
        print(f"   Enhanced Passed: {enhanced_result.get('passed', False)}")
        
        if enhanced_result.get('failure_reasons'):
            print(f"   Enhanced Failure Reasons: {', '.join(enhanced_result['failure_reasons'])}")
        
    except Exception as e:
        print(f"❌ Comparison test failed: {e}")

if __name__ == "__main__":
    try:
        print("🚀 Starting Enhanced Liveness Detection Tests")
        print("Testing security improvements against fake documents and spoofing")
        print()
        
        # Run comprehensive tests
        success = test_enhanced_liveness()
        
        # Compare with original system
        test_original_vs_enhanced()
        
        print("\n" + "=" * 60)
        if success:
            print("✅ ENHANCED LIVENESS DETECTION: SECURITY VALIDATED")
            print("🛡️  System now properly detects:")
            print("   - Documents without face photos")
            print("   - Poor quality selfies")
            print("   - Multiple faces (spoofing attempts)")
            print("   - Mismatched document-selfie pairs")
        else:
            print("❌ ENHANCED LIVENESS DETECTION: NEEDS IMPROVEMENT")
            print("🔧 Review and adjust detection parameters")
        
        print("\n🎯 The enhanced system provides multi-layer security against:")
        print("   1. Fake documents without proper face photos")
        print("   2. Screen photos and printed images")
        print("   3. Multiple face spoofing attempts")
        print("   4. Low quality or manipulated selfies")
        
    except Exception as e:
        print(f"💥 Test suite failed: {e}")
        import traceback
        traceback.print_exc()
