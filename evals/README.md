# Claude Tool Assistant Evaluation

## Purpose

This evaluation runner checks whether the assistant can process the prompts in `evals/sample_inputs.json` through the existing tool-calling flow.

It reports pass/fail status for:

- tool execution
- schema validation
- output structure
- whether a failure occurred

It also records whether retries were required during the run.

## What Is Being Evaluated

The runner uses the existing assistant code where possible:

- `assistant.run_with_model_fallback`
- `assistant.run_tool_flow`
- `assistant.extract_json`
- `assistant.get_text_block`
- `assistant.save_raw_response`
- `schemas.AssistantResult`

For each prompt, the runner checks:

- whether the local `classify_risk` tool was used
- whether the final response can be parsed as JSON
- whether the parsed output has the expected fields
- whether Pydantic validation succeeds
- whether the run completed without an error
- whether retries were required

Results are saved as JSON files in `evals/results/`.

## What Is Not Being Evaluated

This is not a benchmark.

The runner does not measure:

- answer quality
- semantic correctness of the summary
- model intelligence
- production readiness
- long-term reliability
- latency
- cost

The sample prompts are small manual checks, not a benchmark dataset.

## How To Run

```bash
.venv/bin/python evals/run_evals.py
```

The runner requires `ANTHROPIC_API_KEY` in the environment or `.env`.

Optional arguments:

```bash
.venv/bin/python evals/run_evals.py --input evals/sample_inputs.json --output-dir evals/results
```

## Output

Each run writes a JSON file under `evals/results/`.

Each case records:

- case name
- prompt
- pass/fail status
- pass/fail checks
- whether retries were required
- whether a failure occurred
- selected model
- failed models
- raw response path
- error, if present

The runner also saves raw API responses through the existing `assistant.save_raw_response` function.

## Limitations

- The runner calls the Anthropic API, so results depend on network access, credentials, model availability, and API behavior.
- The runner reports pass/fail checks only. It does not create benchmark scores.
- A passing case means the tool flow, structure, and schema checks passed. It does not prove the answer is useful.
- The tool is keyword-based, so risk classification can miss wording or over-classify text.
- The sample input file currently contains a small set of manual prompts.
- Retries are recorded only as required or not required.
