"""Empire OS 2.0: safe, standard-library worker coordination and monitoring.
No network requests, AI model, spending, outreach, or deployment.
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

WORKERS = {
    "Scout": {"file": "scout-report.md", "team": "Research", "specialty": "research"},
    "Radar": {"file": "radar-report.md", "team": "Research", "specialty": "monitoring"},
    "Deal Hunter": {"file": "deal-hunter-report.md", "team": "Revenue", "specialty": "contracts"},
    "Career Elevator": {"file": "career-elevator-report.md", "team": "Careers", "specialty": "careers"},
    "Grant Hunter": {"file": "grant-hunter-report.md", "team": "Grants", "specialty": "grants"},
}

PROPOSALS = [
    {"id": "grant-deadline-checker", "name": "Grant Deadline Checker", "team": "Grants", "risk": "low", "purpose": "Verify grant deadlines and eligibility"},
    {"id": "award-opportunity-separator", "name": "Award vs. Opportunity Verifier", "team": "Revenue", "risk": "low", "purpose": "Separate historical awards from active bids"},
    {"id": "source-quality-auditor", "name": "Source Quality Auditor", "team": "Monitoring", "risk": "low", "purpose": "Check report freshness and basic source evidence"},
    {"id": "career-live-listings", "name": "Career Listings Connector", "team": "Careers", "risk": "medium", "purpose": "Find permitted live paid-training listings"},
]

TASK_ROUTES = {
    "research": "Scout", "monitoring": "Radar", "contracts": "Deal Hunter",
    "careers": "Career Elevator", "grants": "Grant Hunter",
}

APPROVAL_POLICY = {
    "sandbox_research": "allowed",
    "new_code_deployment": "owner",
    "outreach": "owner",
    "spending": "owner",
    "contracts": "owner",
    "permission_changes": "owner",
}


def route_task(task_id, specialty, description):
    """Plan a task assignment; do not execute external actions."""
    worker = TASK_ROUTES.get(specialty)
    return {
        "id": task_id,
        "specialty": specialty,
        "description": description,
        "assigned_to": worker,
        "status": "planned" if worker else "needs_owner_review",
        "execution": "not_started",
        "max_delegation_depth": 2,
    }


def audit_reports(max_age_hours=48):
    """Inspect local report files; source accuracy requires separate verification."""
    now = datetime.now(timezone.utc)
    checks = []
    for worker, config in WORKERS.items():
        path = REPORTS / config["file"]
        result = {"worker": worker, "team": config["team"], "file": config["file"]}
        if not path.is_file():
            result.update(status="missing", severity="high", detail="Report file absent")
        elif path.stat().st_size < 100:
            result.update(status="too_small", severity="medium", detail="Report under 100 bytes")
        else:
            age = round((now.timestamp() - path.stat().st_mtime) / 3600, 1)
            content = path.read_text(encoding="utf-8", errors="replace")
            links = len(re.findall(r"https?://[^\s)\]>]+", content))
            result.update(age_hours=age, source_links_found=links)
            if age > max_age_hours:
                result.update(status="stale", severity="medium", detail="File older than freshness threshold")
            elif links == 0:
                result.update(status="needs_source_review", severity="medium", detail="No web links found; not proof of inaccuracy")
            else:
                result.update(status="generated", severity="info", detail="File present; source accuracy not verified")
        checks.append(result)
    return checks


def build_status():
    checks = audit_reports()
    return {
        "schema_version": "2.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "Local GitHub Actions report-file checks",
        "research_checks": checks,
        "research_reports_generated": sum(c["status"] not in ("missing", "too_small") for c in checks),
        "research_reports_expected": len(checks),
        "worker_registry": [
            {"name": name, "team": cfg["team"], "specialty": cfg["specialty"], "execution_mode": "existing_script"}
            for name, cfg in WORKERS.items()
        ],
        "task_routes": TASK_ROUTES,
        "sample_task_plan": route_task("demo-grant-review", "grants", "Research grant opportunities"),
        "development": {"mode": "proposal-and-review-only", "code_generation_enabled": False, "auto_deployment_enabled": False},
        "approval_policy": APPROVAL_POLICY,
        "proposals": [{**p, "status": "candidate", "automated_tests": "not run", "approval": "not granted"} for p in PROPOSALS],
        "limitations": [
            "File existence and links do not establish source accuracy.",
            "Task routing is a plan, not autonomous execution.",
            "Candidate workers are specifications, not implemented bots.",
            "No AI model or code-generation service is connected.",
        ],
    }


def main():
    status = build_status()
    (REPORTS / "empire-status.json").write_text(json.dumps(status, indent=2), encoding="utf-8")
    lines = [
        "# Empire OS â Development & QA Review", "",
        f"Generated: {status['generated_at']}", "",
        "## Research report checks",
    ]
    lines.extend(f"- {c['worker']}: {c['status']} â {c['detail']}" for c in status["research_checks"])
    lines.extend(["", "## Worker delegation", "- Task routing plans assignments; it does not execute tasks.",
                  "- Delegation depth is limited to two levels.", "", "## Candidate workers (NOT deployed)"])
    lines.extend(f"- **{p['name']}** ({p['risk']}): {p['purpose']}" for p in PROPOSALS)
    lines.extend(["", "## Review board rules", "- No automatic spending, outreach, contracts, permission changes or deployment.",
                  "- New code requires isolated tests and owner approval.",
                  "- File and link checks do not verify factual accuracy.", "",
                  "## Next engineering milestone", "- Add independently tested specialist modules and a controlled AI drafting integration."])
    (REPORTS / "development-review.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Empire Engine 2.0: {status['research_reports_generated']}/{status['research_reports_expected']} reports present")


if __name__ == "__main__":
    main()
