"""Deterministic parser for structured medical findings and laboratory values."""

import re
from typing import Any, Dict, List, Optional
from app.schemas import ExtractedFinding

# Common laboratory units encountered in clinical reports
# Common laboratory units encountered in clinical reports
KNOWN_UNITS = [
    "g/dL",
    "mg/dL",
    "ug/dL",
    "µg/dL",
    "mcg/dL",
    "mmol/L",
    "umol/L",
    "µmol/L",
    "mEq/L",
    "uIU/mL",
    "µIU/mL",
    "mIU/mL",
    "IU/L",
    "U/L",
    "ng/mL",
    "pg/mL",
    "ng/dL",
    "10^3/uL",
    "10^3/µL",
    "x10^3/uL",
    "x10^3/µL",
    "10^6/uL",
    "10^6/µL",
    "x10^6/uL",
    "x10^6/µL",
    "mL/min/1.73m2",
    "K/uL",
    "M/uL",
    "/uL",
    "/µL",
    "fL",
    "pg",
    "%",
    "mm/hr",
    "sec",
    "seconds",
    "cells/uL",
    "copies/mL",
    "ratio",
    "bpm",
    "mmHg",
]

# Regex pattern for laboratory reference intervals
# Examples: 13.5 - 17.5 | 70-99 | < 200 | <= 100 | > 40 | >= 60 | 0.40 to 4.50 | [4.0-11.0] | (150-450)
REF_RANGE_PATTERN = re.compile(
    r"(?:[\(\[]\s*)?"
    r"(?:(?:<\s*=?|>\s*=?|<=|>=)\s*\d+(?:\.\d+)?|"
    r"\d+(?:\.\d+)?\s*(?:-|–|—|to)\s*\d+(?:\.\d+)?)"
    r"(?:\s*[\)\]])?",
    re.IGNORECASE,
)

# Common clinical flags explicitly written in reports
FLAG_PATTERN = re.compile(
    r"\b(HIGH|LOW|CRITICAL|PANIC|ABNORMAL|NORMAL|ALERT|BORDERLINE|H|L|\*)\b",
    re.IGNORECASE,
)

# Patterns for lines to ignore (headers, footers, panel category titles, facility info, patient metadata lines)
IGNORE_LINE_PATTERNS = [
    re.compile(r"^\s*page\s+\d+", re.IGNORECASE),
    re.compile(r"patient\s*(?:name|id)", re.IGNORECASE),
    re.compile(r"date\s*of\s*birth|dob\b", re.IGNORECASE),
    re.compile(r"(?:ordering\s+)?(?:physician|doctor|provider)\b", re.IGNORECASE),
    re.compile(r"(?:collection|report|specimen|received)\s*date", re.IGNORECASE),
    re.compile(r"laboratory\s*(?:report|pathology|facility|diagnostics)?", re.IGNORECASE),
    re.compile(r"accredited\s+medical", re.IGNORECASE),
    re.compile(r"age\s*(?:\/|\s)\s*sex", re.IGNORECASE),
    re.compile(r"specimen\s*:", re.IGNORECASE),
    re.compile(r"clinical\s*notes?", re.IGNORECASE),
    re.compile(r"test\s+name\s+result", re.IGNORECASE),
    re.compile(r"comments?\s*:", re.IGNORECASE),
    re.compile(r"interpretation\s*:", re.IGNORECASE),
    re.compile(r"^(?:COMPLETE BLOOD COUNT|COMPREHENSIVE METABOLIC PANEL|LIPID PANEL|THYROID FUNCTION):?$", re.IGNORECASE),
    re.compile(r"^[-=_]{4,}$"),  # Horizontal divider lines
]


def extract_report_date(text: str) -> Optional[str]:
    """Extracts reported collection/result date if explicitly specified in report text."""
    date_patterns = [
        r"(?:Report\s*Date|Collection\s*Date|Date\s*of\s*Collection|Date\s*Received|Date)\s*[:\-]?\s*([A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4})",
        r"(?:Report\s*Date|Collection\s*Date|Date\s*of\s*Collection|Date\s*Received|Date)\s*[:\-]?\s*(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})",
        r"(?:Report\s*Date|Collection\s*Date|Date\s*of\s*Collection|Date\s*Received|Date)\s*[:\-]?\s*(\d{4}[/\-\.]\d{1,2}[/\-\.]\d{1,2})",
    ]
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def should_ignore_line(line: str) -> bool:
    """Checks if a line is a known report header, footer, or metadata rather than a test finding."""
    stripped = line.strip()
    if not stripped or len(stripped) < 3:
        return True
    for pat in IGNORE_LINE_PATTERNS:
        if pat.search(stripped):
            return True
    return False


def parse_finding_from_line(line: str, page_number: int = 1) -> Optional[ExtractedFinding]:
    """Attempts to extract a test name, value, unit, reference range, and flag from a single line."""
    if should_ignore_line(line):
        return None

    raw_line = line.strip()

    # Normalize delimiters like pipe '|' or multiple spaces
    parts: List[str]
    if "|" in raw_line:
        parts = [p.strip() for p in raw_line.split("|") if p.strip()]
        if len(parts) >= 2:
            test_name = parts[0]
            val_part = parts[1]
            unit = parts[2] if len(parts) > 2 and not REF_RANGE_PATTERN.search(parts[2]) else None
            ref_idx = 3 if unit else 2
            ref_range = parts[ref_idx] if len(parts) > ref_idx and REF_RANGE_PATTERN.search(parts[ref_idx]) else None
            flag = parts[-1] if len(parts) > ref_idx and FLAG_PATTERN.search(parts[-1]) else None

            # Verify value looks like a measurement or result
            if re.search(r"\d", val_part) or val_part.lower() in ("positive", "negative", "detected", "not detected", "reactive", "non-reactive"):
                return ExtractedFinding(
                    test_name=test_name,
                    value=val_part,
                    unit=unit,
                    reference_range=ref_range,
                    reported_flag=flag.upper() if flag else None,
                    page_number=page_number,
                    source_text=raw_line,
                )

    unit_regex = "|".join([re.escape(u) for u in sorted(KNOWN_UNITS, key=len, reverse=True)])
    combined_pattern = re.compile(
        r"^(?P<name>[A-Za-z0-9\s,\-\(\)\/\.\'\"]+?)"  # Test name
        r"(?::|\s{2,}|\s+)"                             # Separator
        r"(?P<val>[<>]?\s*\d+(?:\.\d+)?|Positive|Negative|Reactive|Non-reactive|Detected|Not\s+Detected)" # Value
        r"(?:\s+(?P<unit>" + unit_regex + r"))?"       # Unit (optional)
        r"(?:\s+(?P<ref>(?:[\(\[]\s*)?(?:<\s*=?|>\s*=?|<=|>=|\d+(?:\.\d+)?\s*(?:-|–|—|to))\s*\d*(?:\.\d+)?(?:\s*[\)\]])?))?" # Ref range (optional)
        r"(?:\s+(?P<flag>HIGH|LOW|CRITICAL|ABNORMAL|NORMAL|ALERT|H|L|\*))?", # Explicit flag (optional)
        re.IGNORECASE,
    )

    match = combined_pattern.match(raw_line)
    if match:
        data = match.groupdict()
        test_name = data["name"].strip(" :,-")
        val = data["val"].strip()

        # Sanity check: test name should be reasonable length and not purely numeric
        if len(test_name) < 2 or test_name.isdigit() or len(test_name) > 60:
            return None

        unit = data.get("unit")
        ref = data.get("ref")
        flag = data.get("flag")

        # Ref range cleanup
        if ref:
            ref = ref.strip("[]() ")
            if not ref:
                ref = None

        return ExtractedFinding(
            test_name=test_name,
            value=val,
            unit=unit.strip() if unit else None,
            reference_range=ref,
            reported_flag=flag.strip().upper() if flag else None,
            page_number=page_number,
            source_text=raw_line,
        )

    return None


def extract_findings_from_pages(pages: List[Dict[str, Any]]) -> List[ExtractedFinding]:
    """Parses structured findings across all pages of a report.

    Args:
        pages: List of page objects containing 'page_number' and 'text'.

    Returns:
        List of deduplicated, validated ExtractedFinding instances.
    """
    findings: List[ExtractedFinding] = []
    seen_signatures = set()

    for page in pages:
        p_num = page.get("page_number", 1)
        text = page.get("text", "")
        lines = text.split("\n")

        for line in lines:
            finding = parse_finding_from_line(line, page_number=p_num)
            if finding:
                # Deduplication signature based on test name and value on the same page
                sig = (finding.test_name.lower(), finding.value.lower(), finding.page_number)
                if sig not in seen_signatures:
                    seen_signatures.add(sig)
                    findings.append(finding)

    return findings
