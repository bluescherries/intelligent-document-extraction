from pathlib import Path

from backend.app.services.ocr_service import extract_text


file_path = Path("test_data/invoice.jpg")

file_bytes = file_path.read_bytes()

pages = extract_text(
    file_bytes=file_bytes,
    filename=file_path.name,
)

for page in pages:

    print("=" * 60)
    print(f"PAGE {page['page_number']}")
    print("=" * 60)

    print(page["text"])