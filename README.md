# claude-tool-assistant

A small controlled Claude assistant that demonstrates API calls, one local tool, structured output validation, raw response saving, JSONL logging, and basic error handling.

This is a practical AI engineering exercise. It is intentionally small and inspectable.

## Why this exists

This repo is a small Claude API exercise for practicing tool calls, structured response validation, retry and error paths, and runtime logging in one inspectable script.

## Project Status

Status: Early buildout.

Current focus: reliable command-line tool use with visible validation, retry, fallback, output, and logging behavior.

Current evidence:

- `.venv/bin/python -m py_compile assistant.py tools.py schemas.py logger.py` passes locally.
- Claude API runtime was verified locally with `claude-sonnet-4-20250514`.
- `outputs/example_run.md` records a verified runtime example.
- `outputs/model_fallback_example.md` records a verified model fallback example.
- `evals/sample_inputs.json` contains sample prompts, not benchmark results.

## Why I Built This

This project isolates a small Claude tool-calling workflow so the reliability pieces can be inspected directly.

The main question is practical: when an assistant calls a local tool and returns structured output, what checks make failures visible instead of silent?

## What it does

- accepts a user request from the command line
- calls Claude with the Anthropic API
- exposes one local tool: `classify_risk`
- saves raw API responses to `outputs/`
- appends run logs to `logs/runs.jsonl`
- validates the final result with Pydantic
- prints structured JSON output

## Simple Architecture Diagram

```text
Command-line request
        |
        v
Load environment
        |
        v
Anthropic API call
        |
        v
Claude tool request
        |
        v
Local classify_risk tool
        |
        v
Claude final response
        |
        v
JSON parsing
        |
        v
Pydantic validation
        |
        +--> structured JSON output
        |
        +--> raw response saved to outputs/
        |
        +--> JSONL run log in logs/runs.jsonl
```

## Reliability Layer

Structured output prompt:

- The assistant asks Claude to return only JSON with `summary`, `risk_level`, `reasoning`, and `tool_used`.
- This guards against free-form prose that is hard for the script to parse.
- If the response is not valid JSON, `json.loads` raises an error and the run is logged.

Validation:

- `schemas.py` defines `AssistantResult` with Pydantic.
- `risk_level` must be one of `low`, `medium`, or `high`.
- `tool_used` must be a boolean.
- This guards against missing keys, invalid risk levels, and wrong field types.

Retries:

- `call_with_retries` retries failed Anthropic API calls up to `MAX_RETRIES`.
- It does not retry `NotFoundError`; that error is handled by model fallback.
- This guards against some transient API or network failures.

Fallback handling:

- `run_with_model_fallback` tries configured model candidates in order.
- If a model returns `NotFoundError`, the assistant records the failed model and tries the next candidate.
- `outputs/model_fallback_example.md` records a verified fallback run.

Raw response saving:

- `save_raw_response` writes the final API response to `outputs/raw_response_YYYYMMDDTHHMMSSZ.json`.
- This preserves the API response for inspection after the printed output is gone.

JSONL logging:

- `logger.py` appends one JSON record per run to `logs/runs.jsonl`.
- Each record includes timestamp, input, whether a tool was used, output path, selected model, failed models, and error.
- This guards against silent failures by leaving a run-level trace.

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

## Example Output

`outputs/example_run.md` records this verified local runtime output:

```json
{
  "summary": "Database latency increased during the checkout process, potentially impacting customer transactions and sales.",
  "risk_level": "medium",
  "reasoning": "Matched keywords associated with degraded service or important system components.",
  "tool_used": true,
  "raw_response_path": "outputs/raw_response_20260512T002505Z.json"
}
```

The saved example also records a model deprecation warning for `claude-sonnet-4-20250514`.

## Limitations

- risk classification is keyword-based
- only one local tool is available
- malformed Claude JSON is treated as an error
- raw responses may contain API metadata
- eval cases are sample prompts, not benchmarks
- the tool prompt is simple, so Claude may summarize an incident without calling `classify_risk`
- API calls can fail because of network issues, invalid credentials, rate limits, or service errors
- retry handling is limited to a small number of attempts
- model availability can vary by account, region, and model lifecycle

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
