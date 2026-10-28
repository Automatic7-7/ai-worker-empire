
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlencode

REPORTS = Path("reports")
REPORTS.mkdir(exist_ok=True)

HEADERS = {
    "User-Agent": "EmpireOS-DealHunter/2.0",
    "Content-Type": "application/json"
}

INDUSTRIES = {
    "Transportation": ["transportation", "trucking"],
    "Medical Services": ["medical courier", "healthcare"],
    "Construction": ["construction"],
    "Staffing": ["staffing"],
    "Cleaning": ["janitorial"],
    "Technology": ["information technology"],
    "Logistics": ["logistics"],
    "Facilities": ["facility maintenance"]
}

# Research categories, not guaranteed job openings.
CAREER_PATHS = [
    {
        "career": "Electrician Apprentice",
        "sector": "Skilled Trades",
        "education": "High school/GED often accepted",
        "experience": "Many apprenticeships accept beginners",
        "training": "Paid registered apprenticeship",
        "advancement": "Apprentice to journey-level electrician",
        "search": "electrician apprenticeship"
    },
    {
        "career": "HVAC Apprentice",
        "sector": "Skilled Trades",
        "education": "High school/GED commonly accepted",
        "experience": "Entry-level routes available",
        "training": "Employer or apprenticeship training",
        "advancement": "Technician to senior technician",
        "search": "HVAC apprenticeship"
    },
    {
        "career": "Elevator Mechanic Apprentice",
        "sector": "Skilled Trades",
        "education": "High school/GED commonly required",
        "experience": "Apprenticeship entry route",
        "training": "Paid apprenticeship",
        "advancement": "Apprentice to elevator mechanic",
        "search": "elevator constructor apprenticeship"
    },
    {
        "career": "Water Treatment Operator Trainee",
        "sector": "Utilities",
        "education": "High school/GED often accepted",
        "experience": "Trainee positions may accept beginners",
        "training": "On-the-job training and certification",
        "advancement": "Trainee to licensed operator",
        "search": "water treatment operator trainee"
    },
    {
        "career": "Railroad Conductor Trainee",
        "sector": "Transportation",
        "education": "High school/GED commonly accepted",
        "experience": "Some employers train new hires",
        "training": "Employer-paid training may be available",
        "advancement": "Conductor to other rail operations roles",
        "search": "railroad conductor trainee"
    },
    {
        "career": "Utility Lineworker Apprentice",
        "sector": "Utilities",
        "education": "High school/GED commonly accepted",
        "experience": "Apprenticeship entry route",
        "training": "Paid apprenticeship",
        "advancement": "Apprentice to journey-level lineworker",
        "search": "lineworker apprenticeship"
    },
    {
        "career": "Building Maintenance Trainee",
        "sector": "Facilities",
        "education": "High school/GED often accepted",
        "experience": "Entry-level opportunities exist",
        "training": "On-the-job training",
        "advancement": "Technician to facilities supervisor",
        "search": "building maintenance trainee"
    },
    {
        "career": "IT Support Apprentice",
        "sector": "Technology",
        "education": "Some programs accept high school/GED",
        "experience": "Beginner programs exist",
        "training": "Apprenticeship or employer training",
        "advancement": "Support to systems or network roles",
        "search": "IT support apprenticeship"
    }
]

def request_json(url, payload=None):
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    request = Request(
        url,
        data=data,
        headers=HEADERS,
        method="POST" if data else "GET"
    )

    for attempt in range(3):
        try:
            with urlopen(request, timeout=30) as response:
                return json.load(response), None
        except Exception as error:
            if attempt == 2:
                return None, str(error)
            time.sleep(attempt + 1)

def research_business_awards():
    url = (
        "https://api.usaspending.gov/api/v2/"
        "search/spending_by_award/"
    )

    lines = [
        "# Empire OS - Business Deal Hunter",
        "",
        "Source: USAspending.gov",
        "",
        "**These are historical awards, not open contracts.**",
        ""
    ]

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    seen = set()
    errors = 0

    for industry, keywords in INDUSTRIES.items():
        lines.extend([f"## {industry}", ""])

        for keyword in keywords:
            payload = {
                "filters": {
                    "keywords": [keyword],
                    "award_type_codes": ["A", "B", "C", "D"],
                    "time_period": [{
                        "start_date": "2025-01-01",
                        "end_date": today
                    }]
                },
                "fields": [
                    "Award ID",
                    "Recipient Name",
                    "Award Amount",
                    "Description",
                    "Awarding Agency",
                    "Place of Performance State Code"
                ],
                "page": 1,
                "limit": 10,
                "sort": "Award Amount",
                "order": "desc",
                "subawards": False
            }

            result, error = request_json(url, payload)

            if error:
                errors += 1
                lines.append(
                    f"- Retrieval error for {keyword}: {error}"
                )
                continue

            for award in result.get("results", []):
                award_id = str(award.get("Award ID") or "")
                if not award_id or award_id in seen:
                    continue

                seen.add(award_id)

                recipient = award.get("Recipient Name") or "Unknown"
                agency = award.get("Awarding Agency") or "Unknown"
                amount = award.get("Award Amount")
                description = str(
                    award.get("Description") or ""
                )[:300]

                try:
                    money = f"${float(amount):,.2f}"
                except (TypeError, ValueError):
                    money = "Not available"

                lines.extend([
                    f"### {recipient}",
                    f"- Award ID: {award_id}",
                    f"- Awarding agency: {agency}",
                    f"- Award amount: {money}",
                    f"- Description: {description}",
                    "- Classification: Historical award",
                    "- Action: Investigate buyer and contractor",
                    ""
                ])

    lines.extend([
        "## Summary",
        f"- Unique awards: {len(seen)}",
        f"- Retrieval errors: {errors}",
        "- Verify all leads before outreach.",
        "- Do not automatically bid or spend money."
    ])

    (REPORTS / "deal-hunter-report.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )

    return len(seen), errors

def research_career_paths():
    lines = [
        "# Empire OS - Career Elevator",
        "",
        "## Mission",
        "Help people find accessible routes into higher-paying",
        "careers without requiring a college degree.",
        "",
        "## Matching priorities",
        "- High school diploma or GED accepted",
        "- No prior industry experience where possible",
        "- Paid training or apprenticeships preferred",
        "- Free or affordable training alternatives",
        "- Clear advancement into higher-paying roles",
        "- No credit check where verified",
        "- No upfront payment whenever possible",
        "",
        "**Important:** These are career pathways,",
        "not verified current job vacancies.",
        "Starting wages and eligibility vary by employer.",
        ""
    ]

    for career in CAREER_PATHS:
        query = urlencode({"q": career["search"]})

        lines.extend([
            f"## {career['career']}",
            f"- Industry: {career['sector']}",
            f"- Education: {career['education']}",
            f"- Experience: {career['experience']}",
            f"- Training: {career['training']}",
            f"- Advancement: {career['advancement']}",
            "- Starting salary: Not yet verified",
            "- Current vacancies: Not yet verified",
            "- Credit check: Not yet verified",
            "- Official apprenticeship research: "
            "https://www.apprenticeship.gov/",
            "- Job research: "
            f"https://www.careeronestop.org/",
            f"- Search phrase: {career['search']}",
            ""
        ])

    lines.extend([
        "## Verification checklist",
        "- Confirm a real employer or registered program.",
        "- Verify the application is currently open.",
        "- Confirm starting pay, not just experienced pay.",
        "- Confirm location and entry requirements.",
        "- Confirm training cost and whether wages are paid.",
        "- Confirm any required background or credit checks.",
        "- Never guarantee acceptance or earnings.",
        "",
        "## Future upgrade",
        "Connect live job and apprenticeship sources.",
        "Match candidates by location, education, pay,",
        "experience, training cost, and advancement.",
        ""
    ])

    (REPORTS / "career-elevator-report.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )

    return len(CAREER_PATHS)

def main():
    awards, errors = research_business_awards()
    careers = research_career_paths()

    print("Empire OS - Deal Hunter 2.0 completed")
    print(f"Historical business awards: {awards}")
    print(f"Business retrieval errors: {errors}")
    print(f"Career pathways researched: {careers}")
    print("Reports created:")
    print("- reports/deal-hunter-report.md")
    print("- reports/career-elevator-report.md")

if __name__ == "__main__":
    main()

# ===== EMPIRE OS: GRANT HUNTER 3.0 =====

from urllib.parse import quote

GRANT_SEARCHES = [
    "small business",
    "workforce development",
    "apprenticeship",
    "transportation",
    "construction",
    "healthcare",
    "technology",
    "community development",
    "education",
    "rural development",
    "entrepreneurship"
]

def research_live_grants():
    lines = [
        "# Empire OS - Grant Hunter",
        "",
        "Source: Official Grants.gov search API",
        "Status: Posted or forecasted federal opportunities",
        "",
        "A posted listing is not proof of individual eligibility.",
        "Forecasted opportunities are not yet open.",
        "Deadlines and terms must be confirmed with the funder.",
        ""
    ]

    seen = set()
    errors = 0
    posted = 0
    forecasted = 0

    for keyword in GRANT_SEARCHES:
        payload = {
            "rows": 20,
            "keyword": keyword,
            "oppStatuses": "posted|forecasted"
        }

        result, error = request_json(
            "https://api.grants.gov/v1/api/search2",
            payload
        )

        if error:
            errors += 1
            lines.append(
                f"- Search error for {keyword}: {error}"
            )
            continue

        if result.get("errorcode") != 0:
            errors += 1
            lines.append(
                f"- API error for {keyword}: "
                f"{result.get('msg', 'Unknown')}"
            )
            continue

        hits = (result.get("data") or {}).get("oppHits") or []

        for grant in hits:
            grant_id = grant.get("id")
            if not grant_id or grant_id in seen:
                continue

            seen.add(grant_id)

            status = str(
                grant.get("oppStatus") or "unknown"
            ).lower()

            if status == "posted":
                posted += 1
            elif status == "forecasted":
                forecasted += 1
            else:
                continue

            title = grant.get("title") or "Untitled"
            number = grant.get("number") or "Unknown"
            agency = grant.get("agencyName") or "Unknown"
            close_date = grant.get("closeDate") or "Not listed"

            link = (
                "https://www.grants.gov/search-results-detail/"
                + quote(str(grant_id))
            )

            lines.extend([
                f"## {title}",
                f"- Opportunity number: {number}",
                f"- Agency: {agency}",
                f"- Status: {status}",
                f"- Listed closing date: {close_date}",
                f"- Official listing: {link}",
                "- Funding amount: Verify on official listing",
                "- Eligibility: Not yet verified",
                "- Applicant credit requirements: Not yet verified",
                "- Classification: Federal grant lead",
                ""
            ])

    lines.extend([
        "## Search summary",
        f"- Unique opportunities: {posted + forecasted}",
        f"- Posted: {posted}",
        f"- Forecasted: {forecasted}",
        f"- Search errors: {errors}",
        "",
        "## Future discovery sources",
        "- State and municipal grant portals",
        "- Community foundations",
        "- Private charitable foundations",
        "- Employer workforce-training funds",
        "- Local business competitions",
        "",
        "These additional sources are not yet automated.",
        "Do not claim eligibility or submit applications",
        "without applicant approval."
    ])

    (REPORTS / "grant-hunter-report.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )

    print(
        f"Grant Hunter: {posted} posted, "
        f"{forecasted} forecasted, {errors} errors"
    )


# Run Grant Hunter when this program executes.
research_live_grants()
