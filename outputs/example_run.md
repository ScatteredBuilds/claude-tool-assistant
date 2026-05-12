# Example Run

Status: verified locally with `.venv/bin/python`.

Command:

```bash
.venv/bin/python assistant.py "Summarize this incident note and classify the risk level: database latency increased during checkout."
```

Output:

```text
/Users/adamvaldez/Documents/Codex/2026-05-11/github-plugin-github-openai-curated-you/claude-tool-assistant/assistant.py:42: DeprecationWarning: The model 'claude-sonnet-4-20250514' is deprecated and will reach end-of-life on June 15th, 2026.
Please migrate to a newer model. Visit https://docs.anthropic.com/en/docs/resources/model-deprecations for more information.
  return client.messages.create(**kwargs)
{
  "summary": "Database latency increased during the checkout process, potentially impacting customer transactions and sales.",
  "risk_level": "medium",
  "reasoning": "Matched keywords associated with degraded service or important system components.",
  "tool_used": true,
  "raw_response_path": "outputs/raw_response_20260512T002505Z.json"
}
```

The raw response JSON was saved locally by the script but is not committed.
