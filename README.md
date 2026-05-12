# claude-tool-assistant

A small controlled Claude assistant that demonstrates API calls, one local tool, structured output validation, raw response saving, JSONL logging, and basic error handling.

This is a practical AI engineering exercise. It is intentionally small and inspectable.

## What it does

- accepts a user request from the command line
- calls Claude with the Anthropic API
- exposes one local tool: `classify_risk`
- saves raw API responses to `outputs/`
- appends run logs to `logs/runs.jsonl`
- validates the final result with Pydantic
- prints structured JSON output

## What it does not do

- does not run autonomously
- does not use memory
- does not use multiple agents
- does not browse the web
- does not claim production-grade risk scoring

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Set your Anthropic API key:

```text
ANTHROPIC_API_KEY=your_api_key_here
ANTHROPIC_MODEL=claude-3-5-haiku-20241022
```

`ANTHROPIC_MODEL` is optional. If it is not set, the assistant defaults to `claude-3-5-haiku-20241022`.

Do not commit `.env`.

## Example command

```bash
python assistant.py "Summarize this incident note and classify the risk level: database latency increased during checkout."
```

## Expected output shape

```json
{
  "summary": "Short summary of the incident note.",
  "risk_level": "medium",
  "reasoning": "Brief explanation for the risk classification.",
  "tool_used": true,
  "raw_response_path": "outputs/raw_response_YYYYMMDDTHHMMSSZ.json"
}
```

## Current limitations

- risk classification is keyword-based
- only one local tool is available
- malformed Claude JSON is treated as an error
- raw responses may contain API metadata
- eval cases are sample prompts, not benchmarks

## Verification status

- `python3 -m py_compile assistant.py tools.py schemas.py logger.py` passes locally.
- `evals/sample_inputs.json` is valid JSON.
- Claude API runtime verification is pending because `ANTHROPIC_API_KEY` is not set in this environment.

## Next milestones

1. Add a tiny eval runner for `evals/sample_inputs.json`.
2. Record one verified run if `ANTHROPIC_API_KEY` is available.
3. Improve structured-output prompting if malformed JSON appears in real runs.
