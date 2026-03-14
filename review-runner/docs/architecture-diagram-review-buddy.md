// ...existing code...
# Review Buddy — Architecture Diagram

This diagram shows the high-level architecture and data flow for the `review-runner` components in `src/`.

```mermaid
flowchart LR
  CLI["CLI / Entrypoint\nsrc/main.py"]
  Config["LLMConfig\nconfig/llm_config.py"]
  Factory["LLMFactory\nsrc/llm_factory.py"]
  LLMInterface["LLMClient (interface)\nsrc/llm_client.py"]
  OpenAI["OpenAIClient\nsrc/openai_client.py"]
  Anthropic["AnthropicClient\nsrc/anthropic_client.py"]
  Engine["CodeReviewEngine\nsrc/code_review_engine.py"]
  Models["ReviewObservation / ReviewResult\nsrc/review_observation.py"]
  GitHub["GitHubClient\nsrc/github_client.py"]
  Storage["review_results/ (JSON files)"]
  Logs["logs/review.log"]
  Tests["Unit tests (MockLLMClient)\ntests/test_code_review.py"]

  CLI -->|loads config| Config
  CLI -->|create client| Factory
  Factory -->|returns concrete client| LLMInterface
  LLMInterface --> OpenAI
  LLMInterface --> Anthropic

  CLI -->|calls| Engine
  Engine -->|calls LLM via| LLMInterface
  Engine -->|parses JSON| Models
  Models -->|serialize| Storage
  CLI -->|optional post| GitHub
  GitHub -->|uses observations| Models

  CLI --> Logs
  Engine --> Logs
  Tests -.->|uses mock client| Engine
```

Notes:
- Entrypoint: [`src.main.perform_code_review`](review-runner/src/main.py) orchestrates the workflow.
- LLM creation: [`src.llm_factory.LLMFactory`](review-runner/src/llm_factory.py) returns a client implementing [`src.llm_client.LLMClient`](review-runner/src/llm_client.py) (e.g., [`src.openai_client.OpenAIClient`](review-runner/src/openai_client.py) or [`src.anthropic_client.AnthropicClient`](review-runner/src/anthropic_client.py)).
- Core analyzer: [`src.code_review_engine.CodeReviewEngine`](review-runner/src/code_review_engine.py) produces [`src.review_observation.ReviewObservation`](review-runner/src/review_observation.py) and [`src.review_observation.ReviewResult`](review-runner/src/review_observation.py).
- Optional GitHub posting: [`src.github_client.GitHubClient`](review-runner/src/github_client.py).
- Config is read from [`config.llm_config.LLMConfig`](review-runner/config/llm_config.py).
- Unit tests use a `MockLLMClient` in [`review-runner/tests/test_code_review.py`](review-runner/tests/test_code_review.py).