from pathlib import Path

from backend.app.services.ocr_service import extract_text

from backend.app.services.cash_flow_extraction_service import (
    extract_cash_flow_data,
)


# =========================================================
# Select the same Cash Flow document
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
# Periods
# =========================================================

print("=" * 70)
print("PERIODS")
print("=" * 70)

for period in result.periods:
    print(period)


# =========================================================
# Operating activities
# =========================================================

print("\n")
print("=" * 70)
print("OPERATING ACTIVITIES")
print("=" * 70)

for item in result.operating_activities:

    print(f"\n{item.name}")

    print(
        f"Type: {item.line_type}"
    )

    print(
        f"Schedule: {item.schedule}"
    )

    for value in item.values:

        print(
            f"  {value.period}: "
            f"{value.value}"
        )


# =========================================================
# Investing activities
# =========================================================

print("\n")
print("=" * 70)
print("INVESTING ACTIVITIES")
print("=" * 70)

for item in result.investing_activities:

    print(f"\n{item.name}")

    print(
        f"Type: {item.line_type}"
    )

    print(
        f"Schedule: {item.schedule}"
    )

    for value in item.values:

        print(
            f"  {value.period}: "
            f"{value.value}"
        )


# =========================================================
# Financing activities
# =========================================================

print("\n")
print("=" * 70)
print("FINANCING ACTIVITIES")
print("=" * 70)

for item in result.financing_activities:

    print(f"\n{item.name}")

    print(
        f"Type: {item.line_type}"
    )

    print(
        f"Schedule: {item.schedule}"
    )

    for value in item.values:

        print(
            f"  {value.period}: "
            f"{value.value}"
        )


# =========================================================
# Cash reconciliation
# =========================================================

print("\n")
print("=" * 70)
print("CASH RECONCILIATION")
print("=" * 70)

for item in result.cash_reconciliation:

    print(f"\n{item.name}")

    print(
        f"Type: {item.line_type}"
    )

    print(
        f"Schedule: {item.schedule}"
    )

    for value in item.values:

        print(
            f"  {value.period}: "
            f"{value.value}"
        )