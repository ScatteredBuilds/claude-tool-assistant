# claude-tool-assistant

A small controlled Claude assistant that demonstrates API calls, one local tool, structured output validation, raw response saving, JSONL logging, and basic error handling.

This is a practical AI engineering exercise. It is intentionally small and inspectable.

## Why this exists

This repo is a small Claude API exercise for practicing tool calls, structured response validation, retry and error paths, and runtime logging in one inspectable script.

## What it does

- accepts a user request from the command line
- calls Claude with the Anthropic API
- exposes one local tool: `classify_risk`
- saves raw API responses to `outputs/`
- appends run logs to `logs/runs.jsonl`
- validates the final result with Pydantic
- prints structured JSON output

## Flow

```text
User Request
      |
   Claude
      |
  Tool Call
      |
 Tool Result
      |
Structured Output
      |
  Logging
```

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
ANTHROPIC_MODEL=claude-sonnet-4-20250514
```

`ANTHROPIC_MODEL` is optional. If it is not set, the assistant defaults to `claude-sonnet-4-20250514`.

Do not commit `.env`.

## Model fallback

Anthropic model availability can vary by account, region, and model lifecycle. A model ID that works in one account may return `NotFoundError` in another.

The assistant tries models in this order:

1. `ANTHROPIC_MODEL`, if set
2. `claude-sonnet-4-20250514`
3. `claude-3-7-sonnet-20250219`
4. `claude-3-5-sonnet-20241022`
5. `claude-3-haiku-20240307`

If a model returns `NotFoundError`, the assistant records that model in the run log and tries the next candidate. On success, it prints the selected model before the structured result.

A verified fallback example is recorded in `outputs/model_fallback_example.md`.

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

- `.venv/bin/python -m py_compile assistant.py tools.py schemas.py logger.py` passes locally.
- `evals/sample_inputs.json` is valid JSON.
- Claude API runtime was verified locally with `claude-sonnet-4-20250514`.
- Verified runtime output is recorded in `outputs/example_run.md`.
- Model fallback behavior was verified locally with an unavailable configured model. Output is recorded in `outputs/model_fallback_example.md`.

## Completed

- Command-line request handling against the Anthropic API.
- Local `classify_risk` tool call flow.
- Pydantic validation for the final structured output.
- Retry handling and model fallback for unavailable models.
- Raw response saving and JSONL run logging.

## Next

- Add a tiny eval runner for `evals/sample_inputs.json`.
- Improve structured-output prompting if malformed JSON appears in real runs.
- Track model deprecation warnings and update the default model after verification.
