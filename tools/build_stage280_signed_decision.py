#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


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


def load_private_key(path: Path) -> Ed25519PrivateKey:
    key = serialization.load_pem_private_key(
        path.read_bytes(),
        password=None
    )
    if not isinstance(key, Ed25519PrivateKey):
        raise TypeError("Private key is not Ed25519")
    return key


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and sign Stage280 decision artifact.")
    parser.add_argument("--input", default="out/stage280/evidence_summary.json")
    parser.add_argument("--output", default="out/stage280/decision.json")
    parser.add_argument("--private-key", default="keys/ed25519_private.pem")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    private_key_path = Path(args.private_key)

    sha_path = output_path.with_suffix(".sha256")
    sig_path = output_path.with_suffix(".sig")

    summary = load_json(input_path)
    decision = compute_decision(summary)

    output_path.write_text(
        json.dumps(decision, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8"
    )

    digest = sha256_file(output_path)
    sha_path.write_text(f"{digest}  {output_path.name}\n", encoding="utf-8")

    private_key = load_private_key(private_key_path)
    signature = private_key.sign(output_path.read_bytes())
    sig_path.write_bytes(signature)

    print(f"[OK] wrote {output_path}")
    print(f"[OK] wrote {sha_path}")
    print(f"[OK] wrote {sig_path}")
    print(f"[OK] decision={decision['decision']}")
    print(f"[OK] total_trust={decision['scores']['total_trust']}")


if __name__ == "__main__":
    main()
