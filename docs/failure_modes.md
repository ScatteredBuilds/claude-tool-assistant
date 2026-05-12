# Failure Modes

This project is a small controlled Claude API demo. It is not an autonomous agent.

## Tool Not Called When It Should Be

Claude may summarize an incident without calling the local `classify_risk` tool. The tool prompt is intentionally simple, so this should be checked with small manual eval cases.

## Risk Classification Mismatch

The local tool uses keyword heuristics. It can miss wording that a human would consider important, or classify a note too strongly because a keyword appears without enough context.

## Malformed Structured Output

The final Claude response is expected to be JSON with a specific shape. If the response contains prose, missing keys, or invalid values, Pydantic validation will fail.

## API Failure

The Anthropic API call can fail because of network issues, invalid credentials, rate limits, or service errors.

## Retry Exhaustion

The assistant retries failed API calls a small number of times. If all retries fail, the run is logged with an error.

## Vague Input

Short or vague inputs may not contain enough information for a useful summary or risk classification.
