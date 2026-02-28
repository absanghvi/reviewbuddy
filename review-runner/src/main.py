"""
Main Application Entry Point

This module orchestrates the entire code review workflow:
1. Loads configuration
2. Creates LLM client
3. Performs code review
4. Saves results as JSON
5. Optionally posts to GitHub
"""

import sys
import json
import logging
import argparse
from pathlib import Path

from config.llm_config import LLMConfig
from src.llm_factory import LLMFactory
from src.code_review_engine import CodeReviewEngine
from src.github_client import GitHubClient


# Configure logging
def setup_logger():
    """Setup logging directory and configuration"""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'review.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


logger = None


def load_code_changes(filepath: str) -> str:
    """
    Load code changes from file.
    
    Args:
        filepath: Path to file containing code diff/changes
    
    Returns:
        Content of the file as string
    
    Raises:
        FileNotFoundError: If file not found
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            logger.info(f"Loaded {len(content)} bytes of code changes from {filepath}")
            return content
    except FileNotFoundError:
        logger.error(f"Code changes file not found: {filepath}")
        raise


def save_review_result(result, output_path: str = None) -> str:
    """
    Save review result to JSON file.
    
    The JSON structure is designed to be compatible with GitHub API
    and contains all observations in a format that can be posted.
    
    Args:
        result: ReviewResult object to save
        output_path: Optional custom output path
    
    Returns:
        Path where result was saved
    """
    if output_path is None:
        output_path = f"review_results/pr_{result.pull_request_number}.json"
    
    # Create directory if needed
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(result.to_json())
    
    logger.info(f"Review result saved to {output_path}")
    return output_path


def perform_code_review(
    pr_number: int,
    repo_name: str,
    repo_owner: str,
    code_changes_file: str,
    output_file: str = None,
    post_to_github: bool = False
) -> dict:
    """
    Perform code review and optionally post to GitHub.
    
    This is the main workflow function that:
    1. Loads LLM configuration
    2. Creates appropriate LLM client based on provider
    3. Analyzes code changes using CodeReviewEngine
    4. Saves results as JSON array of observations
    5. Optionally posts results to GitHub
    
    Args:
        pr_number: Pull request number
        repo_name: Repository name
        repo_owner: Repository owner/organization
        code_changes_file: Path to file with code changes/diff
        output_file: Optional custom output file path
        post_to_github: Whether to post review to GitHub
    
    Returns:
        Dictionary with review result status and data
    """
    logger.info(f"Starting code review for PR #{pr_number} in {repo_owner}/{repo_name}")
    
    try:
        # Load configuration from environment
        config = LLMConfig.load_from_env()
        logger.info(f"Loaded configuration for provider: {config.provider}")
        
        # Create LLM client using factory pattern (supports OpenAI, Anthropic, etc.)
        llm_client = LLMFactory.create_client(config)
        logger.info("LLM client created successfully")
        
        # Validate connection
        if not llm_client.validate_connection():
            logger.warning("LLM connection validation failed, proceeding anyway")
        
        # Create review engine
        review_engine = CodeReviewEngine(llm_client)
        
        # Load code changes to review
        code_changes = load_code_changes(code_changes_file)
        
        # Perform the code review using agentic LLM
        logger.info("Performing code review...")
        review_result = review_engine.review_code_changes(
            pr_number=pr_number,
            repo_name=repo_name,
            code_changes=code_changes
        )
        
        logger.info(
            f"Code review completed. Found {len(review_result.observations)} issue(s)"
        )
        logger.info(f"Summary: {review_result.review_summary}")
        
        # Save result as JSON (this is the observations array)
        result_file = save_review_result(review_result, output_file)
        
        # Post to GitHub if requested
        if post_to_github:
            logger.info("Posting review to GitHub...")
            github_client = GitHubClient(config.github_token)
            
            review_id = github_client.post_review(
                repo_owner=repo_owner,
                repo_name=repo_name,
                pr_number=pr_number,
                review_result=review_result
            )
            
            logger.info(f"Review posted to GitHub. Review ID: {review_id}")
        
        # Return result in JSON-serializable format
        return {
            "success": True,
            "pr_number": pr_number,
            "repository": f"{repo_owner}/{repo_name}",
            "observations_count": len(review_result.observations),
            "result_file": result_file,
            "review_summary": review_result.review_summary,
            "observations": [obs.to_dict() for obs in review_result.observations]
        }
    
    except Exception as e:
        logger.error(f"Error during code review: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


def main():
    """
    Main entry point with command-line argument parsing.
    
    Accepts arguments for:
    - PR number and repository info
    - Code changes file path
    - Optional output file path
    - Optional GitHub posting
    """
    parser = argparse.ArgumentParser(
        description="AI-powered code review tool for GitHub PRs"
    )
    parser.add_argument(
        "--pr-number",
        type=int,
        required=True,
        help="Pull request number"
    )
    parser.add_argument(
        "--repo-name",
        required=True,
        help="Repository name"
    )
    parser.add_argument(
        "--repo-owner",
        required=True,
        help="Repository owner/organization"
    )
    parser.add_argument(
        "--code-changes-file",
        required=True,
        help="Path to file containing code changes/diff"
    )
    parser.add_argument(
        "--output-file",
        help="Optional path for JSON output file"
    )
    parser.add_argument(
        "--post-to-github",
        action="store_true",
        help="Post review results to GitHub"
    )
    
    args = parser.parse_args()
    
    # Perform review
    result = perform_code_review(
        pr_number=args.pr_number,
        repo_name=args.repo_name,
        repo_owner=args.repo_owner,
        code_changes_file=args.code_changes_file,
        output_file=args.output_file,
        post_to_github=args.post_to_github
    )
    
    # Print result
    print(json.dumps(result, indent=2))
    
    # Return exit code based on success
    return 0 if result['success'] else 1


if __name__ == "__main__":
    logger = setup_logger()
    sys.exit(main())
