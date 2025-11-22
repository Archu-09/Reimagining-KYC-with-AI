"""
SHAP Explainability Demo for KYC System
Demonstrates how the explainability features work with sample data
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app.services.shap_visualizer import shap_visualizer
import json

def demo_face_matching_explanation():
    """Demonstrate face matching explainability."""
    print("\n" + "="*80)
    print("DEMO 1: Face Matching Explainability")
    print("="*80)
    
    # Simulate face matching result with explainability
    face_match_result = {
        "similarity": 0.85,
        "match": True,
        "method": "facenet",
        "explainability": {
            "shap_values": {
                "face_similarity": 0.35,
                "embedding_confidence": 0.25
            },
            "feature_importance": [
                {
                    "feature": "face_similarity",
                    "value": 0.85,
                    "contribution": 0.70,
                    "abs_contribution": 0.70
                },
                {
                    "feature": "embedding_confidence",
                    "value": 0.92,
                    "contribution": 0.42,
                    "abs_contribution": 0.42
                }
            ],
            "baseline": 0.5,
            "prediction": 1,
            "confidence": 0.85,
            "total_contribution": 1.12,
            "top_3_features": [
                {
                    "feature": "face_similarity",
                    "value": 0.85,
                    "contribution": 0.70,
                    "abs_contribution": 0.70
                }
            ],
            "decision_factors": [
                "Face similarity of 85.00% strongly supported the decision",
                "Embedding confidence of 0.92 supported the decision"
            ]
        }
    }
    
    # Generate visualizations
    waterfall = shap_visualizer.generate_waterfall_data(face_match_result['explainability'])
    force_plot = shap_visualizer.generate_force_plot_data(face_match_result['explainability'])
    bar_chart = shap_visualizer.generate_bar_chart_data(face_match_result['explainability'])
    summary = shap_visualizer.generate_decision_summary(face_match_result['explainability'], 'face_matching')
    
    print("\n📊 Decision Summary:")
    print(json.dumps(summary, indent=2))
    
    print("\n📈 Waterfall Chart Data:")
    print(json.dumps(waterfall, indent=2))
    
    print("\n💪 Force Plot Data:")
    print(json.dumps(force_plot, indent=2))
    
    print("\n📊 Feature Importance:")
    for feat in bar_chart['features']:
        bar = "█" * int(feat['importance'] * 20)
        direction = "✓" if feat['direction'] == 'positive' else "✗"
        print(f"  {direction} {feat['feature']:30s} {bar} {feat['importance']:.3f}")


def demo_liveness_explanation():
    """Demonstrate liveness detection explainability."""
    print("\n" + "="*80)
    print("DEMO 2: Liveness Detection Explainability")
    print("="*80)
    
    # Simulate liveness result with explainability
    liveness_result = {
        "liveness_score": 0.82,
        "passed": True,
        "method": "opencv-strict",
        "explainability": {
            "shap_values": {
                "liveness_score": 0.32,
                "face_area_ratio": 0.15,
                "eyes_detected": 1.0,
                "face_sharpness": 0.08,
                "face_brightness": 0.05,
                "texture_variation": 0.02
            },
            "feature_importance": [
                {
                    "feature": "eyes_detected",
                    "value": 2.0,
                    "contribution": 1.0,
                    "abs_contribution": 1.0
                },
                {
                    "feature": "liveness_score",
                    "value": 0.82,
                    "contribution": 0.64,
                    "abs_contribution": 0.64
                },
                {
                    "feature": "face_area_ratio",
                    "value": 0.15,
                    "contribution": 0.30,
                    "abs_contribution": 0.30
                },
                {
                    "feature": "face_sharpness",
                    "value": 150.5,
                    "contribution": 0.25,
                    "abs_contribution": 0.25
                },
                {
                    "feature": "face_brightness",
                    "value": 125.3,
                    "contribution": 0.15,
                    "abs_contribution": 0.15
                }
            ],
            "baseline": 0.5,
            "prediction": 1,
            "confidence": 0.87,
            "total_contribution": 2.34,
            "top_3_features": [
                {"feature": "eyes_detected", "value": 2.0, "contribution": 1.0, "abs_contribution": 1.0},
                {"feature": "liveness_score", "value": 0.82, "contribution": 0.64, "abs_contribution": 0.64},
                {"feature": "face_area_ratio", "value": 0.15, "contribution": 0.30, "abs_contribution": 0.30}
            ],
            "decision_factors": [
                "Detection of 2 eye(s) strongly supported the decision",
                "Liveness score of 82.00% strongly supported the decision",
                "Face size ratio of 15.00% supported the decision"
            ]
        }
    }
    
    # Generate visualizations
    summary = shap_visualizer.generate_decision_summary(liveness_result['explainability'], 'liveness')
    bar_chart = shap_visualizer.generate_bar_chart_data(liveness_result['explainability'])
    
    print("\n📊 Decision Summary:")
    print(json.dumps(summary, indent=2))
    
    print("\n📊 Feature Importance:")
    for feat in bar_chart['features']:
        bar = "█" * int(feat['importance'] * 20)
        direction = "✓" if feat['direction'] == 'positive' else "✗"
        print(f"  {direction} {feat['feature']:30s} {bar} {feat['importance']:.3f}")
    
    print("\n💡 Decision Narrative:")
    for factor in liveness_result['explainability']['decision_factors']:
        print(f"  • {factor}")


def demo_complete_report():
    """Demonstrate complete explainability report."""
    print("\n" + "="*80)
    print("DEMO 3: Complete KYC Explainability Report")
    print("="*80)
    
    # Simulate complete verification results
    face_match = {
        "similarity": 0.85,
        "match": True,
        "explainability": {
            "confidence": 0.85,
            "feature_importance": [
                {"feature": "face_similarity", "value": 0.85, "contribution": 0.70, "abs_contribution": 0.70}
            ],
            "baseline": 0.5,
            "decision_factors": ["Face similarity of 85% strongly supported the decision"]
        }
    }
    
    liveness = {
        "liveness_score": 0.82,
        "passed": True,
        "explainability": {
            "confidence": 0.87,
            "feature_importance": [
                {"feature": "eyes_detected", "value": 2.0, "contribution": 1.0, "abs_contribution": 1.0},
                {"feature": "liveness_score", "value": 0.82, "contribution": 0.64, "abs_contribution": 0.64}
            ],
            "baseline": 0.5,
            "decision_factors": ["Detection of 2 eyes strongly supported the decision"]
        }
    }
    
    # Generate complete report
    report = shap_visualizer.create_explainability_report(face_match, liveness)
    
    print("\n📋 Complete Explainability Report:")
    print(json.dumps(report, indent=2))
    
    print("\n🎯 Overall Decision:", report['overall_decision'])
    print("📊 Overall Confidence:", f"{report['overall_confidence']:.1%}")
    print("⚠️  Risk Level:", report['risk_assessment']['level'])
    
    print("\n📝 Recommendations:")
    for rec in report['recommendations']:
        print(f"  {rec}")


def main():
    """Run all demonstrations."""
    print("\n" + "="*80)
    print("🔍 KYC System - Explainable AI Demonstration")
    print("="*80)
    print("\nThis demo shows how SHAP-style explanations make AI decisions transparent")
    print("and auditable for regulatory compliance and user trust.")
    
    demo_face_matching_explanation()
    demo_liveness_explanation()
    demo_complete_report()
    
    print("\n" + "="*80)
    print("✅ Demo Complete!")
    print("="*80)
    print("\nKey Takeaways:")
    print("  1. Every AI decision is fully explainable with feature importance")
    print("  2. SHAP values show how each factor contributed to the decision")
    print("  3. Multiple visualization formats available for different stakeholders")
    print("  4. Complete audit trail for regulatory compliance")
    print("  5. Transparent risk assessment with actionable recommendations")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
