# Quick Start Guide

## ⚡ Get Running in 5 Minutes

### Step 1: Setup Virtual Environment (1 min)

```powershell
cd review-runner
python -m venv venv
.\venv\Scripts\Activate
```

### Step 2: Install Dependencies (2 min)

```powershell
pip install -r requirements.txt
```

### Step 3: Configure API Keys (1 min)

```powershell
# Create .env from template
Copy-Item .env.example .env
```

Edit `.env` and add your keys:
```env
PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4
```

### Step 4: Test with Sample Code (1 min)

```powershell
python -m src.main `
  --pr-number 1 `
  --repo-name test-repo `
  --repo-owner test-org `
  --code-changes-file samples/sample_changes.diff
```

### Step 5: Check Results

Open: `review_results/pr_1.json`

You'll see observations like:
```json
{
  "file_path": "src/database.py",
  "line_number": 12,
  "severity": "critical",
  "category": "security",
  "title": "SQL Injection Vulnerability",
  ...
}
```

---

## 🎯 Common Tasks

### Review a Real PR

```powershell
# Get the diff
git diff origin/main > my_changes.diff

# Run review
python -m src.main `
  --pr-number 123 `
  --repo-name my-repo `
  --repo-owner my-org `
  --code-changes-file my_changes.diff `
  --post-to-github
```

### Run Tests

```powershell
python -m pytest tests/test_code_review.py -v
```

### View Logs

```powershell
Get-Content logs/review.log -Tail 50
```

### Switch LLM Provider

Edit `.env`:
```env
PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
```

Done! No code changes needed.

---

## 📋 Project Files Summary

| File | Purpose |
|------|---------|
| `src/main.py` | Entry point - run this |
| `src/code_review_engine.py` | AI review logic |
| `src/llm_factory.py` | Create LLM clients |
| `src/github_client.py` | Post to GitHub |
| `config/llm_config.py` | Load settings |
| `tests/test_code_review.py` | Run tests |

---

## 🔧 Configuration

### `.env` Variables (Minimal)

```env
PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
GITHUB_TOKEN=ghp_...
```

### Optional Tweaks

```env
OPENAI_TEMPERATURE=0.3    # Lower = more consistent
OPENAI_MAX_TOKENS=2000    # Max response size
TIMEOUT=30                # Seconds to wait for API
MAX_RETRIES=3             # Retry on failure
```

---

## ❓ FAQ

**Q: How do I get API keys?**
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/
- GitHub: https://github.com/settings/tokens (create with "repo" scope)

**Q: Why is the review slow?**
- API calls take time. First review typically 30-60 seconds.
- Consider caching results for repeated reviews.

**Q: How much does it cost?**
- OpenAI: ~$0.05-0.15 per review (depends on code size)
- Anthropic: Similar pricing
- Set up API spending limits to control costs

**Q: Can I use different LLM providers?**
- Yes! Set `PROVIDER=anthropic` in `.env`
- Easy to add more (see code for details)

**Q: How do I customize what gets reviewed?**
- Edit `SYSTEM_PROMPT` in `src/code_review_engine.py`
- Tell the AI what you care about

**Q: Can I automate this on GitHub?**
- Yes! See `.github/workflows/code-review.yml` in the main README

---

## 🚀 Next Steps

1. Get API keys
2. Run quick test above
3. Review output JSON
4. Customize as needed
5. Deploy to GitHub Actions

---

## 📚 Learn More

- Full README: `README.md`
- Implementation Tutorial: `TUTORIAL.md`
- JSON Format Spec: `JSON_FORMAT_REFERENCE.md`
- Implementation Checklist: `IMPLEMENTATION_CHECKLIST.md`

---

**Ready?** `python -m src.main --help` to see all options!
