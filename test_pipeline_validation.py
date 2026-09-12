from pathlib import Path

from backend.app.services.document_validation_service import (
    validate_document,
)


# =========================================================
# Test document
# =========================================================

file_path = Path("test_data/invoice.jpg")

file_bytes = file_path.read_bytes()


# =========================================================
# Run document validation
# =========================================================

result = validate_document(
    file_bytes=file_bytes,
    filename=file_path.name,
    content_type="image/jpeg",
)


# =========================================================
# Display result
# =========================================================

print("=" * 70)
print("DOCUMENT VALIDATION RESULT")
print("=" * 70)

print()

print(result)

print()

print("=" * 70)
print("VALIDATION STATUS")
print("=" * 70)

print(
    "Status:",
    result.get("status")
)

print(
    "Reason:",
    result.get("reason")
)

print(
    "Message:",
    result.get("message")
)