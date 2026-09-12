from pathlib import Path

from backend.app.services.ocr_service import extract_text

from backend.app.services.balance_sheet_extraction_service import (
    extract_balance_sheet_data,
)

from backend.app.services.balance_sheet_validation_service import (
    validate_balance_sheet,
)


# =========================================================
# Select the real Balance Sheet
# =========================================================

file_path = Path(
    "test_data/balance_sheet.pdf"
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

print("=" * 70)
print("BALANCE SHEET AI EXTRACTION")
print("=" * 70)

balance_sheet = extract_balance_sheet_data(
    ocr_text
)


print(
    balance_sheet.model_dump_json(
        indent=2
    )
)


# =========================================================
# Financial validation
# =========================================================

print("\n")
print("=" * 70)
print("BALANCE SHEET FINANCIAL VALIDATION")
print("=" * 70)


validation_result = validate_balance_sheet(
    balance_sheet
)


print()

print(
    f"Overall status: "
    f"{validation_result['overall_status']}"
)


# =========================================================
# Display validations
# =========================================================

for validation in validation_result["validations"]:

    print("-" * 70)

    print(
        f"Period: "
        f"{validation['period']}"
    )

    print(
        f"Validation: "
        f"{validation['validation']}"
    )

    print(
        f"Formula: "
        f"{validation['formula']}"
    )

    print(
        f"Calculated: "
        f"{validation['calculated']}"
    )

    print(
        f"Reported: "
        f"{validation['reported']}"
    )

    print(
        f"Variance: "
        f"{validation['variance']}"
    )

    print(
        f"Status: "
        f"{validation['status']}"
    )