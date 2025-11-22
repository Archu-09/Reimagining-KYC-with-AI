"""
SHAP Visualization utilities for KYC explainability
Generates visualizations and reports for AI decision transparency
"""
import logging
from typing import Dict, List, Any
import json

logger = logging.getLogger(__name__)


class SHAPVisualizer:
    """
    Utility class for creating SHAP-style visualizations and explanations
    for KYC verification decisions.
    """
    
    @staticmethod
    def generate_waterfall_data(explanation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate data for waterfall chart visualization showing how features
        contribute to the final decision.
        
        Args:
            explanation: SHAP explanation dictionary from face_service
            
        Returns:
            Visualization data compatible with frontend charting libraries
        """
        feature_importance = explanation.get('feature_importance', [])
        baseline = explanation.get('baseline', 0.5)
        
        # Build waterfall data
        waterfall = []
        cumulative = baseline
        
        waterfall.append({
            'label': 'Baseline',
            'value': baseline,
            'cumulative': cumulative,
            'type': 'baseline'
        })
        
        for feat in feature_importance:
            contribution = feat['contribution']
            cumulative += contribution
            
            waterfall.append({
                'label': feat['feature'].replace('_', ' ').title(),
                'value': contribution,
                'cumulative': cumulative,
                'type': 'positive' if contribution > 0 else 'negative',
                'original_value': feat['value']
            })
        
        waterfall.append({
            'label': 'Final Score',
            'value': cumulative,
            'cumulative': cumulative,
            'type': 'final'
        })
        
        return {
            'waterfall': waterfall,
            'baseline': baseline,
            'final_prediction': cumulative
        }
    
    @staticmethod
    def generate_force_plot_data(explanation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate data for force plot showing positive and negative contributions.
        
        Args:
            explanation: SHAP explanation dictionary
            
        Returns:
            Force plot visualization data
        """
        feature_importance = explanation.get('feature_importance', [])
        baseline = explanation.get('baseline', 0.5)
        
        positive_features = []
        negative_features = []
        
        for feat in feature_importance:
            feature_data = {
                'feature': feat['feature'].replace('_', ' ').title(),
                'value': feat['value'],
                'contribution': abs(feat['contribution'])
            }
            
            if feat['contribution'] > 0:
                positive_features.append(feature_data)
            else:
                negative_features.append(feature_data)
        
        return {
            'baseline': baseline,
            'positive_features': positive_features,
            'negative_features': negative_features,
            'final_value': baseline + explanation.get('total_contribution', 0)
        }
    
    @staticmethod
    def generate_bar_chart_data(explanation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate data for bar chart showing feature importance.
        
        Args:
            explanation: SHAP explanation dictionary
            
        Returns:
            Bar chart data sorted by absolute importance
        """
        feature_importance = explanation.get('feature_importance', [])
        
        chart_data = []
        for feat in feature_importance:
            chart_data.append({
                'feature': feat['feature'].replace('_', ' ').title(),
                'importance': feat['abs_contribution'],
                'contribution': feat['contribution'],
                'value': feat['value'],
                'direction': 'positive' if feat['contribution'] > 0 else 'negative'
            })
        
        return {
            'features': chart_data,
            'max_importance': max([f['importance'] for f in chart_data]) if chart_data else 1.0
        }
    
    @staticmethod
    def generate_decision_summary(explanation: Dict[str, Any], 
                                  decision_type: str = 'verification') -> Dict[str, Any]:
        """
        Generate a comprehensive decision summary with explanations.
        
        Args:
            explanation: SHAP explanation dictionary
            decision_type: Type of decision ('verification', 'liveness', 'match')
            
        Returns:
            Comprehensive decision summary
        """
        top_features = explanation.get('top_3_features', [])
        confidence = explanation.get('confidence', 0.0)
        decision_factors = explanation.get('decision_factors', [])
        
        # Determine decision quality
        if confidence > 0.8:
            quality = "HIGH"
            quality_description = "The decision is strongly supported by multiple factors"
        elif confidence > 0.5:
            quality = "MEDIUM"
            quality_description = "The decision has moderate support from the evidence"
        else:
            quality = "LOW"
            quality_description = "The decision has weak support and should be reviewed"
        
        # Generate key insights
        key_insights = []
        for i, factor in enumerate(top_features, 1):
            feature_name = factor['feature'].replace('_', ' ').title()
            value = factor['value']
            contribution = factor['contribution']
            
            if contribution > 0.5:
                impact = "strongly supported"
            elif contribution > 0:
                impact = "supported"
            elif contribution > -0.5:
                impact = "opposed"
            else:
                impact = "strongly opposed"
            
            key_insights.append({
                'rank': i,
                'feature': feature_name,
                'value': round(value, 3),
                'impact': impact,
                'contribution_score': round(contribution, 3)
            })
        
        return {
            'decision_type': decision_type,
            'confidence': round(confidence, 3),
            'quality': quality,
            'quality_description': quality_description,
            'key_insights': key_insights,
            'narrative': decision_factors,
            'recommendation': SHAPVisualizer._generate_recommendation(confidence, top_features)
        }
    
    @staticmethod
    def _generate_recommendation(confidence: float, top_features: List[Dict]) -> str:
        """
        Generate action recommendation based on confidence and features.
        
        Args:
            confidence: Decision confidence score
            top_features: Top contributing features
            
        Returns:
            Recommendation string
        """
        if confidence > 0.8:
            return "APPROVE: High confidence decision, proceed with verification"
        elif confidence > 0.5:
            if any(f['contribution'] < -0.3 for f in top_features):
                return "REVIEW: Some concerning factors detected, manual review recommended"
            else:
                return "APPROVE WITH CAUTION: Moderate confidence, consider additional checks"
        else:
            return "REJECT OR REVIEW: Low confidence decision, manual review required"
    
    @staticmethod
    def create_explainability_report(face_match_result: Dict[str, Any],
                                    liveness_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create comprehensive explainability report for complete KYC verification.
        
        Args:
            face_match_result: Result from face matching with explainability
            liveness_result: Result from liveness check with explainability
            
        Returns:
            Complete explainability report
        """
        face_explanation = face_match_result.get('explainability', {})
        liveness_explanation = liveness_result.get('explainability', {})
        
        # Calculate overall verification confidence
        face_confidence = face_explanation.get('confidence', 0.0)
        liveness_confidence = liveness_explanation.get('confidence', 0.0)
        overall_confidence = (face_confidence * 0.5) + (liveness_confidence * 0.5)
        
        # Determine overall decision
        face_passed = face_match_result.get('match', False)
        liveness_passed = liveness_result.get('passed', False)
        overall_passed = face_passed and liveness_passed
        
        report = {
            'timestamp': None,  # Set by caller
            'overall_decision': 'APPROVED' if overall_passed else 'REJECTED',
            'overall_confidence': round(overall_confidence, 3),
            'components': {
                'face_matching': {
                    'passed': face_passed,
                    'confidence': round(face_confidence, 3),
                    'similarity_score': face_match_result.get('similarity', 0.0),
                    'explanation': SHAPVisualizer.generate_decision_summary(
                        face_explanation, 'face_matching'
                    ),
                    'visualizations': {
                        'waterfall': SHAPVisualizer.generate_waterfall_data(face_explanation),
                        'force_plot': SHAPVisualizer.generate_force_plot_data(face_explanation),
                        'bar_chart': SHAPVisualizer.generate_bar_chart_data(face_explanation)
                    }
                },
                'liveness_detection': {
                    'passed': liveness_passed,
                    'confidence': round(liveness_confidence, 3),
                    'liveness_score': liveness_result.get('liveness_score', 0.0),
                    'explanation': SHAPVisualizer.generate_decision_summary(
                        liveness_explanation, 'liveness'
                    ),
                    'visualizations': {
                        'waterfall': SHAPVisualizer.generate_waterfall_data(liveness_explanation),
                        'force_plot': SHAPVisualizer.generate_force_plot_data(liveness_explanation),
                        'bar_chart': SHAPVisualizer.generate_bar_chart_data(liveness_explanation)
                    }
                }
            },
            'risk_assessment': {
                'level': 'LOW' if overall_confidence > 0.8 else 'MEDIUM' if overall_confidence > 0.5 else 'HIGH',
                'factors': _combine_risk_factors(face_explanation, liveness_explanation)
            },
            'recommendations': _generate_final_recommendations(overall_passed, overall_confidence)
        }
        
        return report


def _combine_risk_factors(face_exp: Dict, liveness_exp: Dict) -> List[str]:
    """Combine risk factors from both explanations."""
    factors = []
    
    # Extract negative factors
    face_features = face_exp.get('feature_importance', [])
    for feat in face_features:
        if feat['contribution'] < -0.3:
            factors.append(f"Face matching: {feat['feature']} showed concerning values")
    
    liveness_features = liveness_exp.get('feature_importance', [])
    for feat in liveness_features:
        if feat['contribution'] < -0.3:
            factors.append(f"Liveness detection: {feat['feature']} showed concerning values")
    
    if not factors:
        factors.append("No significant risk factors detected")
    
    return factors


def _generate_final_recommendations(passed: bool, confidence: float) -> List[str]:
    """Generate final action recommendations."""
    recommendations = []
    
    if passed:
        if confidence > 0.8:
            recommendations.append("✅ Approve verification - High confidence")
            recommendations.append("Proceed with account activation")
        else:
            recommendations.append("⚠️ Conditional approval - Moderate confidence")
            recommendations.append("Consider additional verification steps")
            recommendations.append("Monitor account activity closely")
    else:
        recommendations.append("❌ Reject verification - Failed checks")
        recommendations.append("Request user to retry with better quality images")
        recommendations.append("If issue persists, escalate to manual review")
    
    return recommendations


# Global visualizer instance
shap_visualizer = SHAPVisualizer()
