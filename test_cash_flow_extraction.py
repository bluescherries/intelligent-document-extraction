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
# Display OCR
# =========================================================

print("=" * 70)
print("CASH FLOW OCR TEXT")
print("=" * 70)

print(ocr_text)


# =========================================================
# AI extraction
# =========================================================

print("\n")
print("=" * 70)
print("CASH FLOW STRUCTURED AI EXTRACTION")
print("=" * 70)

result = extract_cash_flow_data(
    ocr_text
)


# =========================================================
# Display structured result
# =========================================================

print(
    result.model_dump_json(
        indent=2
    )
)