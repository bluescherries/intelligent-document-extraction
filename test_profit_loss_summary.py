from pathlib import Path

from backend.app.services.ocr_service import extract_text

from backend.app.services.profit_loss_extraction_service import (
    extract_profit_loss_data,
)


# =========================================================
# Select the same P&L document
# =========================================================

file_path = Path(
    "test_data/profit_loss_2017.pdf"
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

result = extract_profit_loss_data(
    ocr_text
)


# =========================================================
# Print periods
# =========================================================

print("=" * 70)
print("PERIODS")
print("=" * 70)

for period in result.periods:
    print(period)


# =========================================================
# Print Income
# =========================================================

print("\n")
print("=" * 70)
print("INCOME")
print("=" * 70)

for item in result.income:

    print(
        f"\n{item.name}"
    )

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
# Print Expenditure
# =========================================================

print("\n")
print("=" * 70)
print("EXPENDITURE")
print("=" * 70)

for item in result.expenditure:

    print(
        f"\n{item.name}"
    )

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
# Print Profit / Appropriations
# =========================================================

print("\n")
print("=" * 70)
print("PROFIT AND APPROPRIATIONS")
print("=" * 70)

for item in result.profit_and_appropriations:

    print(
        f"\n{item.name}"
    )

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