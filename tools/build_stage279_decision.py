#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def time_trust_from_ots(ots_status: str) -> float:
    if ots_status == "verified":
        return 1.0
    if ots_status == "pending":
        return 0.5
    return 0.0


def compute_decision(summary: dict) -> dict:
    integrity = float(summary["scores"]["integrity_trust"])
    execution = float(summary["scores"]["execution_trust"])
    identity = float(summary["scores"]["identity_trust"])
    ots_status = summary["time"]["ots_status"]

    time_trust = time_trust_from_ots(ots_status)
    immediate_score = integrity * execution * identity
    total_trust = immediate_score * time_trust

    if integrity == 1.0 and execution == 1.0 and identity == 1.0 and time_trust == 1.0:
        decision = "accept"
        reason = "All gate conditions satisfied including settled time trust."
    elif integrity == 1.0 and execution == 1.0 and identity == 1.0 and time_trust > 0.0:
        decision = "pending"
        reason = "Immediate gate satisfied; time trust exists but is not yet fully settled."
    else:
        decision = "reject"
        reason = "One or more gate conditions failed."

    return {
        "decision": decision,
        "gate_model": {
            "immediate_gate": "integrity × execution × identity",
            "settlement_gate": "time"
        },
        "reason": reason,
        "scores": {
            "integrity_trust": integrity,
            "execution_trust": execution,
            "identity_trust": identity,
            "immediate_score": round(immediate_score, 6),
            "time_trust": time_trust,
            "total_trust": round(total_trust, 6)
        },
        "time": {
            "ots_status": ots_status
        }
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Stage280 external decision artifact.")
    parser.add_argument(
        "--input",
        default="out/stage280/evidence_summary.json",
        help="Path to evidence summary JSON"
    )
    parser.add_argument(
        "--output",
        default="out/stage280/decision.json",
        help="Path to output decision JSON"
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    sha_path = output_path.with_suffix(".sha256")

    summary = load_json(input_path)
    decision = compute_decision(summary)

    output_path.write_text(
        json.dumps(decision, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8"
    )

    digest = sha256_file(output_path)
    sha_path.write_text(f"{digest}  {output_path.name}\n", encoding="utf-8")

    print(f"[OK] wrote {output_path}")
    print(f"[OK] wrote {sha_path}")
    print(f"[OK] decision={decision['decision']}")
    print(f"[OK] total_trust={decision['scores']['total_trust']}")


if __name__ == "__main__":
    main()
