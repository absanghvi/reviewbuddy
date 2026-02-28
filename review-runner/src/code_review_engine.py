"""
AI-Powered Code Review Engine

This module implements the core code review logic using an agentic LLM
to analyze code changes and generate structured observations in JSON format.
"""

import json
from typing import Optional, List
import re
from src.llm_client import LLMClient
from src.review_observation import (
    ReviewObservation,
    ReviewResult,
    Severity,
    Category
)


class CodeReviewEngine:
    """
    Agentic code review engine that analyzes code changes
    and generates structured observations in JSON format.
    
    The engine uses an LLM to analyze code diffs and identify issues across
    security, performance, code quality, best practices, and more.
    Results are returned as a JSON array that can be posted to GitHub.
    """
    
    # System prompt for the review agent
    SYSTEM_PROMPT = """You are an expert code reviewer with deep knowledge of software engineering best practices, security, performance, and code quality.

Your task is to analyze code changes and identify issues or improvements.

When analyzing code, consider:
1. **Security**: SQL injection, XSS, authentication/authorization issues, hardcoded secrets, unsafe operations
2. **Performance**: N+1 queries, inefficient algorithms, memory leaks, unnecessary operations
3. **Code Quality**: Dead code, complexity, code duplication, poor naming, maintainability
4. **Best Practices**: Design patterns, SOLID principles, error handling, resource management
5. **Documentation**: Missing docstrings, unclear comments, undocumented APIs
6. **Testing**: Missing test coverage, inadequate test cases, untested edge cases
7. **Style**: Formatting, naming conventions, consistency with codebase

IMPORTANT: Respond ONLY with a valid JSON array. Do not include any text before or after the JSON.

Each element must be an object with exactly these fields:
- file_path: string (relative path to the file)
- line_number: integer (line number in the file)
- severity: string (one of: critical|high|medium|low|info)
- category: string (one of: security|performance|code_quality|best_practice|documentation|testing|style|other)
- title: string (short issue title, 3-10 words)
- description: string (detailed explanation, 1-3 sentences)
- suggestion: string (how to fix it, 1-3 sentences)
- confidence: number (confidence level between 0.0 and 1.0)
- code_snippet: string or null (optional code snippet showing the issue)

Example response format:
[
    {
        "file_path": "src/auth.py",
        "line_number": 45,
        "severity": "critical",
        "category": "security",
        "title": "SQL Injection Vulnerability",
        "description": "User input is directly concatenated into SQL query without parameterization. This allows attackers to inject arbitrary SQL code.",
        "suggestion": "Use parameterized queries or an ORM to prevent SQL injection attacks.",
        "confidence": 0.95,
        "code_snippet": "query = f\\"SELECT * FROM users WHERE id = {user_id}\\"" 
    }
]

If no issues found, return an empty array: []
"""
    
    def __init__(self, llm_client: LLMClient):
        """
        Initialize the code review engine.
        
        Args:
            llm_client: Configured LLM client instance (OpenAI, Anthropic, etc.)
        """
        self.llm_client = llm_client
    
    def review_code_changes(
        self,
        pr_number: int,
        repo_name: str,
        code_changes: str,
        files_changed: Optional[List[str]] = None
    ) -> ReviewResult:
        """
        Review code changes from a pull request.
        
        This method takes code changes (usually a diff) and uses the LLM
        to analyze them, returning a structured ReviewResult with observations.
        The result is in JSON format suitable for posting to GitHub.
        
        Args:
            pr_number: Pull request number
            repo_name: Repository name
            code_changes: The diff/code changes to review (as string)
            files_changed: Optional list of files affected
        
        Returns:
            ReviewResult with observations array ready for JSON serialization
        """
        # Prepare the prompt
        prompt = self._prepare_review_prompt(
            code_changes,
            files_changed
        )
        
        # Call the LLM
        try:
            response = self.llm_client.call_llm(
                prompt=prompt,
                system_prompt=self.SYSTEM_PROMPT
            )
            
            # Parse the response
            observations = self._parse_observations(response)
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse LLM response as JSON: {e}")
            print(f"Raw response: {response[:200] if len(response) > 200 else response}")
            observations = []
        except Exception as e:
            print(f"Error during code review: {e}")
            observations = []
        
        # Create result
        result = ReviewResult(
            pull_request_number=pr_number,
            repository_name=repo_name,
            observations=observations
        )
        
        # Generate summary
        result.review_summary = self._generate_summary(observations)
        
        return result
    
    def _prepare_review_prompt(
        self,
        code_changes: str,
        files_changed: Optional[List[str]] = None
    ) -> str:
        """
        Prepare the prompt for code review.
        
        Args:
            code_changes: Code diff or changes to review
            files_changed: List of file paths affected
        
        Returns:
            Formatted prompt for the LLM
        """
        prompt = "Please review the following code changes for potential issues:\n\n"
        
        if files_changed:
            prompt += f"Files changed: {', '.join(files_changed)}\n\n"
        
        prompt += "Code changes (diff/code):\n"
        prompt += "```\n"
        prompt += code_changes
        prompt += "\n```\n\n"
        prompt += "Provide your analysis as a JSON array of observations. Return ONLY the JSON array, no other text."
        
        return prompt
    
    def _parse_observations(self, response: str) -> List[ReviewObservation]:
        """
        Parse LLM response into ReviewObservation objects.
        
        Extracts JSON array from response and converts each element
        to a ReviewObservation object with proper validation.
        
        Args:
            response: JSON string from LLM
        
        Returns:
            List of ReviewObservation objects
        """
        # Extract JSON array from response (in case there's extra text)
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if not json_match:
            print("No JSON array found in response")
            return []
        
        json_str = json_match.group(0)
        data = json.loads(json_str)
        
        observations = []
        for item in data:
            try:
                observation = ReviewObservation(
                    file_path=item.get('file_path', 'unknown'),
                    line_number=int(item.get('line_number', 0)),
                    severity=Severity(item.get('severity', 'info')),
                    category=Category(item.get('category', 'other')),
                    title=item.get('title', 'Issue'),
                    description=item.get('description', ''),
                    suggestion=item.get('suggestion', ''),
                    confidence=float(item.get('confidence', 0.8)),
                    code_snippet=item.get('code_snippet')
                )
                observations.append(observation)
            except (KeyError, ValueError, TypeError) as e:
                print(f"Error parsing observation: {e}")
                continue
        
        return observations
    
    def _generate_summary(self, observations: List[ReviewObservation]) -> str:
        """
        Generate a human-readable summary of the review.
        
        Args:
            observations: List of observations from review
        
        Returns:
            Formatted summary string
        """
        if not observations:
            return "✅ No issues found - code looks good!"
        
        # Count by severity
        critical = len([o for o in observations if o.severity == Severity.CRITICAL])
        high = len([o for o in observations if o.severity == Severity.HIGH])
        medium = len([o for o in observations if o.severity == Severity.MEDIUM])
        low = len([o for o in observations if o.severity == Severity.LOW])
        info = len([o for o in observations if o.severity == Severity.INFO])
        
        summary_parts = [f"Found {len(observations)} issue(s):"]
        
        if critical > 0:
            summary_parts.append(f"  🔴 {critical} Critical")
        if high > 0:
            summary_parts.append(f"  🟠 {high} High")
        if medium > 0:
            summary_parts.append(f"  🟡 {medium} Medium")
        if low > 0:
            summary_parts.append(f"  🔵 {low} Low")
        if info > 0:
            summary_parts.append(f"  ℹ️ {info} Info")
        
        return "\n".join(summary_parts)
