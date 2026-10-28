
"""Empire OS — AI Architect foundation.

Creates prioritized development proposals from worker status.
No paid services, external actions, or automatic deployments.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

STATUS = Path("status/empire-status.json")
OUTPUT = Path("reports/architect-plan.json")


def build_plan(status):
    tasks = []

    for check in status.get("research_checks", []):
        worker = check.get("worker", "Unknown")
        state = check.get("status", "unknown")

        if state not in ("generated", "passed", "ok"):
            tasks.append({
                "worker": worker,
                "problem": check.get("detail", state),
                "priority": "high",
                "proposed_action": (
                    "Investigate source evidence, design a fix, "
                    "and create automated verification tests."
                ),
                "approval_required": True,
            })

    tasks.append({
        "worker": "AI Architect",
        "problem": "Worker development needs repeatable testing.",
        "priority": "medium",
        "proposed_action": (
            "Design reusable worker templates, regression tests, "
            "and version comparison procedures."
        ),
        "approval_required": True,
    })

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "planning_only",
        "budget_usd": 0,
        "automatic_deployment": False,
        "tasks": tasks,
    }


def main():
    if not STATUS.exists():
        print("No published status file found.")
        return

    status = json.loads(STATUS.read_text(encoding="utf-8"))
    plan = build_plan(status)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(plan, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"AI Architect created {len(plan['tasks'])} development tasks.")


if __name__ == "__main__":
    main()
