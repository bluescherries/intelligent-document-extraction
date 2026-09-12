from decimal import Decimal
from pathlib import Path

from backend.app.services.ocr_service import extract_text

from backend.app.services.cash_flow_extraction_service import (
    extract_cash_flow_data,
)

from backend.app.services.cash_flow_validation_service import (
    validate_cash_flow,
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

cash_flow = extract_cash_flow_data(
    ocr_text
)


# =========================================================
# Financial validation
# =========================================================

result = validate_cash_flow(
    cash_flow,
    tolerance=Decimal("0.01"),
)


# =========================================================
# Display result
# =========================================================

print("=" * 70)
print("CASH FLOW FINANCIAL VALIDATION")
print("=" * 70)

print(
    f"\nOverall status: "
    f"{result['overall_status']}"
)

print(
    f"Tolerance: "
    f"{result['tolerance']}"
)


for validation in result["validations"]:

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