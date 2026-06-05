import argparse
import json
import os
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from anthropic import Anthropic, NotFoundError
from dotenv import load_dotenv
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import assistant
from schemas import AssistantResult


PASS = "PASS"
FAIL = "FAIL"
REQUIRED_KEYS = {"summary", "risk_level", "reasoning", "tool_used", "raw_response_path"}


class RetryTracker:
    def __init__(self) -> None:
        self.retries_required = False

    def call_with_retries(self, client: Anthropic, **kwargs: Any) -> Any:
        last_error = None

        for attempt in range(assistant.MAX_RETRIES + 1):
            try:
                return client.messages.create(**kwargs)
            except NotFoundError:
                raise
            except Exception as error:
                last_error = error
                if attempt == assistant.MAX_RETRIES:
                    break
                self.retries_required = True
                time.sleep(2**attempt)

        raise last_error


def load_cases(path: Path) -> list[dict[str, str]]:
    return json.loads(path.read_text(encoding="utf-8"))


def output_structure_status(data: dict[str, Any]) -> str:
    if REQUIRED_KEYS.issubset(data.keys()):
        return PASS
    return FAIL


def case_status(checks: dict[str, str]) -> str:
    if all(status == PASS for status in checks.values()):
        return PASS
    return FAIL


def evaluate_case(
    client: Anthropic,
    case: dict[str, str],
    models: list[str],
) -> dict[str, Any]:
    retry_tracker = RetryTracker()
    original_call_with_retries = assistant.call_with_retries
    assistant.call_with_retries = retry_tracker.call_with_retries

    raw_response_path = None
    selected_model = None
    failed_models: list[str] = []
    checks = {
        "tool_execution": FAIL,
        "schema_validation": FAIL,
        "output_structure": FAIL,
        "no_failure": FAIL,
    }
    error = None

    try:
        response, _tool_result, tool_used, selected_model, failed_models = (
            assistant.run_with_model_fallback(client, case["prompt"], models)
        )
        raw_response_path = assistant.save_raw_response(response)
        checks["tool_execution"] = PASS if tool_used else FAIL

        data = assistant.extract_json(assistant.get_text_block(response))
        data["raw_response_path"] = raw_response_path
        checks["output_structure"] = output_structure_status(data)

        AssistantResult(**data)
        checks["schema_validation"] = PASS
        checks["no_failure"] = PASS
    except (json.JSONDecodeError, ValidationError, ValueError) as caught_error:
        error = f"Structured output error: {caught_error}"
    except assistant.ModelFallbackError as caught_error:
        failed_models = caught_error.failed_models
        error = str(caught_error)
    except Exception as caught_error:
        error = str(caught_error)
    finally:
        assistant.call_with_retries = original_call_with_retries

    status = case_status(checks)

    return {
        "case": case.get("case"),
        "prompt": case["prompt"],
        "status": status,
        "checks": checks,
        "retries_required": retry_tracker.retries_required,
        "failure_occurred": status == FAIL,
        "selected_model": selected_model,
        "failed_models": failed_models,
        "raw_response_path": raw_response_path,
        "error": error,
    }


def write_results(results: dict[str, Any], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    path = output_dir / f"eval_results_{timestamp}.json"
    path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run simple assistant eval cases.")
    parser.add_argument("--input", default="evals/sample_inputs.json")
    parser.add_argument("--output-dir", default="evals/results")
    args = parser.parse_args()

    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    preferred_model = os.getenv("ANTHROPIC_MODEL", assistant.DEFAULT_MODEL)
    if not api_key:
        raise SystemExit("ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add a key.")

    cases = load_cases(Path(args.input))
    client = Anthropic(api_key=api_key)
    models = assistant.model_candidates(preferred_model)

    results = {
        "created_at": datetime.now(UTC).isoformat(),
        "input_file": args.input,
        "checks": [
            "tool_execution",
            "schema_validation",
            "output_structure",
            "no_failure",
        ],
        "cases": [evaluate_case(client, case, models) for case in cases],
    }

    output_path = write_results(results, Path(args.output_dir))

    for result in results["cases"]:
        print(f"{result['status']}: {result['case']}")

    print(f"Saved results to {output_path}")

    if any(result["status"] == FAIL for result in results["cases"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
