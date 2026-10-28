
import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# Empire OS — Scout Research Worker
# Source: Federal Register public API
# No API key or paid service required.

INDUSTRIES = {
    "Freight & Trucking": "freight transportation",
    "Medical & Healthcare": "medical transportation",
    "Construction": "construction contracts",
    "Staffing & Labor": "workforce development",
    "Cleaning & Maintenance": "facility maintenance",
    "Technology & AI": "artificial intelligence",
    "Government Contracting": "federal procurement",
    "Other Business": "small business",
}

API = "https://www.federalregister.gov/api/v1/documents.json"
reports = []
errors = []

for industry, search_term in INDUSTRIES.items():
    params = urllib.parse.urlencode({
        "conditions[term]": search_term,
        "per_page": 5,
        "order": "newest",
    })

    url = f"{API}?{params}"

    try:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "EmpireOS-Scout/1.0"}
        )

        with urllib.request.urlopen(request, timeout=20) as response:
            data = json.load(response)

        items = []

        for document in data.get("results", []):
            items.append({
                "title": document.get("title", "Untitled"),
                "date": document.get("publication_date", "Unknown"),
                "type": document.get("type", "Unknown"),
                "url": document.get("html_url", ""),
            })

        reports.append({
            "industry": industry,
            "search_term": search_term,
            "results": items,
        })

    except Exception as error:
        errors.append(f"{industry}: {error}")
        reports.append({
            "industry": industry,
            "search_term": search_term,
            "results": [],
        })

Path("reports").mkdir(exist_ok=True)

timestamp = datetime.now(timezone.utc).strftime(
    "%Y-%m-%d %H:%M UTC"
)

lines = [
    "# Empire OS — Scout Research Report",
    "",
    f"Generated: {timestamp}",
    "",
    "Source: Federal Register public API",
    "",
    "**Important:** These are federal notices and market",
    "research signals, NOT verified open contracts or loads.",
    "Availability, eligibility, deadlines, and potential",
    "revenue must be checked separately.",
    "",
]

for group in reports:
    lines.append(f"## {group['industry']}")
    lines.append("")

    if not group["results"]:
        lines.append("No results retrieved.")
        lines.append("")
        continue

    for item in group["results"]:
        lines.append(f"### {item['title']}")
        lines.append(f"- Published: {item['date']}")
        lines.append(f"- Document type: {item['type']}")
        lines.append(f"- Source: {item['url']}")
        lines.append("")

if errors:
    lines.append("## Retrieval Errors")
    lines.append("")
    lines.extend(f"- {error}" for error in errors)

Path("reports/scout-report.md").write_text(
    "\n".join(lines),
    encoding="utf-8",
)

print("Scout research report created.")
print(f"Industries checked: {len(reports)}")
print(f"Retrieval errors: {len(errors)}")
