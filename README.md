# claude-tool-assistant

A small command-line Claude API workflow for examining tool use, structured-output validation, logging, retries, model fallback, and visible failure handling.

## Status

Learning project / working prototype. It handles one request at a time with one local heuristic tool. It is not an autonomous agent or a production risk system.

## Problem

Tool-calling demos often hide the reliability details around the model call. This project keeps a narrow workflow inspectable: whether the tool ran, whether the response has the required structure, which model was selected, what failed, and what evidence was saved.

## Implemented

- Anthropic Messages API calls from a CLI
- One local `classify_risk` keyword-based tool
- Pydantic validation for `summary`, `risk_level`, `reasoning`, and `tool_used`
- Raw response files under `outputs/` and run-level JSONL logging under `logs/`
- Exponential retries for API errors and fallback on unavailable model IDs
- A five-case API-backed evaluation runner

## Architecture

```text
CLI request -> Claude API -> optional classify_risk tool call -> Claude API
                                                           |
                                      JSON parse -> Pydantic validation
                                                           |
                                      terminal output + raw response + JSONL log
```

The model decides whether to call the local tool. `tools.py` performs the heuristic classification, `schemas.py` validates the final shape, and `logger.py` records run metadata.

## Setup and usage

Python 3.10 or newer and an Anthropic API key are required.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Add your key to `.env`; do not commit that file. `ANTHROPIC_MODEL` is optional and defaults to `claude-sonnet-4-6`.

```dotenv
ANTHROPIC_API_KEY=your_api_key_here
ANTHROPIC_MODEL=claude-sonnet-4-6
```

Run the assistant:

```bash
python assistant.py "Summarize this incident note and classify the risk level: database latency increased during checkout."
```

If the configured model is unavailable, the current fallback list tries `claude-sonnet-4-6` and then `claude-haiku-4-5-20251001`.

## Evaluation and testing

Offline checks:

```bash
python -m py_compile assistant.py tools.py schemas.py logger.py evals/run_evals.py
python -m json.tool evals/sample_inputs.json >/dev/null
```

API-backed eval:

```bash
python evals/run_evals.py
```

For every prompt, the runner checks tool execution, JSON structure, Pydantic validation, and completion without an error. It records retries, selected and failed models, raw output paths, and pass/fail status.

The committed run in `evals/results/` reports 4/5 passing cases using the now-retired `claude-sonnet-4-20250514`. The irrelevant-input case failed because the model did not follow the incident-oriented tool/JSON flow. This historical result has not been relabeled as a result for the updated model; rerun the eval with credentials before making comparisons. See [evals/README.md](evals/README.md).

## Limitations

- Risk classification is a small keyword heuristic and is easy to miss or over-trigger.
- The model may skip the tool, especially for non-incident input.
- JSON is requested by prompt and parsed after generation; malformed output fails the run.
- Retries catch broad exceptions and do not distinguish every permanent error from a transient one.
- Raw API responses and logs may contain user-provided text and should be handled accordingly.
- The eval set is five manual prompts, not a benchmark or evidence of production readiness.
- Results depend on credentials, network access, model availability, and model behavior.

Additional failure modes are documented in [docs/failure_modes.md](docs/failure_modes.md).
