# AI Code Reviewer — Getting Started

This file consolidates the essential project information and quick-start instructions.

Step-by-step testing process-

Markdown
# 🛠️ Project Setup & Maintenance Guide: Review-Runner

---

## 1. 🧹 The "Clean Slate" Phase
```bash
cd C:\Home\Workspaces\github\reviewbuddy\review-runner

2. 🏗️ The Sandbox Phase (Virtual Environment)
Bash
python -m venv venv
venv\Scripts\activate
3. 📦 The Installation Phase
Bash
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pydantic-settings
4. 🔑 The Configuration Phase (.env)
Bash
# notepad .env
PROVIDER=openai
OPENAI_API_KEY=ghp_YOUR_TOKEN_HERE
OPENAI_BASE_URL=[https://models.inference.ai.azure.com](https://models.inference.ai.azure.com)
OPENAI_MODEL=gpt-4o
GITHUB_TOKEN=ghp_YOUR_TOKEN_HERE
5. ✅ The Testing Phase (Pytest)
Bash
pytest tests/ -v
6. 🚀 Execution Phase
Bash
python main.py
7. 🔄 Daily Workflow Summary
Task	Command
Start	venv\Scripts\activate
Test	pytest tests/ -v
Run	python main.py
Stop	deactivate




### Old
Overview
- Small, configurable Python tool that analyzes GitHub PR diffs using an LLM and returns structured JSON observations suitable for posting to GitHub.

Prerequisites
- Python 3.8+
- A GitHub personal access token with `repo` scope
- An API key for your LLM provider (OpenAI or Anthropic)

Quick setup
```powershell
cd review-runner
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt
```

Configure
```powershell
Copy-Item .env.example .env
# Edit .env and add your API keys
```

Windows (cmd) — Python 3.12 (Option B)
From the repository root run these commands in `cmd.exe`:
```bat
cd C:\Home\Workspaces\github\reviewbuddy
py -3.12 -m venv review-runner\.venv
review-runner\.venv\Scripts\activate.bat
python -m pip install --upgrade pip setuptools wheel
python -m pip install --prefer-binary pydantic-core
pip install -r review-runner\requirements.txt
python -m pytest review-runner\tests -q
deactivate
```

Notes
- If `py -3.12` is not available use `py -3` or install Python 3.12.
- If `pydantic-core` falls back to source build and fails, install Rust or use Python 3.11.

Minimal `.env` (example)
```env
PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
GITHUB_TOKEN=ghp_...
```

Run a local review (sample)
```powershell
python -m src.main \
  --pr-number 1 \
  --repo-name test-repo \
  --repo-owner test-org \
  --code-changes-file samples/sample_changes.diff
```

Run and post to GitHub
```powershell
python -m src.main \
  --pr-number 1 \
  --repo-name test-repo \
  --repo-owner test-org \
  --code-changes-file samples/sample_changes.diff \
  --post-to-github
```

Core modules (brief)
- `src/main.py` — CLI entrypoint and orchestration
- `src/code_review_engine.py` — Prepares prompts, calls LLM, parses JSON into observations
- `src/review_observation.py` — Data models (Severity, Category, ReviewObservation, ReviewResult)
- `src/llm_factory.py` — Creates LLM client based on `PROVIDER`
- `src/openai_client.py` / `src/anthropic_client.py` — Provider implementations
- `src/github_client.py` — Posts reviews via GitHub API
- `config/llm_config.py` — Pydantic-based configuration loader

Testing
- Unit tests use a `MockLLMClient` so tests run without API calls.
- Run tests:
```powershell
pytest -q
```

Support / common issues
- "API key not configured" — ensure `.env` exists and `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` is set
- "Module not found" — activate venv and run `pip install -r requirements.txt`
- "JSON parsing error" — verify the LLM returns valid JSON; increase `OPENAI_MAX_TOKENS` if truncated
- GitHub posting fails — confirm `GITHUB_TOKEN` has `repo` scope

Security
- Keep API keys in `.env` and out of source control (`.gitignore` contains `.env`)
- Use minimal GitHub token scopes

Next steps
- Get API keys and configure `.env`
- Run sample review
- Customize `SYSTEM_PROMPT` in `src/code_review_engine.py` to match your team standards
- Optionally add a GitHub Actions workflow to run reviews on PRs

Where to find more
- Full README: `README.md`
- Design and implementation notes: `docs/backup/IMPLEMENTATION_SUMMARY.md`

---

Changes
- Merged content from `START_HERE.md` into this file and removed redundant sections.
