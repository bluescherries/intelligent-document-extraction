from pathlib import Path

from backend.app.services.ocr_service import extract_text

from backend.app.services.profit_loss_extraction_service import (
    extract_profit_loss_data,
)


# =========================================================
# Select the P&L document
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
# Display OCR
# =========================================================

print("=" * 70)
print("PROFIT & LOSS OCR TEXT")
print("=" * 70)

print(ocr_text)


# =========================================================
# AI extraction
# =========================================================

print("\n")
print("=" * 70)
print("PROFIT & LOSS STRUCTURED AI EXTRACTION")
print("=" * 70)


result = extract_profit_loss_data(
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