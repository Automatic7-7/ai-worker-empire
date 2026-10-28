"""Empire OS: no-cost, stdlib-only monitoring and worker proposal engine.
No deployment, network calls, payments, or customer outreach.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / 'reports'
REPORTS.mkdir(exist_ok=True)

WORKERS = {
    'Scout': 'scout-report.md',
    'Radar': 'radar-report.md',
    'Deal Hunter': 'deal-hunter-report.md',
    'Career Elevator': 'career-elevator-report.md',
    'Grant Hunter': 'grant-hunter-report.md',
}

PROPOSALS = [
    {'id': 'grant-deadline-checker', 'name': 'Grant Deadline Checker', 'team': 'Grant Hunter', 'purpose': 'Extract and verify application deadlines and eligibility fields from sourced grant records.', 'risk': 'low'},
    {'id': 'award-opportunity-separator', 'name': 'Award vs. Opportunity Verifier', 'team': 'Deal Hunter', 'purpose': 'Flag historical awards separately from open solicitations so users do not mistake awards for active bids.', 'risk': 'low'},
    {'id': 'source-quality-auditor', 'name': 'Source Quality Auditor', 'team': 'Monitoring', 'purpose': 'Check source timestamps, missing citations, duplicates and broken report generation.', 'risk': 'low'},
    {'id': 'career-live-listings', 'name': 'Career Listings Connector', 'team': 'Career Elevator', 'purpose': 'Research permitted sources for current paid training and apprenticeship openings.', 'risk': 'medium'},
]


def assess_reports():
    checks = []
    for worker, filename in WORKERS.items():
        path = REPORTS / filename
        if not path.exists():
            checks.append({'worker': worker, 'status': 'missing', 'detail': 'Report not generated'})
        elif path.stat().st_size < 100:
            checks.append({'worker': worker, 'status': 'warning', 'detail': 'Report unusually short'})
        else:
            checks.append({'worker': worker, 'status': 'generated', 'detail': 'Report file present; content not independently verified'})
    return checks


def build_status():
    checks = assess_reports()
    status = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'source': 'GitHub Actions report-file checks',
        'research_checks': checks,
        'research_reports_generated': sum(c['status'] == 'generated' for c in checks),
        'research_reports_expected': len(checks),
        'development': {'mode': 'proposal-and-review-only', 'code_generation_enabled': False, 'auto_deployment_enabled': False},
        'approval_policy': {'sandbox_research': 'allowed', 'new_code_deployment': 'owner', 'outreach': 'owner', 'spending': 'owner', 'contracts': 'owner', 'permission_changes': 'owner'},
        'proposals': [{**p, 'status': 'candidate', 'automated_tests': 'not run', 'approval': 'not granted'} for p in PROPOSALS],
        'limitations': ['Report existence does not prove source accuracy.', 'Candidate workers are specifications, not implemented bots.', 'No AI model or code-generation service is connected.'],
    }
    return status


def main():
    status = build_status()
    (REPORTS / 'empire-status.json').write_text(json.dumps(status, indent=2) + '\n', encoding='utf-8')
    lines = ['# Empire OS — Development & QA Review', '', 'Generated: ' + status['generated_at'], '', '## Research report checks']
    lines += [f"- {c['worker']}: {c['status']} — {c['detail']}" for c in status['research_checks']]
    lines += ['', '## Candidate worker specifications (NOT deployed)']
    lines += [f"- **{p['name']}** ({p['risk']} risk): {p['purpose']}" for p in status['proposals']]
    lines += ['', '## Review board rules', '- Candidate specifications are not code and have not passed functionality/security tests.', '- No auto-deployment, customer outreach, spending, contracts, or permission changes.', '- New code must pass isolated tests and owner review before any production deployment.', '', '## Next engineering milestone', 'Connect a sandboxed code-drafting service and independent CI test suite using narrowly scoped permissions.']
    (REPORTS / 'development-review.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f"Empire engine: {status['research_reports_generated']}/{status['research_reports_expected']} research reports present; {len(PROPOSALS)} candidates")


if __name__ == '__main__':
    main()
