# Model Fallback Example

Status: verified locally with `.venv/bin/python`.

This run forced `ANTHROPIC_MODEL=claude-3-5-haiku-20241022`, which was not available for the local Anthropic account. The assistant caught the `NotFoundError`, recorded the failed model, and continued to the fallback list.

Earlier local runtime also observed `NotFoundError` for the alias `claude-3-5-haiku-latest`.

Command:

```bash
ANTHROPIC_MODEL=claude-3-5-haiku-20241022 .venv/bin/python assistant.py "Summarize this incident note and classify the risk level: database latency increased during checkout."
```

Output:

```text
/Users/adamvaldez/Documents/Codex/2026-05-11/github-plugin-github-openai-curated-you/claude-tool-assistant/assistant.py:56: DeprecationWarning: The model 'claude-3-5-haiku-20241022' is deprecated and will reach end-of-life on February 19th, 2026.
Please migrate to a newer model. Visit https://docs.anthropic.com/en/docs/resources/model-deprecations for more information.
  return client.messages.create(**kwargs)
/Users/adamvaldez/Documents/Codex/2026-05-11/github-plugin-github-openai-curated-you/claude-tool-assistant/assistant.py:56: DeprecationWarning: The model 'claude-sonnet-4-20250514' is deprecated and will reach end-of-life on June 15th, 2026.
Please migrate to a newer model. Visit https://docs.anthropic.com/en/docs/resources/model-deprecations for more information.
  return client.messages.create(**kwargs)
Failed models: claude-3-5-haiku-20241022
Selected model: claude-sonnet-4-20250514
{
  "summary": "Database latency increased during the checkout process, potentially impacting customer transactions and user experience.",
  "risk_level": "medium",
  "reasoning": "Matched keywords associated with degraded service or important system components.",
  "tool_used": true,
  "raw_response_path": "outputs/raw_response_20260512T003140Z.json"
}
```

The raw response JSON and local run logs were not committed.
