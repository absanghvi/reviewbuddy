# AI Code Reviewer - Implementation Complete ✅

## Overview

This is a complete Python-based implementation of an **automatic code review system** that uses agentic AI capabilities to analyze GitHub pull requests and generate structured review observations in JSON format.

### Key Features

✅ **Configurable LLM Support** - Easy switching between OpenAI, Anthropic, or other LLM providers  
✅ **Structured JSON Output** - Reviews are returned as JSON arrays compatible with GitHub API  
✅ **Agentic Code Review** - Uses LLM intelligence for comprehensive code analysis  
✅ **GitHub Integration** - Automatically post reviews to PRs  
✅ **Production Ready** - Full error handling, logging, retry logic, and type hints  

---

## Project Structure

```
review-runner/
├── src/                           # Source code
│   ├── __init__.py
│   ├── llm_client.py              # Abstract base class for LLM providers
│   ├── openai_client.py           # OpenAI implementation
│   ├── anthropic_client.py        # Anthropic Claude implementation
│   ├── llm_factory.py             # Factory for creating LLM clients
│   ├── review_observation.py      # Data models (Severity, Category, Observation, Result)
│   ├── code_review_engine.py      # Core review logic (agentic AI analysis)
│   ├── github_client.py           # GitHub API integration
│   └── main.py                    # Application entry point
├── config/
│   ├── __init__.py
│   └── llm_config.py              # Configuration management
├── tests/
│   ├── __init__.py
│   └── test_code_review.py        # Unit tests with mock LLM
├── samples/
│   └── sample_changes.diff        # Example code diff for testing
├── logs/                          # Auto-created for log files
├── review_results/                # Auto-created for JSON output
├── requirements.txt               # Python dependencies
├── .env.example                   # Template for environment variables
├── .env                           # Your configuration (add your API keys here)
└── README.md                      # This file
```

---

## Installation & Setup

### 1. Prerequisites

- Python 3.8 or later
- GitHub account with personal access token (repo scope)
- API key from LLM provider:
  - **OpenAI**: https://platform.openai.com/api-keys (recommended for POC)
  - **Anthropic**: https://console.anthropic.com/

### 2. Create Virtual Environment

```powershell
cd review-runner
python -m venv venv
.\venv\Scripts\Activate
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure API Keys

Copy `.env.example` to `.env` and fill in your actual credentials:

```powershell
# Option A: Manual copy
Copy-Item .env.example .env

# Option B: VS Code Explorer - Right-click .env.example → Copy → Paste as .env
```

Edit `.env` with your keys:
```env
PROVIDER=openai
OPENAI_API_KEY=sk-your-actual-key-here
OPENAI_MODEL=gpt-4
GITHUB_TOKEN=ghp_your-github-token-here
```

---

## Usage

### Option 1: Command Line (Recommended)

```powershell
python -m src.main `
  --pr-number 42 `
  --repo-name my-repo `
  --repo-owner my-org `
  --code-changes-file samples/sample_changes.diff
```

**With GitHub posting:**
```powershell
python -m src.main `
  --pr-number 42 `
  --repo-name my-repo `
  --repo-owner my-org `
  --code-changes-file samples/sample_changes.diff `
  --post-to-github
```

### Option 2: Python API

```python
from config.llm_config import LLMConfig
from src.llm_factory import LLMFactory
from src.code_review_engine import CodeReviewEngine

# Load config
config = LLMConfig.load_from_env()

# Create LLM client
llm_client = LLMFactory.create_client(config)

# Review code
engine = CodeReviewEngine(llm_client)
result = engine.review_code_changes(
    pr_number=42,
    repo_name="my-repo",
    code_changes=code_diff_string
)

# Access observations
print(result.to_json())  # Get full JSON output
for obs in result.observations:
    print(f"{obs.severity}: {obs.title}")
```

---

## Output Format

### JSON Structure

The tool outputs a JSON array of observations, where each observation is a finding:

```json
{
  "pull_request_number": 42,
  "repository_name": "my-repo",
  "timestamp": "2026-02-28T10:30:45.123456",
  "review_summary": "Found 3 issue(s):\n  🔴 1 Critical\n  🟠 1 High\n  🟡 1 Medium",
  "observations_count": 3,
  "observations": [
    {
      "file_path": "src/database.py",
      "line_number": 45,
      "severity": "critical",
      "category": "security",
      "title": "SQL Injection Vulnerability",
      "description": "User input is directly concatenated into SQL query without parameterization. This allows attackers to inject arbitrary SQL code.",
      "suggestion": "Use parameterized queries or an ORM to prevent SQL injection attacks.",
      "confidence": 0.95,
      "code_snippet": "query = f\"SELECT * FROM users WHERE id = {user_id}\"",
      "timestamp": "2026-02-28T10:30:45.123456"
    },
    {
      "file_path": "src/api.py",
      "line_number": 89,
      "severity": "high",
      "category": "performance",
      "title": "N+1 Query Problem",
      "description": "Loop executes separate database query for each item...",
      "suggestion": "Fetch all related data in a single query using JOIN or batch loading...",
      "confidence": 0.90,
      "timestamp": "2026-02-28T10:30:45.123456"
    }
  ]
}
```

### Severity Levels

- **critical** - Security vulnerabilities, data loss risk, production blockers
- **high** - Major issues affecting functionality or security
- **medium** - Important issues but not blocking
- **low** - Minor improvements or suggestions
- **info** - Informational comments

### Categories

- **security** - Security vulnerabilities, authentication, encryption
- **performance** - Optimization, N+1 queries, inefficient algorithms
- **code_quality** - Complexity, duplication, maintainability
- **best_practice** - Design patterns, SOLID principles
- **documentation** - Missing docstrings, comments
- **testing** - Test coverage, test cases
- **style** - Formatting, naming conventions
- **other** - Miscellaneous findings

---

## Core Components

### 1. **LLM Abstraction** (`llm_client.py`, `llm_factory.py`)

Makes LLM provider configurable. Change `PROVIDER` in `.env` to switch between:
- `openai` - Uses OpenAI's GPT models
- `anthropic` - Uses Anthropic's Claude

Adding new providers is simple - just implement the `LLMClient` interface:

```python
class YourLLMClient(LLMClient):
    def call_llm(self, prompt, system_prompt=None, **kwargs) -> str:
        # Your implementation
        pass
    
    def validate_connection(self) -> bool:
        # Validation logic
        pass
```

Then register it:
```python
LLMFactory.register_provider('your-provider', YourLLMClient)
```

### 2. **Code Review Engine** (`code_review_engine.py`)

The core intelligence that:
- Prepares review prompts with code changes
- Calls the configured LLM
- Parses LLM response into structured observations
- Generates human-readable summaries

The engine uses an **agentic system prompt** that instructs the LLM to:
- Analyze code for security issues
- Identify performance problems
- Check code quality standards
- Verify best practices
- Find missing tests/documentation
- Spot styling issues

### 3. **Observation Models** (`review_observation.py`)

Data classes for:
- **ReviewObservation** - Single finding with file, line, severity, category, description, suggestion
- **ReviewResult** - Container for all observations from a PR review
- **Severity** & **Category** enums for standardized values

### 4. **GitHub Integration** (`github_client.py`)

Posts reviews to GitHub using PyGithub:
- Post review comments on PR
- Post inline comments on specific lines
- Format observations as markdown

### 5. **Configuration** (`config/llm_config.py`)

Loads settings from `.env`:
- Provider selection (OpenAI, Anthropic, etc.)
- API keys for each provider
- Model selections
- Timeout and retry settings
- GitHub token

---

## Testing

### Run Unit Tests

```powershell
python -m pytest tests/test_code_review.py -v
```

Tests include:
- LLM response parsing
- JSON structure validation
- Observation serialization
- Review result generation
- Enum validation

### Test with Sample Code

The project includes `samples/sample_changes.diff` with intentional issues to demonstrate the review engine.

```powershell
python -m src.main `
  --pr-number 1 `
  --repo-name test-repo `
  --repo-owner test-org `
  --code-changes-file samples/sample_changes.diff
```

This will generate `review_results/pr_1.json` with observations.

---

## Configuration Options

### `.env` Variables

```env
# LLM Provider (openai or anthropic)
PROVIDER=openai

# OpenAI Settings
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4              # Model to use
OPENAI_TEMPERATURE=0.3          # Lower = more deterministic
OPENAI_MAX_TOKENS=2000          # Max response length

# Anthropic Settings (optional)
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-opus-20240229
ANTHROPIC_MAX_TOKENS=2000

# GitHub Settings
GITHUB_TOKEN=ghp_...            # Personal access token

# General Settings
TIMEOUT=30                       # API request timeout
MAX_RETRIES=3                    # Retry attempts on failure
```

### Switching Providers

To switch from OpenAI to Anthropic, just change:
```env
PROVIDER=anthropic
ANTHROPIC_API_KEY=your-key
```

No code changes needed!

---

## GitHub Actions Integration (Optional)

Automate reviews on every PR by adding this workflow:

**File:** `.github/workflows/code-review.yml`

```yaml
name: AI Code Review
on:
  pull_request:
    types: [opened, synchronize]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      - uses: actions/setup-python@v4
        with: {python-version: '3.11'}
      - run: pip install -r requirements.txt
      - run: |
          git diff origin/${{ github.base_ref }} > pr.diff
          python -m src.main \
            --pr-number ${{ github.event.pull_request.number }} \
            --repo-name ${{ github.event.repository.name }} \
            --repo-owner ${{ github.repository_owner }} \
            --code-changes-file pr.diff \
            --post-to-github
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

Add secrets to repository settings for `OPENAI_API_KEY` and `GITHUB_TOKEN`.

---

## Key Design Decisions

### 1. **Configurable LLM Provider**
Uses factory pattern to support any LLM provider. Change via environment variable, no code changes needed.

### 2. **Structured JSON Output**
Reviews are returned as JSON arrays, directly compatible with GitHub API. Each observation is a complete finding with all context.

### 3. **Agentic Approach**
Uses a detailed system prompt to guide the LLM to act as an expert code reviewer across multiple dimensions (security, performance, quality, etc.).

### 4. **Type Safety**
Pydantic and dataclasses for validation. Enums for severity/category ensure consistency.

### 5. **Error Handling**
Retry logic for API failures, graceful JSON parsing with fallbacks, comprehensive logging.

### 6. **Extensibility**
Easy to:
- Add new LLM providers
- Customize review prompts
- Extend observation data
- Integrate with other tools

---

## Customization

### Custom Review Prompts

Edit the `SYSTEM_PROMPT` in `src/code_review_engine.py` to customize what the AI looks for:

```python
SYSTEM_PROMPT = """Your custom instructions here...
Focus on:
- Your specific quality standards
- Team conventions
- Project-specific concerns
"""
```

### Filter Observations

```python
# Only critical issues
critical_obs = [o for o in result.observations 
                if o.severity == Severity.CRITICAL]

# Only security issues
security_obs = [o for o in result.observations 
                if o.category == Category.SECURITY]
```

### Custom Severity Weights

Extend `ReviewResult` with methods for your scoring:

```python
def get_severity_score(result):
    """Calculate impact score for observations"""
    weights = {
        Severity.CRITICAL: 10,
        Severity.HIGH: 5,
        Severity.MEDIUM: 2,
        Severity.LOW: 1,
        Severity.INFO: 0
    }
    return sum(weights[o.severity] for o in result.observations)
```

---

## Troubleshooting

### API Key Issues
```
Error: "API key not configured"
→ Check .env file exists and has OPENAI_API_KEY=... (not commented)
```

### JSON Parsing Errors
```
Error: "Failed to parse LLM response as JSON"
→ The LLM returned non-JSON. Check SYSTEM_PROMPT is being followed
→ Reduce OPENAI_MAX_TOKENS or increase timeout
```

### Python Import Errors
```
ModuleNotFoundError: No module named 'openai'
→ Make sure virtual environment is activated
→ Run: pip install -r requirements.txt
```

### GitHub Token Issues
```
Error: "Bad credentials"
→ Create new token at https://github.com/settings/tokens
→ Token needs 'repo' scope
→ Update .env with new token
```

---

## Performance Tips

- **Token Usage**: Lower `OPENAI_MAX_TOKENS` to reduce API costs
- **Temperature**: Use `0.3` for consistent results (set in .env)
- **Batching**: Review multiple files at once in single diff
- **Caching**: Cache API responses for repeated reviews

---

## Security Best Practices

1. **Never commit .env file** (add to .gitignore)
2. **Use GitHub Secrets** for CI/CD workflows
3. **Rotate API keys regularly**
4. **Use least-privileged GitHub token** (repo scope only)
5. **Audit logs** in `logs/review.log` for access patterns

---

## Next Steps

1. ✅ **Setup Complete** - All files created
2. 📝 **Configure** - Add your API keys to `.env`
3. 🧪 **Test** - Run with sample code
4. 🚀 **Deploy** - Set up GitHub Actions
5. ⚙️ **Customize** - Adjust prompts and rules

---

## Dependencies

- **python-dotenv** - Environment variable loading
- **pydantic** - Configuration validation
- **requests** - HTTP requests
- **openai** - OpenAI API client
- **anthropic** - Anthropic API client
- **PyGithub** - GitHub API wrapper
- **tenacity** - Retry logic
- **pytest** - Testing framework

---

## File Sizes & Estimated Complexity

| File | Lines | Purpose |
|------|-------|---------|
| `code_review_engine.py` | 250+ | Core review logic |
| `review_observation.py` | 150+ | Data models |
| `openai_client.py` | 100+ | LLM client |
| `github_client.py` | 180+ | GitHub integration |
| `main.py` | 200+ | CLI & orchestration |
| `llm_config.py` | 120+ | Configuration |
| `test_code_review.py` | 350+ | Comprehensive tests |
| **Total** | **~1,500** | **Production-ready** |

---

## License & Attribution

This implementation follows the tutorial from `tutorials/POC/codereview/TUTORIAL.md` and implements best practices for:
- Agentic AI integration
- Code review automation
- GitHub PR analysis

---

## Support

For issues or questions:
1. Check `.env` configuration
2. Review logs in `logs/review.log`
3. Run tests with `pytest tests/ -v`
4. Verify API key credentials
5. Check GitHub token permissions

---

**Status**: ✅ **Ready for Production Use**

All components are implemented, tested, and documented. Start by configuring your API keys in `.env` and run your first review!
