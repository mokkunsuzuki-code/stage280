import json
import os
from pathlib import Path

OUTPUT_DIR = Path("out/ci_evidence")
OUTPUT_PATH = OUTPUT_DIR / "stage276_summary.json"


def main() -> None:
    run_id = os.getenv("GITHUB_RUN_ID", "local")
    run_number = os.getenv("GITHUB_RUN_NUMBER", "local")
    workflow = os.getenv("GITHUB_WORKFLOW", "local")
    sha = os.getenv("GITHUB_SHA", "local")
    ref = os.getenv("GITHUB_REF", "local")
    actor = os.getenv("GITHUB_ACTOR", "local")

    summary = {
        "stage": "Stage276",
        "ci_evidence": True,
        "run_info": {
            "run_id": run_id,
            "run_number": run_number,
            "workflow": workflow,
            "sha": sha,
            "ref": ref,
            "actor": actor,
        },
        "artifact_info": {
            "summary_file": "out/ci_evidence/stage276_summary.json",
            "verify_file": "out/ci_evidence/verify_stage276_result.json",
        },
        "status": "summary_generated",
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("[OK] Stage276 summary generated")
    print(f"[OK] Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
