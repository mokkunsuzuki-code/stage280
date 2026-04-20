# Stage280: Signed Decision Verification

## Overview

Stage280 adds issuer authenticity to externally reproducible decisions.

Stage279 proved reproducibility.

Stage280 adds:

- signature (Ed25519)
- public verification
- issuer identity binding

---

## Files

- out/stage280/evidence_summary.json
- out/stage280/decision.json
- out/stage280/decision.sha256
- out/stage280/decision.sig
- keys/ed25519_public.pem

---

## Local Build

python3 tools/build_stage280_signed_decision.py

---

## Local Verification

python3 tools/verify_stage280_signed_decision.py

---

## What This Stage Proves

- decision is deterministic
- SHA256 integrity is verified
- signature is valid
- issuer authenticity is verified

---

## Important Note

This stage does NOT prove global time existence.

Time anchoring (Bitcoin / OpenTimestamps) is separate.

---

## License

MIT License

Copyright (c) 2025 Motohiro Suzuki
