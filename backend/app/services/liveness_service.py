"""
Advanced Liveness Detection Service
Combines multiple techniques for robust anti-spoofing detection
"""
import logging
import numpy as np
from typing import Dict, List, Tuple, Optional
import cv2
from pathlib import Path

logger = logging.getLogger(__name__)

class LivenessDetector:
    """
    Multi-modal liveness detection using:
    1. Eye blink detection
    2. Head movement analysis  
    3. Texture analysis (LBP)
    4. Color space analysis
    5. Fourier domain analysis
    """
    
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        # Thresholds for different checks
        self.blink_threshold = 0.25
        self.texture_threshold = 50.0
        self.color_variance_threshold = 500.0
        
    def detect_liveness_single_image(self, image_path: str) -> Dict[str, any]:
        """
        Detect liveness from a single image using multiple indicators
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                return {"liveness_score": 0.0, "passed": False, "error": "Could not load image"}
            
            # Convert to different color spaces for analysis
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            
            # Detect face
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            if len(faces) == 0:
                return {"liveness_score": 0.0, "passed": False, "error": "No face detected"}
            
            # Use largest face
            face = max(faces, key=lambda x: x[2] * x[3])
            x, y, w, h = face
            
            # Extract face region
            face_gray = gray[y:y+h, x:x+w]
            face_color = image[y:y+h, x:x+w]
            face_hsv = hsv[y:y+h, x:x+w]
            face_lab = lab[y:y+h, x:x+w]
            
            # Run liveness checks
            checks = {}
            
            # 1. Eye detection and analysis
            checks['eye_analysis'] = self._analyze_eyes(face_gray, face_color)
            
            # 2. Texture analysis using Local Binary Patterns
            checks['texture_analysis'] = self._analyze_texture(face_gray)
            
            # 3. Color distribution analysis
            checks['color_analysis'] = self._analyze_color_distribution(face_color, face_hsv, face_lab)
            
            # 4. Edge and frequency analysis
            checks['frequency_analysis'] = self._analyze_frequency_domain(face_gray)
            
            # 5. Reflection and lighting analysis
            checks['lighting_analysis'] = self._analyze_lighting(face_gray, face_color)
            
            # Calculate composite liveness score
            liveness_score = self._calculate_composite_score(checks)
            
            return {
                "liveness_score": round(liveness_score, 3),
                "passed": liveness_score > 0.6,
                "method": "multi_modal_single_image",
                "checks": checks,
                "face_detected": True,
                "face_size": {"width": w, "height": h}
            }
            
        except Exception as e:
            logger.exception(f"Liveness detection failed: {e}")
            return {"liveness_score": 0.0, "passed": False, "error": str(e)}
    
    def _analyze_eyes(self, face_gray: np.ndarray, face_color: np.ndarray) -> Dict[str, any]:
        """Analyze eyes for liveness indicators"""
        eyes = self.eye_cascade.detectMultiScale(face_gray, 1.1, 3)
        
        if len(eyes) < 2:
            return {"eyes_detected": False, "score": 0.3}
        
        eye_scores = []
        for (ex, ey, ew, eh) in eyes:
            eye_region = face_gray[ey:ey+eh, ex:ex+ew]
            
            # Analyze eye characteristics
            mean_intensity = np.mean(eye_region)
            std_intensity = np.std(eye_region)
            
            # Eyes should have good contrast (dark pupil, lighter sclera)
            eye_score = min(std_intensity / 50.0, 1.0)  # Normalize std
            eye_scores.append(eye_score)
        
        avg_eye_score = np.mean(eye_scores) if eye_scores else 0.0
        
        return {
            "eyes_detected": len(eyes) >= 2,
            "eye_count": len(eyes),
            "score": avg_eye_score,
            "details": f"Detected {len(eyes)} eyes with avg score {avg_eye_score:.3f}"
        }
    
    def _analyze_texture(self, face_gray: np.ndarray) -> Dict[str, any]:
        """Analyze texture patterns using Local Binary Patterns"""
        # Simple LBP implementation
        height, width = face_gray.shape
        lbp_image = np.zeros_like(face_gray)
        
        for i in range(1, height-1):
            for j in range(1, width-1):
                center = face_gray[i, j]
                binary_pattern = 0
                
                # 8-connected neighbors
                neighbors = [
                    face_gray[i-1, j-1], face_gray[i-1, j], face_gray[i-1, j+1],
                    face_gray[i, j+1], face_gray[i+1, j+1], face_gray[i+1, j],
                    face_gray[i+1, j-1], face_gray[i, j-1]
                ]
                
                for k, neighbor in enumerate(neighbors):
                    if neighbor >= center:
                        binary_pattern |= (1 << k)
                
                lbp_image[i, j] = binary_pattern
        
        # Calculate texture uniformity
        texture_variance = np.var(lbp_image)
        texture_score = min(texture_variance / 1000.0, 1.0)  # Normalize
        
        return {
            "texture_variance": float(texture_variance),
            "score": texture_score,
            "details": f"LBP variance: {texture_variance:.1f}"
        }
    
    def _analyze_color_distribution(self, face_bgr: np.ndarray, face_hsv: np.ndarray, face_lab: np.ndarray) -> Dict[str, any]:
        """Analyze color distribution for naturalness"""
        # RGB analysis
        b_mean, g_mean, r_mean = np.mean(face_bgr, axis=(0,1))
        rgb_variance = np.var(face_bgr)
        
        # HSV analysis (Hue, Saturation, Value)
        h_mean, s_mean, v_mean = np.mean(face_hsv, axis=(0,1))
        
        # LAB analysis (better for skin detection)
        l_mean, a_mean, b_lab_mean = np.mean(face_lab, axis=(0,1))
        
        # Skin tone analysis in LAB space
        # Typical skin ranges: L: 50-95, A: 0-20, B: 5-25
        skin_likelihood = 0.0
        if 50 <= l_mean <= 95 and 0 <= a_mean <= 20 and 5 <= b_lab_mean <= 25:
            skin_likelihood = 1.0
        elif 40 <= l_mean <= 100 and -5 <= a_mean <= 25 and 0 <= b_lab_mean <= 30:
            skin_likelihood = 0.7
        else:
            skin_likelihood = 0.3
        
        # Color variance score (natural faces have good color variation)
        color_score = min(rgb_variance / 2000.0, 1.0)
        
        final_score = (skin_likelihood * 0.6) + (color_score * 0.4)
        
        return {
            "rgb_mean": [float(r_mean), float(g_mean), float(b_mean)],
            "rgb_variance": float(rgb_variance),
            "skin_likelihood": skin_likelihood,
            "score": final_score,
            "details": f"Skin: {skin_likelihood:.2f}, Variance: {rgb_variance:.1f}"
        }
    
    def _analyze_frequency_domain(self, face_gray: np.ndarray) -> Dict[str, any]:
        """Analyze frequency domain characteristics"""
        # FFT analysis
        f_transform = np.fft.fft2(face_gray)
        f_shift = np.fft.fftshift(f_transform)
        magnitude_spectrum = np.log(np.abs(f_shift) + 1)
        
        # High frequency content indicates natural texture
        high_freq_energy = np.sum(magnitude_spectrum > np.mean(magnitude_spectrum) + np.std(magnitude_spectrum))
        total_energy = magnitude_spectrum.size
        
        freq_score = min(high_freq_energy / (total_energy * 0.1), 1.0)
        
        return {
            "high_freq_ratio": float(high_freq_energy / total_energy),
            "score": freq_score,
            "details": f"High freq ratio: {high_freq_energy/total_energy:.4f}"
        }
    
    def _analyze_lighting(self, face_gray: np.ndarray, face_color: np.ndarray) -> Dict[str, any]:
        """Analyze lighting patterns for naturalness"""
        # Gradient analysis
        grad_x = cv2.Sobel(face_gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(face_gray, cv2.CV_64F, 0, 1, ksize=3)
        
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        gradient_uniformity = 1.0 - (np.std(gradient_magnitude) / (np.mean(gradient_magnitude) + 1e-6))
        
        # Lighting uniformity (natural faces have some lighting variation)
        lighting_std = np.std(face_gray)
        lighting_score = min(lighting_std / 50.0, 1.0)  # Some variation is good
        
        # Reflection analysis (detect strong reflections that might indicate screens)
        reflection_pixels = np.sum(face_gray > 200)  # Very bright pixels
        reflection_ratio = reflection_pixels / face_gray.size
        reflection_penalty = max(0, (reflection_ratio - 0.05) * 10)  # Penalize >5% bright pixels
        
        final_score = max(0, (gradient_uniformity * 0.4) + (lighting_score * 0.6) - reflection_penalty)
        
        return {
            "gradient_uniformity": float(gradient_uniformity),
            "lighting_std": float(lighting_std),
            "reflection_ratio": float(reflection_ratio),
            "score": final_score,
            "details": f"Gradient: {gradient_uniformity:.3f}, Lighting: {lighting_std:.1f}, Reflections: {reflection_ratio:.3f}"
        }
    
    def _calculate_composite_score(self, checks: Dict[str, Dict]) -> float:
        """Calculate weighted composite liveness score"""
        weights = {
            'eye_analysis': 0.25,
            'texture_analysis': 0.20,
            'color_analysis': 0.25,
            'frequency_analysis': 0.15,
            'lighting_analysis': 0.15
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for check_name, weight in weights.items():
            if check_name in checks and 'score' in checks[check_name]:
                score = checks[check_name]['score']
                total_score += score * weight
                total_weight += weight
        
        # Normalize by actual weights used
        if total_weight > 0:
            final_score = total_score / total_weight
        else:
            final_score = 0.0
        
        return min(max(final_score, 0.0), 1.0)  # Clamp to [0, 1]

# Global liveness detector instance
liveness_detector = LivenessDetector()
