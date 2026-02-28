*** End Patch
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

1.  **Setup Complete** - All files created
2.  **Configure** - Add your API keys to `.env`
3.  **Test** - Run with sample code
4.  **Deploy** - Set up GitHub Actions
5.  **Customize** - Adjust prompts and rules

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



## Support

For issues or questions:
1. Check `.env` configuration
2. Review logs in `logs/review.log`
3. Run tests with `pytest tests/ -v`
4. Verify API key credentials
5. Check GitHub token permissions

---

**Status**:  **Ready for Production Use**

All components are implemented, tested, and documented. Start by configuring your API keys in `.env` and run your first review!
