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

## Quick External Verification

git clone https://github.com/mokkunsuzuki-code/stage280.git && \
cd stage280 && \
python3 -m pip install cryptography && \
RUN_ID=$(gh run list --workflow stage280-signature --limit 1 --json databaseId -q '.[0].databaseId') && \
rm -rf downloaded_stage280_signed_decision && \
mkdir -p downloaded_stage280_signed_decision && \
gh run download $RUN_ID --dir downloaded_stage280_signed_decision && \
python3 tools/verify_stage280_signed_decision.py \
  --summary downloaded_stage280_signed_decision/stage280-signed-decision-artifacts/out/stage280/evidence_summary.json \
  --decision downloaded_stage280_signed_decision/stage280-signed-decision-artifacts/out/stage280/decision.json \
  --sha256 downloaded_stage280_signed_decision/stage280-signed-decision-artifacts/out/stage280/decision.sha256 \
  --signature downloaded_stage280_signed_decision/stage280-signed-decision-artifacts/out/stage280/decision.sig \
  --public-key downloaded_stage280_signed_decision/stage280-signed-decision-artifacts/keys/ed25519_public.pem

---

## Public Verification URL

After Pages deployment, the public verification page will be available at:

- https://mokkunsuzuki-code.github.io/stage280/

This page shows:

- final decision
- trust scores
- signature verification status
- public key
- one-command external verification path

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
