"""
AI-powered failure analysis using NLP and ML techniques.
"""
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from core.logger import test_logger
from config.settings import settings

try:
    from transformers import pipeline, AutoTokenizer, AutoModel
    import torch
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    import nltk
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    test_logger.warning("AI analysis dependencies not available. Install transformers, torch, scikit-learn, and nltk.")

@dataclass
class FailureAnalysis:
    """Data class for failure analysis results."""
    category: str
    confidence: float
    root_cause: str
    suggestions: List[str]
    similar_failures: List[str]
    patterns: Dict[str, Any]

class FailureCategorizer:
    """Categorize test failures using ML classification."""
    
    def __init__(self):
        self.categories = {
            'element_not_found': ['element not found', 'selector', 'locator', 'xpath', 'css'],
            'timeout': ['timeout', 'wait', 'element not visible', 'page load'],
            'assertion_error': ['assertion', 'expected', 'actual', 'assert'],
            'network_error': ['network', 'connection', 'http', 'request', 'response'],
            'permission_error': ['permission', 'access', 'forbidden', 'unauthorized'],
            'data_error': ['invalid data', 'format', 'validation', 'schema'],
            'environment_error': ['driver', 'browser', 'device', 'platform'],
            'application_error': ['application error', 'crash', 'exception', 'bug']
        }
    
    def categorize_failure(self, error_message: str, stack_trace: str = "") -> Dict[str, float]:
        """Categorize failure based on error message and stack trace."""
        text = f"{error_message} {stack_trace}".lower()
        
        scores = {}
        for category, keywords in self.categories.items():
            score = 0
            for keyword in keywords:
                if keyword in text:
                    score += text.count(keyword)
            
            # Normalize score
            scores[category] = score / len(keywords) if keywords else 0
        
        return scores
    
    def get_best_category(self, error_message: str, stack_trace: str = "") -> tuple:
        """Get the most likely failure category."""
        scores = self.categorize_failure(error_message, stack_trace)
        
        if not scores or max(scores.values()) == 0:
            return "unknown", 0.0
        
        best_category = max(scores, key=scores.get)
        confidence = scores[best_category]
        
        return best_category, confidence

class ErrorPatternAnalyzer:
    """Analyze error patterns across multiple test failures."""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english') if AI_AVAILABLE else None
        self.error_history = []
    
    def add_error(self, error_data: Dict[str, Any]):
        """Add error to history for pattern analysis."""
        self.error_history.append(error_data)
    
    def find_similar_errors(self, current_error: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find similar errors from history."""
        if not AI_AVAILABLE or not self.error_history:
            return []
        
        try:
            # Extract error messages from history
            historical_errors = [error.get('error_message', '') for error in self.error_history]
            all_errors = historical_errors + [current_error]
            
            # Vectorize errors
            vectors = self.vectorizer.fit_transform(all_errors)
            current_vector = vectors[-1]
            
            # Calculate similarities
            similarities = []
            for i, historical_vector in enumerate(vectors[:-1]):
                similarity = torch.cosine_similarity(
                    torch.tensor(current_vector.toarray()),
                    torch.tensor(historical_vector.toarray()),
                    dim=1
                ).item()
                
                similarities.append({
                    'error': self.error_history[i],
                    'similarity': similarity
                })
            
            # Sort by similarity and return top matches
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            return similarities[:limit]
            
        except Exception as e:
            test_logger.error(f"Error finding similar patterns: {str(e)}")
            return []
    
    def cluster_errors(self, n_clusters: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """Cluster similar errors together."""
        if not AI_AVAILABLE or len(self.error_history) < n_clusters:
            return {}
        
        try:
            error_messages = [error.get('error_message', '') for error in self.error_history]
            vectors = self.vectorizer.fit_transform(error_messages)
            
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = kmeans.fit_predict(vectors)
            
            # Group errors by cluster
            clustered_errors = {}
            for i, cluster_id in enumerate(clusters):
                cluster_key = f"cluster_{cluster_id}"
                if cluster_key not in clustered_errors:
                    clustered_errors[cluster_key] = []
                clustered_errors[cluster_key].append(self.error_history[i])
            
            return clustered_errors
            
        except Exception as e:
            test_logger.error(f"Error clustering failures: {str(e)}")
            return {}

class SuggestionEngine:
    """Generate suggestions for fixing test failures."""
    
    def __init__(self):
        self.suggestions_db = {
            'element_not_found': [
                "Check if the element selector is correct",
                "Verify the element exists on the page",
                "Add explicit wait for element to appear",
                "Check if the element is in an iframe",
                "Verify the page has loaded completely"
            ],
            'timeout': [
                "Increase timeout value",
                "Add explicit waits for specific conditions",
                "Check network connectivity",
                "Verify page load performance",
                "Check for JavaScript errors blocking execution"
            ],
            'assertion_error': [
                "Review test expectations vs actual behavior",
                "Check test data validity",
                "Verify application behavior changes",
                "Update test assertions to match current requirements",
                "Check for timing issues in assertions"
            ],
            'network_error': [
                "Check network connectivity",
                "Verify API endpoints are accessible",
                "Check for firewall or proxy issues",
                "Verify SSL certificates",
                "Check API response format and status codes"
            ],
            'permission_error': [
                "Check user permissions and roles",
                "Verify authentication tokens",
                "Check file system permissions",
                "Verify API access rights",
                "Check browser security settings"
            ],
            'data_error': [
                "Validate test data format",
                "Check data source availability",
                "Verify data schema compatibility",
                "Check for data corruption",
                "Validate input parameters"
            ],
            'environment_error': [
                "Check browser/driver compatibility",
                "Verify environment configuration",
                "Check system resources",
                "Update browser or driver versions",
                "Verify platform-specific settings"
            ],
            'application_error': [
                "Check application logs for errors",
                "Verify application deployment",
                "Check for application bugs",
                "Review recent application changes",
                "Check application performance"
            ]
        }
    
    def get_suggestions(self, category: str, error_context: Dict[str, Any] = None) -> List[str]:
        """Get suggestions for a specific failure category."""
        base_suggestions = self.suggestions_db.get(category, [
            "Review error message and stack trace carefully",
            "Check recent code changes",
            "Verify test environment setup",
            "Check for intermittent issues"
        ])
        
        # Add context-specific suggestions
        contextual_suggestions = []
        if error_context:
            if 'test_name' in error_context:
                contextual_suggestions.append(f"Review test logic in {error_context['test_name']}")
            
            if 'page_url' in error_context:
                contextual_suggestions.append(f"Verify behavior on page: {error_context['page_url']}")
        
        return base_suggestions + contextual_suggestions

class AIFailureAnalyzer:
    """Main AI-powered failure analyzer."""
    
    def __init__(self):
        self.categorizer = FailureCategorizer()
        self.pattern_analyzer = ErrorPatternAnalyzer()
        self.suggestion_engine = SuggestionEngine()
        self.nlp_pipeline = None
        
        if AI_AVAILABLE and settings.ai.enabled:
            try:
                self.nlp_pipeline = pipeline(
                    "text-classification",
                    model=settings.ai.model_name,
                    return_all_scores=True
                )
                test_logger.info("AI analysis initialized successfully")
            except Exception as e:
                test_logger.warning(f"Failed to initialize NLP pipeline: {str(e)}")
    
    def analyze_failure(self, test_result: Dict[str, Any]) -> FailureAnalysis:
        """Perform comprehensive failure analysis."""
        error_message = test_result.get('error_message', '')
        stack_trace = test_result.get('stack_trace', '')
        test_name = test_result.get('test_name', '')
        
        # Categorize failure
        category, confidence = self.categorizer.get_best_category(error_message, stack_trace)
        
        # Extract root cause
        root_cause = self._extract_root_cause(error_message, stack_trace)
        
        # Get suggestions
        suggestions = self.suggestion_engine.get_suggestions(
            category, 
            {'test_name': test_name}
        )
        
        # Find similar failures
        similar_failures = self.pattern_analyzer.find_similar_errors(error_message)
        
        # Analyze patterns
        patterns = self._analyze_patterns(error_message, stack_trace)
        
        # Add to error history for future analysis
        self.pattern_analyzer.add_error(test_result)
        
        analysis = FailureAnalysis(
            category=category,
            confidence=confidence,
            root_cause=root_cause,
            suggestions=suggestions,
            similar_failures=[f['error']['test_name'] for f in similar_failures],
            patterns=patterns
        )
        
        test_logger.ai_analysis({
            'category': category,
            'confidence': confidence,
            'root_cause': root_cause,
            'suggestions_count': len(suggestions)
        })
        
        return analysis
    
    def _extract_root_cause(self, error_message: str, stack_trace: str) -> str:
        """Extract root cause from error information."""
        # Look for common error patterns
        patterns = {
            r'Element.*not found': 'Element locator issue',
            r'Timeout.*waiting': 'Timing/synchronization issue',
            r'AssertionError': 'Test expectation mismatch',
            r'Connection.*refused': 'Network connectivity issue',
            r'Permission.*denied': 'Access permission issue',
            r'Invalid.*format': 'Data format issue',
            r'Driver.*error': 'WebDriver/Appium issue'
        }
        
        combined_text = f"{error_message} {stack_trace}"
        
        for pattern, cause in patterns.items():
            if re.search(pattern, combined_text, re.IGNORECASE):
                return cause
        
        # Extract the most informative line from stack trace
        if stack_trace:
            lines = stack_trace.split('\n')
            for line in lines:
                if 'test_' in line.lower() or 'assert' in line.lower():
                    return f"Issue in: {line.strip()}"
        
        return "Unknown root cause - manual investigation required"
    
    def _analyze_patterns(self, error_message: str, stack_trace: str) -> Dict[str, Any]:
        """Analyze patterns in the error."""
        patterns = {
            'error_length': len(error_message),
            'stack_trace_length': len(stack_trace),
            'contains_xpath': 'xpath' in error_message.lower(),
            'contains_css': 'css' in error_message.lower(),
            'contains_timeout': 'timeout' in error_message.lower(),
            'contains_assertion': 'assert' in error_message.lower(),
            'line_count': len(stack_trace.split('\n')) if stack_trace else 0
        }
        
        return patterns
    
    def generate_report(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive analysis report."""
        if not test_results:
            return {'error': 'No test results provided'}
        
        failed_tests = [t for t in test_results if t.get('status') in ['failed', 'error']]
        
        if not failed_tests:
            return {'message': 'No failed tests to analyze'}
        
        analyses = []
        category_counts = {}
        
        for test_result in failed_tests:
            analysis = self.analyze_failure(test_result)
            analyses.append({
                'test_name': test_result.get('test_name'),
                'analysis': analysis.__dict__
            })
            
            # Count categories
            category = analysis.category
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Cluster similar errors
        error_clusters = self.pattern_analyzer.cluster_errors()
        
        report = {
            'summary': {
                'total_failures': len(failed_tests),
                'categories': category_counts,
                'most_common_category': max(category_counts, key=category_counts.get) if category_counts else None
            },
            'detailed_analyses': analyses,
            'error_clusters': error_clusters,
            'recommendations': self._generate_global_recommendations(category_counts)
        }
        
        return report
    
    def _generate_global_recommendations(self, category_counts: Dict[str, int]) -> List[str]:
        """Generate global recommendations based on failure patterns."""
        recommendations = []
        
        if not category_counts:
            return ["No specific recommendations available"]
        
        most_common = max(category_counts, key=category_counts.get)
        
        if most_common == 'element_not_found':
            recommendations.append("Consider reviewing element locator strategies")
            recommendations.append("Implement more robust waiting mechanisms")
        elif most_common == 'timeout':
            recommendations.append("Review timeout values across test suite")
            recommendations.append("Investigate application performance issues")
        elif most_common == 'assertion_error':
            recommendations.append("Review test expectations and application behavior")
            recommendations.append("Consider updating test assertions")
        
        # Add general recommendations
        recommendations.extend([
            "Implement retry mechanisms for flaky tests",
            "Add more detailed logging for failure diagnosis",
            "Consider parallel execution optimization"
        ])
        
        return recommendations

# Global AI analyzer instance
ai_analyzer = AIFailureAnalyzer() if AI_AVAILABLE else None