from pathlib import Path

from backend.app.services.document_processing_service import (
    process_document,
)


# =========================================================
# Test document
# =========================================================

file_path = Path(
    "test_data/invoice.jpg"
)


# =========================================================
# Read file
# =========================================================

file_bytes = file_path.read_bytes()


# =========================================================
# Process document
# =========================================================

result = process_document(
    file_bytes=file_bytes,
    filename=file_path.name,
    document_type="INVOICE",
)


# =========================================================
# Display result
# =========================================================

print("=" * 70)
print("END-TO-END DOCUMENT PIPELINE")
print("=" * 70)

print()

print("Document name:")
print(result["document_name"])

print()

print("Document type:")
print(result["document_type"])

print()

print("Status:")
print(result["status"])

print()

print("EXTRACTED DATA")
print("-" * 70)

print(
    result["extracted_data"]
)

print()

print("FINANCIAL VALIDATION")
print("-" * 70)

print(
    result["financial_validation"]
)

print()

print("DATABASE ID:")
print(
    result.get("id")
)

print()

print("=" * 70)
print("END-TO-END PIPELINE TEST COMPLETED")
print("=" * 70)