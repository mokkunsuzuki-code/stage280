import json
from pathlib import Path

SUMMARY_PATH = Path("out/ci_evidence/stage276_summary.json")
OUTPUT_PATH = Path("out/ci_evidence/verify_stage276_result.json")


def main() -> None:
    if not SUMMARY_PATH.exists():
        raise SystemExit(f"Missing summary file: {SUMMARY_PATH}")

    with SUMMARY_PATH.open("r", encoding="utf-8") as f:
        summary = json.load(f)

    run_info = summary.get("run_info", {})
    artifact_info = summary.get("artifact_info", {})

    result = {
        "stage": "Stage276",
        "summary_exists": True,
        "run_info_present": bool(run_info),
        "artifact_info_present": bool(artifact_info),
        "checks": {
            "has_run_id": "run_id" in run_info,
            "has_workflow": "workflow" in run_info,
            "has_summary_file_reference": "summary_file" in artifact_info,
            "has_verify_file_reference": "verify_file" in artifact_info,
        },
        "result": "verified" if run_info and artifact_info else "incomplete",
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("[OK] Stage276 verification result generated")
    print(f"[OK] Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
