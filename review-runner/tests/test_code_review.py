"""
Unit Tests for Code Review Engine

Tests the core functionality of the code review system including:
- LLM response parsing
- JSON observation structure
- Review result generation
"""

import pytest
import json
from pathlib import Path
from src.code_review_engine import CodeReviewEngine
from src.review_observation import (
    ReviewObservation,
    ReviewResult,
    Severity,
    Category
)
from config.llm_config import LLMConfig
from src.llm_factory import LLMFactory


class MockLLMClient:
    """
    Mock LLM client for testing without actual API calls.
    Returns predefined observations in JSON format.
    """
    
    def __init__(self, config):
        self.config = config
    
    def call_llm(self, prompt, system_prompt=None, **kwargs):
        """Return mock review response with predefined observations"""
        return json.dumps([
            {
                "file_path": "src/database.py",
                "line_number": 12,
                "severity": "critical",
                "category": "security",
                "title": "SQL Injection Vulnerability",
                "description": "User input is directly concatenated into SQL query without parameterization. This allows attackers to inject arbitrary SQL commands.",
                "suggestion": "Use parameterized queries or an ORM like SQLAlchemy to prevent SQL injection attacks.",
                "confidence": 0.95,
                "code_snippet": 'query = "SELECT * FROM users WHERE id = " + str(user_id)'
            },
            {
                "file_path": "src/database.py",
                "line_number": 32,
                "severity": "high",
                "category": "performance",
                "title": "N+1 Query Problem",
                "description": "Executing separate database queries in a loop for each record. This causes N+1 queries which severely impacts performance.",
                "suggestion": "Use batch operations or JOIN queries to fetch all related data in a single query.",
                "confidence": 0.90
            },
            {
                "file_path": "src/database.py",
                "line_number": 38,
                "severity": "critical",
                "category": "security",
                "title": "Hardcoded API Secret",
                "description": "Sensitive API secret is hardcoded directly in source code. This is a major security risk if repository is exposed.",
                "suggestion": "Move API key to environment variables or a secure secrets management system. Use: api_key = os.getenv('PAYMENT_API_KEY')",
                "confidence": 1.0
            },
            {
                "file_path": "src/database.py",
                "line_number": 23,
                "severity": "medium",
                "category": "code_quality",
                "title": "Missing Error Handling",
                "description": "Function does not handle potential database errors or validate input parameters.",
                "suggestion": "Add try-except blocks and input validation to handle edge cases properly.",
                "confidence": 0.75
            }
        ])
    
    def validate_connection(self):
        """Mock connection validation"""
        return True


class TestCodeReviewEngine:
    """Test cases for CodeReviewEngine"""
    
    def test_review_engine_parses_observations(self):
        """Test that review engine correctly parses LLM observations"""
        # Create mock client
        mock_client = MockLLMClient(None)
        
        # Create review engine
        engine = CodeReviewEngine(mock_client)
        
        # Perform review
        result = engine.review_code_changes(
            pr_number=1,
            repo_name="test-repo",
            code_changes="sample code changes"
        )
        
        # Assertions
        assert len(result.observations) == 4
        assert result.observations[0].severity == Severity.CRITICAL
        assert result.observations[1].severity == Severity.HIGH
        assert "SQL Injection" in result.observations[0].title
        assert "N+1" in result.observations[1].title
        assert result.observations[2].severity == Severity.CRITICAL
        assert "Hardcoded" in result.observations[2].title
    
    def test_observation_to_dict(self):
        """Test observation serialization to dictionary"""
        obs = ReviewObservation(
            file_path="src/app.py",
            line_number=42,
            severity=Severity.HIGH,
            category=Category.SECURITY,
            title="Potential XSS Vulnerability",
            description="User input is not escaped before rendering",
            suggestion="Use template escaping or sanitization",
            confidence=0.85
        )
        
        obs_dict = obs.to_dict()
        
        assert obs_dict['file_path'] == "src/app.py"
        assert obs_dict['line_number'] == 42
        assert obs_dict['severity'] == "high"
        assert obs_dict['category'] == "security"
        assert obs_dict['confidence'] == 0.85
    
    def test_observation_to_json(self):
        """Test observation serialization to JSON string"""
        obs = ReviewObservation(
            file_path="src/utils.py",
            line_number=15,
            severity=Severity.LOW,
            category=Category.STYLE,
            title="Naming Convention",
            description="Variable name does not follow convention",
            suggestion="Use camelCase for variables"
        )
        
        json_str = obs.to_json()
        parsed = json.loads(json_str)
        
        assert parsed['file_path'] == "src/utils.py"
        assert parsed['line_number'] == 15
        assert parsed['severity'] == "low"
        assert parsed['category'] == "style"
    
    def test_review_result_structure(self):
        """Test ReviewResult JSON structure for GitHub API compatibility"""
        result = ReviewResult(
            pull_request_number=123,
            repository_name="my-repo"
        )
        
        # Add some observations
        result.add_observation(ReviewObservation(
            file_path="src/main.py",
            line_number=50,
            severity=Severity.HIGH,
            category=Category.PERFORMANCE,
            title="Inefficient Loop",
            description="Loop contains repeated calculations",
            suggestion="Move calculation outside loop",
            confidence=0.9
        ))
        
        # Generate summary
        result.review_summary = "Found 1 issue(s):\n  🟠 1 High"
        
        # Convert to JSON
        json_str = result.to_json()
        data = json.loads(json_str)
        
        # Verify structure
        assert data['pull_request_number'] == 123
        assert data['repository_name'] == "my-repo"
        assert data['observations_count'] == 1
        assert len(data['observations']) == 1
        assert 'timestamp' in data
        assert 'review_summary' in data
    
    def test_review_result_severity_counts(self):
        """Test ReviewResult methods for counting observations by severity"""
        result = ReviewResult(
            pull_request_number=1,
            repository_name="test"
        )
        
        # Add observations of different severities
        result.add_observation(ReviewObservation(
            file_path="test.py", line_number=1,
            severity=Severity.CRITICAL, category=Category.SECURITY,
            title="Critical", description="Test", suggestion="Fix"
        ))
        result.add_observation(ReviewObservation(
            file_path="test.py", line_number=2,
            severity=Severity.HIGH, category=Category.PERFORMANCE,
            title="High", description="Test", suggestion="Fix"
        ))
        result.add_observation(ReviewObservation(
            file_path="test.py", line_number=3,
            severity=Severity.MEDIUM, category=Category.CODE_QUALITY,
            title="Medium", description="Test", suggestion="Fix"
        ))
        
        # Test counting methods
        assert result.get_critical_count() == 1
        assert result.get_high_count() == 1
        assert result.get_medium_count() == 1
        assert result.has_critical_issues() == True
    
    def test_empty_review_result(self):
        """Test ReviewResult with no observations"""
        result = ReviewResult(
            pull_request_number=50,
            repository_name="clean-code"
        )
        
        assert len(result.observations) == 0
        assert result.get_critical_count() == 0
        assert result.has_critical_issues() == False
        
        json_data = json.loads(result.to_json())
        assert json_data['observations_count'] == 0


class TestObservationEnums:
    """Test cases for Severity and Category enums"""
    
    def test_severity_enum_values(self):
        """Test Severity enum contains expected values"""
        severities = [s.value for s in Severity]
        assert "critical" in severities
        assert "high" in severities
        assert "medium" in severities
        assert "low" in severities
        assert "info" in severities
    
    def test_category_enum_values(self):
        """Test Category enum contains expected values"""
        categories = [c.value for c in Category]
        assert "security" in categories
        assert "performance" in categories
        assert "code_quality" in categories
        assert "best_practice" in categories
        assert "documentation" in categories
        assert "testing" in categories
        assert "style" in categories
        assert "other" in categories


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
