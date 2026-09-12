from pathlib import Path

from backend.app.services.ocr_service import extract_text
from backend.app.services.cash_flow_extraction_service import (
    extract_cash_flow_data,
)


# =========================================================
# Select Cash Flow document
# =========================================================

file_path = Path(
    "test_data/cash_flow.pdf"
)


# =========================================================
# Read document
# =========================================================

file_bytes = file_path.read_bytes()


# =========================================================
# OCR
# =========================================================

pages = extract_text(
    file_bytes=file_bytes,
    filename=file_path.name,
)

ocr_text = "\n\n".join(
    page["text"]
    for page in pages
)


# =========================================================
# AI extraction
# =========================================================

result = extract_cash_flow_data(
    ocr_text
)


# =========================================================
# Helper function
# =========================================================

def print_totals(title, items):

    print("\n")
    print("=" * 70)
    print(title)
    print("=" * 70)

    for item in items:

        if item.line_type == "TOTAL":

            print(f"\n{item.name}")

            for value in item.values:

                print(
                    f"  {value.period}: "
                    f"{value.value}"
                )


# =========================================================
# Operating totals
# =========================================================

print_totals(
    "OPERATING ACTIVITY TOTALS",
    result.operating_activities,
)


# =========================================================
# Investing totals
# =========================================================

print_totals(
    "INVESTING ACTIVITY TOTALS",
    result.investing_activities,
)


# =========================================================
# Financing totals
# =========================================================

print_totals(
    "FINANCING ACTIVITY TOTALS",
    result.financing_activities,
)


# =========================================================
# Cash reconciliation totals
# =========================================================

print_totals(
    "CASH RECONCILIATION TOTALS",
    result.cash_reconciliation,
)
