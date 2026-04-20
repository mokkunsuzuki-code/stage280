#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
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


def compute_expected(summary: dict) -> dict:
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
    parser = argparse.ArgumentParser(description="Verify Stage280 decision reproducibility.")
    parser.add_argument(
        "--summary",
        default="out/stage280/evidence_summary.json",
        help="Path to evidence summary JSON"
    )
    parser.add_argument(
        "--decision",
        default="out/stage280/decision.json",
        help="Path to decision JSON"
    )
    parser.add_argument(
        "--sha256",
        default="out/stage280/decision.sha256",
        help="Path to decision sha256 file"
    )
    args = parser.parse_args()

    summary_path = Path(args.summary)
    decision_path = Path(args.decision)
    sha_path = Path(args.sha256)

    summary = load_json(summary_path)
    decision_actual = load_json(decision_path)
    decision_expected = compute_expected(summary)

    if decision_actual != decision_expected:
        print("[NG] decision.json does not match recomputed result")
        print("[INFO] expected:")
        print(json.dumps(decision_expected, ensure_ascii=False, indent=2, sort_keys=True))
        print("[INFO] actual:")
        print(json.dumps(decision_actual, ensure_ascii=False, indent=2, sort_keys=True))
        sys.exit(1)

    sha_line = sha_path.read_text(encoding="utf-8").strip()
    actual_digest = sha256_file(decision_path)
    expected_line = f"{actual_digest}  {decision_path.name}"

    if sha_line != expected_line:
        print("[NG] decision.sha256 mismatch")
        print(f"[INFO] expected: {expected_line}")
        print(f"[INFO] actual:   {sha_line}")
        sys.exit(1)

    print("[OK] decision recomputation matched")
    print("[OK] sha256 matched")
    print(f"[OK] decision={decision_actual['decision']}")
    print(f"[OK] total_trust={decision_actual['scores']['total_trust']}")


if __name__ == "__main__":
    main()
