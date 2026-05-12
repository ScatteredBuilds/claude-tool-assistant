import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def write_log(
    user_input: str,
    tool_used: bool,
    output_path: str | None = None,
    error: str | None = None,
    log_dir: str = "logs",
) -> None:
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    log_path = Path(log_dir) / "runs.jsonl"

    record: dict[str, Any] = {
        "timestamp": datetime.now(UTC).isoformat(),
        "input": user_input,
        "tool_used": tool_used,
        "output_path": output_path,
        "error": error,
    }

    with log_path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record) + "\n")
