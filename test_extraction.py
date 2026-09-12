from pathlib import Path

from backend.app.services.ocr_service import extract_text
from backend.app.services.extraction_service import extract_invoice_data
from backend.app.services.financial_validation_service import validate_invoice


file_path = Path("test_data/invoice.jpg")
file_bytes = file_path.read_bytes()


# ---------------------------------------------------------
# OCR
# ---------------------------------------------------------

pages = extract_text(
    file_bytes=file_bytes,
    filename=file_path.name
)

ocr_text = "\n\n".join(
    page["text"]
    for page in pages
)


print("=" * 70)
print("OCR TEXT")
print("=" * 70)

print(ocr_text)


# ---------------------------------------------------------
# AI EXTRACTION
# ---------------------------------------------------------

print("\n")
print("=" * 70)
print("STRUCTURED AI EXTRACTION")
print("=" * 70)

result = extract_invoice_data(ocr_text)

print(
    result.model_dump_json(
        indent=2
    )
)


# ---------------------------------------------------------
# FINANCIAL VALIDATION
# ---------------------------------------------------------

print("\n")
print("=" * 70)
print("FINANCIAL VALIDATION")
print("=" * 70)

validation_result = validate_invoice(result)

print(validation_result)