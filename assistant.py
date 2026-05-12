import argparse
import json
import os
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from anthropic import Anthropic
from dotenv import load_dotenv
from pydantic import ValidationError

from logger import write_log
from schemas import AssistantResult
from tools import classify_risk


DEFAULT_MODEL = "claude-3-5-haiku-20241022"
MAX_RETRIES = 2

RISK_TOOL = {
    "name": "classify_risk",
    "description": "Classify incident risk using local keyword heuristics.",
    "input_schema": {
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "Incident note or user text to classify.",
            }
        },
        "required": ["text"],
    },
}


def call_with_retries(client: Anthropic, **kwargs: Any) -> Any:
    last_error = None

    for attempt in range(MAX_RETRIES + 1):
        try:
            return client.messages.create(**kwargs)
        except Exception as error:
            last_error = error
            if attempt == MAX_RETRIES:
                break
            time.sleep(2**attempt)

    raise last_error


def response_to_dict(response: Any) -> dict:
    if hasattr(response, "model_dump"):
        return response.model_dump()
    return json.loads(response.json())


def content_blocks_to_dicts(blocks: list[Any]) -> list[dict[str, Any]]:
    return [block.model_dump() if hasattr(block, "model_dump") else dict(block) for block in blocks]


def save_raw_response(response: Any, output_dir: str = "outputs") -> str:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    path = Path(output_dir) / f"raw_response_{timestamp}.json"

    path.write_text(json.dumps(response_to_dict(response), indent=2), encoding="utf-8")
    return str(path)


def get_text_block(response: Any) -> str:
    for block in response.content:
        if block.type == "text":
            return block.text
    raise ValueError("Claude response did not include a text block.")


def extract_json(text: str) -> dict:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.removeprefix("json").strip()
    return json.loads(cleaned)


def run_tool_flow(client: Anthropic, user_request: str, model: str) -> tuple[Any, str, bool]:
    first_response = call_with_retries(
        client,
        model=model,
        max_tokens=500,
        tools=[RISK_TOOL],
        messages=[
            {
                "role": "user",
                "content": (
                    "Summarize the request and call classify_risk when the text describes "
                    f"an incident or operational risk:\n\n{user_request}"
                ),
            }
        ],
    )

    tool_result = None
    tool_used = False
    followup_content: list[dict[str, Any]] = []

    for block in first_response.content:
        if block.type != "tool_use":
            continue

        if block.name == "classify_risk":
            tool_used = True
            tool_result = classify_risk(block.input["text"])
            followup_content.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(tool_result),
                }
            )

    if not tool_used:
        return first_response, "", False

    final_response = call_with_retries(
        client,
        model=model,
        max_tokens=700,
        messages=[
            {
                "role": "user",
                "content": (
                    "Summarize the request and call classify_risk when the text describes "
                    f"an incident or operational risk:\n\n{user_request}"
                ),
            },
            {"role": "assistant", "content": content_blocks_to_dicts(first_response.content)},
            {"role": "user", "content": followup_content},
            {
                "role": "user",
                "content": (
                    "Return only JSON with keys: summary, risk_level, reasoning, tool_used. "
                    "Use the tool result for risk_level and reasoning."
                ),
            },
        ],
    )

    return final_response, json.dumps(tool_result), True


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a small controlled Claude tool assistant.")
    parser.add_argument("request")
    args = parser.parse_args()

    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    model = os.getenv("ANTHROPIC_MODEL", DEFAULT_MODEL)
    if not api_key:
        message = "ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add a key."
        write_log(args.request, tool_used=False, error=message)
        raise SystemExit(message)

    client = Anthropic(api_key=api_key)
    raw_response_path = None
    tool_used = False

    try:
        response, _tool_result, tool_used = run_tool_flow(client, args.request, model)
        raw_response_path = save_raw_response(response)

        data = extract_json(get_text_block(response))
        data["raw_response_path"] = raw_response_path
        result = AssistantResult(**data)

        print(result.model_dump_json(indent=2))
        write_log(args.request, tool_used=tool_used, output_path=raw_response_path)
    except (json.JSONDecodeError, ValidationError, ValueError) as error:
        write_log(args.request, tool_used=tool_used, output_path=raw_response_path, error=str(error))
        raise SystemExit(f"Structured output error: {error}")
    except Exception as error:
        write_log(args.request, tool_used=tool_used, output_path=raw_response_path, error=str(error))
        raise


if __name__ == "__main__":
    main()
