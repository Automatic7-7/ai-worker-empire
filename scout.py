

# Empire OS — Scout 2.0
# Public-source research and investigative signals
# Uses Python's built-in libraries only.

import json
import re
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

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

SIGNALS = {
    "Potential procurement signal": [
        "request for proposals",
        "request for information",
        "sources sought",
        "contract opportunity",
        "solicitation",
    ],
    "Expansion or demand signal": [
        "expansion",
        "new facility",
        "infrastructure",
        "capacity",
        "development",
    ],
    "Regulatory or market signal": [
        "regulation",
        "proposed rule",
        "final rule",
        "compliance",
        "standards",
    ],
}

def fetch_json(url):
    """Retry temporary network failures."""
    last_error = None

    for attempt in range(3):
        try:
            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "EmpireOS-Scout/2.0",
                    "Accept": "application/json",
                },
            )
            with urllib.request.urlopen(
                request, timeout=25
            ) as response:
                return json.load(response)
        except Exception as error:
            last_error = error
            if attempt < 2:
                time.sleep(2 * (attempt + 1))

    raise RuntimeError(str(last_error))

def classify(title, document_type):
    text = f"{title} {document_type}".lower()

    for category, keywords in SIGNALS.items():
        if any(word in text for word in keywords):
            return category

    return "General research notice"

def safe_link(url):
    """Accept only links to the official source."""
    parsed = urllib.parse.urlparse(url)

    return (
        parsed.scheme == "https"
        and parsed.hostname == "www.federalregister.gov"
    )

def investigate(item):
    title = item["title"]
    category = classify(title, item["type"])

    questions = [
        "Does this notice describe a real purchasing need?",
        "Is there an active solicitation or deadline?",
        "Who is authorized to provide the service?",
        "Could a lawful introduction or agency service earn a fee?",
    ]

    if category == "Expansion or demand signal":
        hypothesis = (
            "This development may create future supplier "
            "or service demand. Further evidence is required."
        )
    elif category == "Potential procurement signal":
        hypothesis = (
            "This may point toward procurement activity. "
            "An active opportunity has not been verified."
        )
    else:
        hypothesis = (
            "Background intelligence only; no commercial "
            "opportunity has been established."
        )

    return category, hypothesis, questions

def main():
    Path("reports").mkdir(exist_ok=True)

    now = datetime.now(timezone.utc).strftime(
        "%Y-%m-%d %H:%M UTC"
    )

    report = [
        "# Empire OS — Scout 2.0 Research",
        "",
        f"Generated: {now}",
        "",
        "Source: Federal Register public API",
        "",
        "Findings are public notices, not verified",
        "open contracts, available loads, or paying clients.",
        "",
    ]

    radar = [
        "# Empire OS — Radar Investigation Brief",
        "",
        f"Generated: {now}",
        "",
        "These are automated research hypotheses.",
        "They are not verified predictions.",
        "",
    ]

    seen = set()
    errors = []
    unique_count = 0
    duplicate_count = 0

    for industry, term in INDUSTRIES.items():
        report.extend(["", f"## {industry}", ""])

        params = urllib.parse.urlencode({
            "conditions[term]": term,
            "per_page": 10,
            "order": "newest",
        })

        try:
            data = fetch_json(f"{API}?{params}")
            documents = data.get("results", [])

            if not documents:
                report.append("No notices returned.")

            for document in documents:
                title = document.get("title", "Untitled")
                link = document.get("html_url", "")
                doc_type = document.get("type", "Unknown")
                published = document.get(
                    "publication_date", "Unknown"
                )

                if not safe_link(link):
                    continue

                if link in seen:
                    duplicate_count += 1
                    continue

                seen.add(link)
                unique_count += 1

                category, hypothesis, questions = (
                    investigate({
                        "title": title,
                        "type": doc_type,
                    })
                )

                report.extend([
                    f"### {title}",
                    f"- Industry search: {industry}",
                    f"- Published: {published}",
                    f"- Type: {doc_type}",
                    f"- Classification: {category}",
                    f"- Source: {link}",
                    "",
                ])

                if category != "General research notice":
                    radar.extend([
                        f"## {title}",
                        f"- Industry: {industry}",
                        f"- Signal: {category}",
                        f"- Hypothesis: {hypothesis}",
                        f"- Original source: {link}",
                        "- Verification: Not independently confirmed",
                        "",
                        "### Questions to investigate",
                    ])
                    radar.extend(
                        f"- {question}" for question in questions
                    )
                    radar.append("")

        except Exception as error:
            errors.append(f"{industry}: {error}")
            report.append("Research retrieval failed.")

    summary = [
        "",
        "## Research Summary",
        f"- Industries searched: {len(INDUSTRIES)}",
        f"- Unique notices: {unique_count}",
        f"- Duplicate notices removed: {duplicate_count}",
        f"- Retrieval errors: {len(errors)}",
        "- Verified open contracts: Not checked",
        "- Verified available freight loads: Not checked",
        "- Verified paying clients: Not checked",
        "",
    ]

    if errors:
        summary.append("## Errors")
        summary.extend(f"- {error}" for error in errors)

    report.extend(summary)
    radar.extend(summary)

    Path("reports/scout-report.md").write_text(
        "\n".join(report), encoding="utf-8"
    )

    Path("reports/radar-report.md").write_text(
        "\n".join(radar), encoding="utf-8"
    )

    print("Scout 2.0 research completed.")
    print(f"Industries checked: {len(INDUSTRIES)}")
    print(f"Unique notices: {unique_count}")
    print(f"Duplicates removed: {duplicate_count}")
    print(f"Retrieval errors: {len(errors)}")
    print("Scout and Radar reports created.")

if __name__ == "__main__":
    main()
