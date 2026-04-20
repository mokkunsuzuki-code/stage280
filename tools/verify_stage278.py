#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
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
    manifest_path = Path("out/stage280/manifest.json")

    if not manifest_path.exists():
        print("[FAIL] missing manifest.json")
        return 1

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    summary_path = Path(manifest["files"]["summary"]["path"])
    sha256_path = Path(manifest["files"]["summary_sha256"]["path"])
    ots_path = Path(manifest["files"]["summary_ots"]["path"])

    if not summary_path.exists():
        print("[FAIL] missing summary.json")
        return 1

    if not sha256_path.exists():
        print("[FAIL] missing summary.sha256")
        return 1

    if not ots_path.exists():
        print("[FAIL] missing summary.json.ots")
        return 1

    actual_summary_digest = sha256_file(summary_path)
    expected_summary_digest = manifest["files"]["summary"]["sha256"]

    if actual_summary_digest != expected_summary_digest:
        print("[FAIL] summary.json digest mismatch against manifest")
        print(f"expected: {expected_summary_digest}")
        print(f"actual:   {actual_summary_digest}")
        return 1

    summary_sha256_line = sha256_path.read_text(encoding="utf-8").strip()
    summary_sha256_from_file = summary_sha256_line.split()[0]

    if actual_summary_digest != summary_sha256_from_file:
        print("[FAIL] summary.sha256 does not match summary.json")
        print(f"expected: {summary_sha256_from_file}")
        print(f"actual:   {actual_summary_digest}")
        return 1

    actual_sha256_file_digest = sha256_file(sha256_path)
    expected_sha256_file_digest = manifest["files"]["summary_sha256"]["sha256"]

    if actual_sha256_file_digest != expected_sha256_file_digest:
        print("[FAIL] summary.sha256 file digest mismatch against manifest")
        print(f"expected: {expected_sha256_file_digest}")
        print(f"actual:   {actual_sha256_file_digest}")
        return 1

    actual_ots_digest = sha256_file(ots_path)
    expected_ots_digest = manifest["files"]["summary_ots"]["sha256"]

    if expected_ots_digest is not None and actual_ots_digest != expected_ots_digest:
        print("[FAIL] summary.json.ots digest mismatch against manifest")
        print(f"expected: {expected_ots_digest}")
        print(f"actual:   {actual_ots_digest}")
        return 1

    print("[OK] manifest file bindings verified")
    print("[OK] summary.json matches summary.sha256")

    try:
        code, output = run_command(["ots", "verify", str(ots_path)])
    except FileNotFoundError:
        print("[FAIL] ots command not found")
        return 1

    if output:
        print(output.strip())

    if code == 0:
        print("[OK] OpenTimestamps verification completed")
        print("[OK] Stage280 verification succeeded")
        return 0

    pending_markers = [
        "Pending confirmation in Bitcoin blockchain",
        "Timestamp not complete",
    ]

    if any(marker in output for marker in pending_markers):
        print("[OK] OpenTimestamps stamp exists and is pending Bitcoin confirmation")
        print("[OK] Stage280 verification succeeded under pending policy")
        return 0

    print("[FAIL] ots verification failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
