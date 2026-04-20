#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def run_git(args: list[str]) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    out_dir = Path("out/stage277")
    out_dir.mkdir(parents=True, exist_ok=True)

    summary_path = out_dir / "summary.json"
    sha256_path = out_dir / "summary.sha256"

    try:
        git_commit = run_git(["rev-parse", "HEAD"])
    except Exception:
        git_commit = "unknown"

    try:
        git_branch = run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    except Exception:
        git_branch = "unknown"

    try:
        repo_root = run_git(["rev-parse", "--show-toplevel"])
    except Exception:
        repo_root = os.getcwd()

    generated_at = datetime.now(timezone.utc).isoformat()

    summary = {
        "stage": "stage277",
        "title": "External Anchor Integration",
        "generated_at_utc": generated_at,
        "git": {
            "commit": git_commit,
            "branch": git_branch,
        },
        "artifact": {
            "summary_file": "out/stage277/summary.json",
            "sha256_file": "out/stage277/summary.sha256",
            "ots_file": "out/stage277/summary.json.ots",
        },
        "claim": {
            "what_this_stage_proves": [
                "A deterministic CI summary is generated.",
                "The summary is hashed with SHA-256.",
                "The summary hash is externally anchored via OpenTimestamps.",
                "The anchor artifact can be independently verified later."
            ],
            "what_this_stage_does_not_prove": [
                "Direct Bitcoin on-chain inscription by this repository alone.",
                "Immediate Bitcoin confirmation at workflow execution time.",
                "Identity proof beyond repository and workflow context."
            ]
        },
        "environment": {
            "repo_root": repo_root
        }
    }

    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8"
    )

    digest = sha256_file(summary_path)
    sha256_path.write_text(f"{digest}  {summary_path.name}\n", encoding="utf-8")

    print(f"[OK] wrote {summary_path}")
    print(f"[OK] wrote {sha256_path}")
    print(f"[OK] sha256={digest}")


if __name__ == "__main__":
    main()
