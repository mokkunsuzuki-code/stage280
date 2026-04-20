#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def run_command(cmd: list[str]) -> tuple[int, str]:
    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    return proc.returncode, proc.stdout


def main() -> int:
    summary_path = Path("out/stage277/summary.json")
    sha256_path = Path("out/stage277/summary.sha256")
    ots_path = Path("out/stage277/summary.json.ots")

    if not summary_path.exists():
        print("[FAIL] missing summary.json")
        return 1

    if not sha256_path.exists():
        print("[FAIL] missing summary.sha256")
        return 1

    if not ots_path.exists():
        print("[FAIL] missing summary.json.ots")
        return 1

    actual_digest = sha256_file(summary_path)
    expected_line = sha256_path.read_text(encoding="utf-8").strip()
    expected_digest = expected_line.split()[0]

    if actual_digest != expected_digest:
        print("[FAIL] sha256 mismatch")
        print(f"expected: {expected_digest}")
        print(f"actual:   {actual_digest}")
        return 1

    print("[OK] sha256 matches")

    try:
        code, output = run_command(["ots", "verify", str(ots_path)])
    except FileNotFoundError:
        print("[FAIL] ots command not found")
        return 1

    if output:
        print(output.strip())

    if code == 0:
        print("[OK] OpenTimestamps verification completed")
        return 0

    pending_markers = [
        "Pending confirmation in Bitcoin blockchain",
        "Timestamp not complete",
    ]

    if any(marker in output for marker in pending_markers):
        print("[OK] OpenTimestamps stamp exists and is pending Bitcoin confirmation")
        print("[OK] Stage277 external anchor is present")
        return 0

    print("[FAIL] ots verification failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
