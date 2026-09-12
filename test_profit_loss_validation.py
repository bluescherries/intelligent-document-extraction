from pathlib import Path

from backend.app.services.ocr_service import extract_text

from backend.app.services.profit_loss_extraction_service import (
    extract_profit_loss_data,
)

from backend.app.services.profit_loss_validation_service import (
    validate_profit_loss,
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

profit_loss = extract_profit_loss_data(
    ocr_text
)


# =========================================================
# Financial validation
# =========================================================

validation_result = validate_profit_loss(
    profit_loss
)


# =========================================================
# Display results
# =========================================================

print("=" * 70)
print("PROFIT & LOSS FINANCIAL VALIDATION")
print("=" * 70)

print(
    f"\nOverall status: "
    f"{validation_result['overall_status']}"
)

print(
    f"Tolerance: "
    f"{validation_result['tolerance']}"
)


for validation in validation_result["validations"]:

    print("\n" + "-" * 70)

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
        f"Inputs: "
        f"{validation['inputs']}"
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