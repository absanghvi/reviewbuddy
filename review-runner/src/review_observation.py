"""
Code Review Observation Models

This module defines the data structures for code review observations
and results, including enums for severity levels and issue categories.
These are serialized to JSON for GitHub API integration.
"""

from typing import Optional, List
from dataclasses import dataclass, field, asdict
from enum import Enum
import json
from datetime import datetime


class Severity(str, Enum):
    """Severity levels for code review findings"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Category(str, Enum):
    """Categories for code review observations"""
    SECURITY = "security"
    PERFORMANCE = "performance"
    CODE_QUALITY = "code_quality"
    BEST_PRACTICE = "best_practice"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    STYLE = "style"
    OTHER = "other"


@dataclass
class ReviewObservation:
    """
    Represents a single code review observation.
    
    This is a structured finding from the AI code review that can be
    converted to JSON and posted to GitHub as a review comment.
    
    Attributes:
        file_path: Relative path to the file being reviewed
        line_number: Line number where issue occurs (1-indexed)
        severity: Severity level of the issue
        category: Category/type of the issue
        title: Short title of the observation (3-10 words)
        description: Detailed explanation of why this is an issue
        suggestion: Recommended fix or improvement
        confidence: Confidence level 0.0-1.0 that this is a real issue
        code_snippet: Optional code snippet showing the issue
        timestamp: ISO 8601 timestamp of when review was performed
    """
    file_path: str
    line_number: int
    severity: Severity
    category: Category
    title: str
    description: str
    suggestion: str
    confidence: float = 0.8
    code_snippet: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> dict:
        """Convert observation to dictionary"""
        data = asdict(self)
        # Convert enums to strings
        data['severity'] = self.severity.value
        data['category'] = self.category.value
        return data
    
    def to_json(self) -> str:
        """Convert observation to JSON string"""
        data = self.to_dict()
        return json.dumps(data, indent=2)


@dataclass
class ReviewResult:
    """
    Container for all review observations from a single PR.
    
    This object holds the complete review result including all observations,
    metadata, and a summary. It can be serialized to JSON for storage and
    GitHub API integration.
    
    Attributes:
        pull_request_number: GitHub PR number
        repository_name: Name of the repository
        observations: List of ReviewObservation objects found
        review_summary: Human-readable summary of findings
        timestamp: When the review was performed
    """
    
    pull_request_number: int
    repository_name: str
    observations: List[ReviewObservation] = field(default_factory=list)
    review_summary: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def add_observation(self, observation: ReviewObservation):
        """Add an observation to the result"""
        self.observations.append(observation)
    
    def to_dict(self) -> dict:
        """Convert result to dictionary"""
        return {
            "pull_request_number": self.pull_request_number,
            "repository_name": self.repository_name,
            "timestamp": self.timestamp,
            "review_summary": self.review_summary,
            "observations_count": len(self.observations),
            "observations": [obs.to_dict() for obs in self.observations]
        }
    
    def to_json(self) -> str:
        """Convert result to JSON string with pretty printing"""
        return json.dumps(self.to_dict(), indent=2)
    
    def get_observations_by_severity(self, severity: Severity) -> List[ReviewObservation]:
        """Get all observations of a specific severity"""
        return [obs for obs in self.observations if obs.severity == severity]
    
    def get_critical_count(self) -> int:
        """Get count of critical severity observations"""
        return len(self.get_observations_by_severity(Severity.CRITICAL))
    
    def get_high_count(self) -> int:
        """Get count of high severity observations"""
        return len(self.get_observations_by_severity(Severity.HIGH))
    
    def get_medium_count(self) -> int:
        """Get count of medium severity observations"""
        return len(self.get_observations_by_severity(Severity.MEDIUM))
    
    def has_critical_issues(self) -> bool:
        """Check if there are any critical severity issues"""
        return self.get_critical_count() > 0
