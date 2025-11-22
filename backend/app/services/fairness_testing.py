"""
Fairness Testing Module for KYC System
Tests AI system performance across different demographic groups to detect bias
"""
import logging
from typing import Dict, List, Any, Optional
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)


class FairnessMetrics:
    """
    Calculate fairness metrics to detect bias in AI decisions.
    
    Monitors performance across demographic groups to ensure equitable treatment.
    """
    
    def __init__(self):
        self.test_results = defaultdict(list)
        self.performance_by_group = {}
        
    def record_result(self, group: str, prediction: bool, ground_truth: bool, 
                     confidence: float, features: Dict[str, float]):
        """
        Record a verification result for fairness analysis.
        
        Args:
            group: Demographic group identifier
            prediction: Model's prediction (True/False for pass/fail)
            ground_truth: Actual correct result
            confidence: Model's confidence score
            features: Feature values used in decision
        """
        self.test_results[group].append({
            'prediction': prediction,
            'ground_truth': ground_truth,
            'correct': prediction == ground_truth,
            'confidence': confidence,
            'features': features
        })
    
    def calculate_metrics(self, group: str) -> Dict[str, float]:
        """
        Calculate fairness metrics for a specific group.
        
        Args:
            group: Demographic group to analyze
            
        Returns:
            Dictionary of fairness metrics
        """
        results = self.test_results[group]
        if not results:
            return {'error': 'No results for group'}
        
        total = len(results)
        correct = sum(1 for r in results if r['correct'])
        accuracy = correct / total
        
        true_positives = sum(1 for r in results if r['prediction'] and r['ground_truth'])
        false_positives = sum(1 for r in results if r['prediction'] and not r['ground_truth'])
        false_negatives = sum(1 for r in results if not r['prediction'] and r['ground_truth'])
        true_negatives = sum(1 for r in results if not r['prediction'] and not r['ground_truth'])
        
        # Precision: Of those we approved, how many should we have approved?
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        
        # Recall: Of those who should be approved, how many did we approve?
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        
        # F1 Score: Harmonic mean of precision and recall
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        # Average confidence
        avg_confidence = np.mean([r['confidence'] for r in results])
        
        # False Positive Rate (Type I Error)
        fpr = false_positives / (false_positives + true_negatives) if (false_positives + true_negatives) > 0 else 0
        
        # False Negative Rate (Type II Error)
        fnr = false_negatives / (false_negatives + true_positives) if (false_negatives + true_positives) > 0 else 0
        
        return {
            'accuracy': round(accuracy, 4),
            'precision': round(precision, 4),
            'recall': round(recall, 4),
            'f1_score': round(f1_score, 4),
            'avg_confidence': round(avg_confidence, 4),
            'false_positive_rate': round(fpr, 4),
            'false_negative_rate': round(fnr, 4),
            'total_samples': total
        }
    
    def compare_groups(self, groups: List[str]) -> Dict[str, Any]:
        """
        Compare performance across multiple demographic groups.
        
        Args:
            groups: List of group identifiers to compare
            
        Returns:
            Comparison report with disparate impact analysis
        """
        metrics_by_group = {}
        for group in groups:
            metrics_by_group[group] = self.calculate_metrics(group)
        
        # Calculate disparate impact
        # Using "four-fifths rule" - if any group's accuracy is less than 80% of the best group's, flag it
        accuracies = {g: m['accuracy'] for g, m in metrics_by_group.items() if 'error' not in m}
        if accuracies:
            max_accuracy = max(accuracies.values())
            min_accuracy = min(accuracies.values())
            disparate_impact_ratio = min_accuracy / max_accuracy if max_accuracy > 0 else 0
            
            # Four-fifths rule threshold
            passes_four_fifths = disparate_impact_ratio >= 0.8
            
            # Calculate standard deviation to measure variance
            accuracy_std = np.std(list(accuracies.values()))
            
            # Identify groups with significantly lower performance
            flagged_groups = []
            for group, acc in accuracies.items():
                if acc < max_accuracy * 0.8:
                    flagged_groups.append({
                        'group': group,
                        'accuracy': acc,
                        'gap': round(max_accuracy - acc, 4)
                    })
        else:
            disparate_impact_ratio = 0
            passes_four_fifths = False
            accuracy_std = 0
            flagged_groups = []
        
        return {
            'metrics_by_group': metrics_by_group,
            'fairness_analysis': {
                'disparate_impact_ratio': round(disparate_impact_ratio, 4),
                'passes_four_fifths_rule': passes_four_fifths,
                'accuracy_variance': round(accuracy_std, 4),
                'max_accuracy': round(max_accuracy, 4) if accuracies else 0,
                'min_accuracy': round(min_accuracy, 4) if accuracies else 0,
                'flagged_groups': flagged_groups
            },
            'recommendation': self._generate_recommendation(disparate_impact_ratio, flagged_groups)
        }
    
    def _generate_recommendation(self, disparate_impact_ratio: float, 
                                flagged_groups: List[Dict]) -> str:
        """Generate actionable recommendation based on fairness analysis."""
        if disparate_impact_ratio >= 0.95:
            return "✅ EXCELLENT: Performance is consistent across all groups. No bias detected."
        elif disparate_impact_ratio >= 0.8:
            return "✅ PASS: Meets four-fifths rule. Minor variance acceptable but monitor ongoing."
        else:
            groups_str = ", ".join([g['group'] for g in flagged_groups])
            return f"⚠️ ATTENTION NEEDED: Disparate impact detected for {groups_str}. Investigate feature contributions and consider retraining with balanced dataset."
    
    def analyze_feature_bias(self, groups: List[str], feature_name: str) -> Dict[str, Any]:
        """
        Analyze if a specific feature disproportionately affects certain groups.
        
        Args:
            groups: List of groups to analyze
            feature_name: Name of feature to analyze
            
        Returns:
            Feature bias analysis
        """
        feature_impact = {}
        
        for group in groups:
            results = self.test_results[group]
            if not results:
                continue
            
            # Calculate average feature value for correct vs incorrect predictions
            correct_features = [r['features'].get(feature_name, 0) for r in results if r['correct']]
            incorrect_features = [r['features'].get(feature_name, 0) for r in results if not r['correct']]
            
            feature_impact[group] = {
                'avg_when_correct': round(np.mean(correct_features), 4) if correct_features else 0,
                'avg_when_incorrect': round(np.mean(incorrect_features), 4) if incorrect_features else 0,
                'correlation_with_accuracy': round(
                    np.corrcoef([r['features'].get(feature_name, 0) for r in results],
                               [1 if r['correct'] else 0 for r in results])[0, 1], 4
                ) if len(results) > 1 else 0
            }
        
        # Identify if feature affects groups differently
        correlations = [v['correlation_with_accuracy'] for v in feature_impact.values()]
        if correlations:
            correlation_variance = np.var(correlations)
            biased = correlation_variance > 0.1  # Threshold for concern
        else:
            correlation_variance = 0
            biased = False
        
        return {
            'feature': feature_name,
            'impact_by_group': feature_impact,
            'correlation_variance': round(correlation_variance, 4),
            'potentially_biased': biased,
            'recommendation': f"⚠️ Feature '{feature_name}' shows different impact across groups. Consider normalizing or removing." if biased else f"✅ Feature '{feature_name}' appears fair across groups."
        }


class FairnessTestSuite:
    """
    Test suite for running fairness evaluations on the KYC system.
    """
    
    def __init__(self):
        self.metrics = FairnessMetrics()
    
    def run_synthetic_fairness_test(self) -> Dict[str, Any]:
        """
        Run a synthetic fairness test with simulated diverse data.
        This demonstrates the fairness testing framework.
        
        In production, replace with real diverse test datasets.
        """
        logger.info("Running synthetic fairness test...")
        
        # Simulate test results for different demographic groups
        # In production, these would be real verification results
        groups = {
            'light_skin': {'base_accuracy': 0.96, 'samples': 100},
            'dark_skin': {'base_accuracy': 0.94, 'samples': 100},
            'male': {'base_accuracy': 0.95, 'samples': 100},
            'female': {'base_accuracy': 0.95, 'samples': 100},
            'age_18_30': {'base_accuracy': 0.97, 'samples': 100},
            'age_31_50': {'base_accuracy': 0.95, 'samples': 100},
            'age_51_plus': {'base_accuracy': 0.93, 'samples': 100}
        }
        
        # Generate synthetic test data
        for group, config in groups.items():
            base_acc = config['base_accuracy']
            samples = config['samples']
            
            for i in range(samples):
                # Simulate feature values with slight group variations
                features = {
                    'face_similarity': np.random.normal(0.75, 0.1),
                    'liveness_score': np.random.normal(0.80, 0.12),
                    'face_brightness': np.random.normal(120 if 'dark' in group else 130, 15),
                    'face_sharpness': np.random.normal(150, 30),
                    'eyes_detected': 2.0 if np.random.random() > 0.05 else 1.0
                }
                
                # Ground truth (what should be correct)
                ground_truth = np.random.random() < 0.6  # 60% legitimate users
                
                # Model prediction with group-specific accuracy
                if ground_truth:
                    prediction = np.random.random() < base_acc
                else:
                    prediction = np.random.random() > base_acc
                
                confidence = np.random.uniform(0.7, 0.95) if prediction == ground_truth else np.random.uniform(0.5, 0.7)
                
                self.metrics.record_result(
                    group=group,
                    prediction=prediction,
                    ground_truth=ground_truth,
                    confidence=confidence,
                    features=features
                )
        
        # Calculate comparative metrics
        all_groups = list(groups.keys())
        comparison = self.metrics.compare_groups(all_groups)
        
        # Analyze key features for bias
        feature_analyses = []
        for feature in ['face_brightness', 'face_sharpness', 'liveness_score']:
            analysis = self.metrics.analyze_feature_bias(all_groups, feature)
            feature_analyses.append(analysis)
        
        return {
            'test_type': 'synthetic_fairness_evaluation',
            'groups_tested': all_groups,
            'total_samples': sum(config['samples'] for config in groups.values()),
            'comparison': comparison,
            'feature_bias_analysis': feature_analyses,
            'summary': {
                'passes_fairness_check': comparison['fairness_analysis']['passes_four_fifths_rule'],
                'disparate_impact_ratio': comparison['fairness_analysis']['disparate_impact_ratio'],
                'recommendation': comparison['recommendation']
            }
        }
    
    def generate_fairness_report(self, test_results: Dict[str, Any]) -> str:
        """
        Generate a human-readable fairness report.
        
        Args:
            test_results: Results from fairness testing
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("\n" + "="*80)
        report.append("FAIRNESS TESTING REPORT")
        report.append("="*80)
        
        report.append(f"\n📊 Test Overview:")
        report.append(f"  Groups Tested: {len(test_results['groups_tested'])}")
        report.append(f"  Total Samples: {test_results['total_samples']}")
        
        report.append(f"\n📈 Performance by Group:")
        for group, metrics in test_results['comparison']['metrics_by_group'].items():
            if 'error' not in metrics:
                report.append(f"\n  {group}:")
                report.append(f"    Accuracy: {metrics['accuracy']:.1%}")
                report.append(f"    Precision: {metrics['precision']:.1%}")
                report.append(f"    Recall: {metrics['recall']:.1%}")
                report.append(f"    F1 Score: {metrics['f1_score']:.3f}")
        
        report.append(f"\n⚖️  Fairness Analysis:")
        fairness = test_results['comparison']['fairness_analysis']
        report.append(f"  Disparate Impact Ratio: {fairness['disparate_impact_ratio']:.3f}")
        report.append(f"  Four-Fifths Rule: {'✅ PASS' if fairness['passes_four_fifths_rule'] else '⚠️ FAIL'}")
        report.append(f"  Accuracy Variance: {fairness['accuracy_variance']:.4f}")
        
        if fairness['flagged_groups']:
            report.append(f"\n  ⚠️ Groups Requiring Attention:")
            for flag in fairness['flagged_groups']:
                report.append(f"    - {flag['group']}: {flag['accuracy']:.1%} (gap: {flag['gap']:.1%})")
        
        report.append(f"\n🔍 Feature Bias Analysis:")
        for analysis in test_results['feature_bias_analysis']:
            biased_marker = "⚠️" if analysis['potentially_biased'] else "✅"
            report.append(f"  {biased_marker} {analysis['feature']}: Variance = {analysis['correlation_variance']:.4f}")
        
        report.append(f"\n💡 Recommendation:")
        report.append(f"  {test_results['summary']['recommendation']}")
        
        report.append("\n" + "="*80 + "\n")
        
        return "\n".join(report)


# Global fairness test suite instance
fairness_suite = FairnessTestSuite()
