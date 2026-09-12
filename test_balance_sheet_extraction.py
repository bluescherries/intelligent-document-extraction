from pathlib import Path

from backend.app.services.ocr_service import extract_text
from backend.app.services.balance_sheet_extraction_service import (
    extract_balance_sheet_data,
)


# ---------------------------------------------------------
# Select Balance Sheet sample
# ---------------------------------------------------------

file_path = Path(
    "test_data/balance_sheet.pdf"
)


# ---------------------------------------------------------
# Read file
# ---------------------------------------------------------

file_bytes = file_path.read_bytes()


# ---------------------------------------------------------
# OCR
# ---------------------------------------------------------

pages = extract_text(
    file_bytes=file_bytes,
    filename=file_path.name,
)


# ---------------------------------------------------------
# Combine OCR text
# ---------------------------------------------------------

ocr_text = "\n\n".join(
    page["text"]
    for page in pages
)


# ---------------------------------------------------------
# Display OCR
# ---------------------------------------------------------

print("=" * 70)

print("BALANCE SHEET OCR TEXT")

print("=" * 70)

print(ocr_text)


# ---------------------------------------------------------
# AI extraction
# ---------------------------------------------------------

print("\n")

print("=" * 70)

print("BALANCE SHEET STRUCTURED AI EXTRACTION")

print("=" * 70)


result = extract_balance_sheet_data(
    ocr_text
)


# ---------------------------------------------------------
# Display structured JSON
# ---------------------------------------------------------

print(
    result.model_dump_json(
        indent=2
    )
)