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


def build_summary_dict(repo_root: str, git_commit: str, git_branch: str, generated_at: str) -> dict:
    return {
        "stage": "stage280",
        "title": "Manifest Packaging for Reproducible Verification",
        "generated_at_utc": generated_at,
        "git": {
            "commit": git_commit,
            "branch": git_branch,
        },
        "artifact": {
            "summary_file": "out/stage280/summary.json",
            "sha256_file": "out/stage280/summary.sha256",
            "ots_file": "out/stage280/summary.json.ots",
            "manifest_file": "out/stage280/manifest.json",
        },
        "claim": {
            "what_this_stage_proves": [
                "A deterministic summary is generated.",
                "The summary is hashed with SHA-256.",
                "The summary is externally anchored via OpenTimestamps.",
                "A manifest packages the evidence set.",
                "A fixed verification procedure can reproduce the verification result."
            ],
            "what_this_stage_does_not_prove": [
                "Direct Bitcoin on-chain inscription by this repository alone.",
                "Immediate Bitcoin finality at workflow runtime.",
                "Identity proof beyond repository/workflow context."
            ]
        },
        "environment": {
            "repo_root": repo_root
        }
    }


def main() -> None:
    out_dir = Path("out/stage280")
    out_dir.mkdir(parents=True, exist_ok=True)

    summary_path = out_dir / "summary.json"
    sha256_path = out_dir / "summary.sha256"
    ots_path = out_dir / "summary.json.ots"
    manifest_path = out_dir / "manifest.json"

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

    if summary_path.exists():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        generated_at = summary.get("generated_at_utc", datetime.now(timezone.utc).isoformat())
    else:
        generated_at = datetime.now(timezone.utc).isoformat()
        summary = build_summary_dict(repo_root, git_commit, git_branch, generated_at)
        summary_path.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8"
        )

    summary_digest = sha256_file(summary_path)
    sha256_path.write_text(f"{summary_digest}  {summary_path.name}\n", encoding="utf-8")

    manifest = {
        "stage": "stage280",
        "title": "Verification Manifest",
        "generated_at_utc": generated_at,
        "git": {
            "commit": git_commit,
            "branch": git_branch,
        },
        "files": {
            "summary": {
                "path": "out/stage280/summary.json",
                "sha256": summary_digest,
            },
            "summary_sha256": {
                "path": "out/stage280/summary.sha256",
                "sha256": sha256_file(sha256_path),
            },
            "summary_ots": {
                "path": "out/stage280/summary.json.ots",
                "sha256": sha256_file(ots_path) if ots_path.exists() else None,
            },
        },
        "verification_procedure": [
            "Check that summary.json exists.",
            "Check that summary.sha256 exists.",
            "Check that summary.json.ots exists.",
            "Recompute SHA-256 of summary.json.",
            "Compare it with summary.sha256.",
            "Run OpenTimestamps verification on summary.json.ots.",
            "Accept both complete verification and pending Bitcoin confirmation."
        ],
        "verification_policy": {
            "sha256_must_match": True,
            "ots_complete_ok": True,
            "ots_pending_ok": True
        }
    }

    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8"
    )

    print(f"[OK] wrote {summary_path}")
    print(f"[OK] wrote {sha256_path}")
    print(f"[OK] wrote {manifest_path}")
    print(f"[OK] summary sha256={summary_digest}")


if __name__ == "__main__":
    main()
