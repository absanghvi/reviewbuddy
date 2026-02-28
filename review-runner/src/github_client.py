"""
GitHub Integration Client

This module provides functionality to interact with GitHub API,
including fetching PR information and posting review comments.
"""

from typing import Optional, List
from github import Github
from github.Repository import Repository
from github.PullRequest import PullRequest
from github.GithubException import GithubException
from src.review_observation import ReviewResult, ReviewObservation


class GitHubClient:
    """Client for interacting with GitHub API"""
    
    def __init__(self, github_token: str):
        """
        Initialize GitHub client.
        
        Args:
            github_token: GitHub personal access token with 'repo' scope
        """
        self.github = Github(github_token)
    
    def get_pull_request(
        self,
        repo_owner: str,
        repo_name: str,
        pr_number: int
    ) -> PullRequest:
        """
        Get a pull request object.
        
        Args:
            repo_owner: Repository owner/organization
            repo_name: Repository name
            pr_number: Pull request number
        
        Returns:
            PullRequest object from PyGithub
        
        Raises:
            GithubException: If PR not found or access denied
        """
        try:
            repo = self.github.get_user(repo_owner).get_repo(repo_name)
            pr = repo.get_pull(pr_number)
            return pr
        except GithubException as e:
            print(f"Error fetching PR: {e}")
            raise
    
    def get_changed_files(
        self,
        repo_owner: str,
        repo_name: str,
        pr_number: int
    ) -> List[str]:
        """
        Get list of files changed in PR.
        
        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            pr_number: Pull request number
        
        Returns:
            List of file paths that were modified/added/deleted
        """
        try:
            pr = self.get_pull_request(repo_owner, repo_name, pr_number)
            files = pr.get_files()
            return [f.filename for f in files]
        except GithubException as e:
            print(f"Error fetching changed files: {e}")
            raise
    
    def post_review(
        self,
        repo_owner: str,
        repo_name: str,
        pr_number: int,
        review_result: ReviewResult,
        event: str = "COMMENT"
    ) -> str:
        """
        Post code review comments on a PR.
        
        Takes the ReviewResult JSON and posts it to GitHub as a review comment.
        This makes the observations visible to all PR reviewers.
        
        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            pr_number: Pull request number
            review_result: ReviewResult object with observations
            event: GitHub review event (APPROVE, REQUEST_CHANGES, COMMENT)
        
        Returns:
            Review ID if successful
        
        Raises:
            GithubException: If posting fails
        """
        try:
            pr = self.get_pull_request(repo_owner, repo_name, pr_number)
            
            # Prepare review body with observations
            review_body = review_result.review_summary + "\n\n"
            review_body += "### Detailed Observations\n\n"
            
            if review_result.observations:
                comments = []
                for obs in review_result.observations:
                    comment = self._format_observation_as_comment(obs)
                    comments.append(comment)
                review_body += "\n\n".join(comments)
            else:
                review_body += "No observations found in this review."
            
            # Post review to GitHub
            review = pr.create_review(
                body=review_body,
                event=event
            )
            
            return str(review.id)
        
        except GithubException as e:
            print(f"Error posting review: {e}")
            raise
    
    def post_inline_comments(
        self,
        repo_owner: str,
        repo_name: str,
        pr_number: int,
        review_result: ReviewResult
    ):
        """
        Post inline comments on specific lines of changed files.
        
        This posts observations as comments directly on the affected lines,
        making them visible in the code context.
        
        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            pr_number: Pull request number
            review_result: ReviewResult with observations
        
        Raises:
            GithubException: If posting fails
        """
        try:
            pr = self.get_pull_request(repo_owner, repo_name, pr_number)
            commits = pr.get_commits()
            
            if commits.totalCount == 0:
                print("No commits found in PR")
                return
            
            last_commit = commits[commits.totalCount - 1]
            
            for obs in review_result.observations:
                comment_body = f"**[{obs.severity.upper()}]** {obs.title}\n\n"
                comment_body += f"{obs.description}\n\n"
                comment_body += f"**Suggestion:** {obs.suggestion}"
                
                try:
                    pr.create_review_comment(
                        body=comment_body,
                        commit=last_commit.commit,
                        path=obs.file_path,
                        line=obs.line_number
                    )
                except Exception as e:
                    print(f"Error posting inline comment for {obs.file_path}:{obs.line_number}: {e}")
        
        except GithubException as e:
            print(f"Error posting inline comments: {e}")
            raise
    
    def _format_observation_as_comment(self, obs: ReviewObservation) -> str:
        """
        Format a single observation as a markdown comment for GitHub.
        
        Args:
            obs: ReviewObservation to format
        
        Returns:
            Formatted markdown string
        """
        comment = f"#### {obs.severity.upper()}: {obs.title}\n\n"
        comment += f"**File:** `{obs.file_path}` (Line {obs.line_number})\n\n"
        comment += f"**Category:** `{obs.category.value}`\n\n"
        comment += f"**Description:**\n{obs.description}\n\n"
        comment += f"**Suggestion:**\n{obs.suggestion}\n\n"
        comment += f"**Confidence:** {obs.confidence:.0%}"
        
        if obs.code_snippet:
            comment += f"\n\n**Code:**\n```\n{obs.code_snippet}\n```"
        
        return comment
