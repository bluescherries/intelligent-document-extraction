from io import BytesIO
from pathlib import Path

import fitz
from PIL import Image


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
}

MAX_PAGES = 3


def validate_document(
    file_bytes: bytes,
    filename: str,
    content_type: str | None = None,
) -> dict:

    # 1. Check if the uploaded file is empty
    if not file_bytes:
        return {
            "status": "FAILED",
            "reason": "EMPTY_FILE",
            "message": "The uploaded file is empty.",
        }

    # 2. Check the file extension
    extension = Path(filename).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        return {
            "status": "FAILED",
            "reason": "UNSUPPORTED_FILE_TYPE",
            "message": "Only PDF / JPG / PNG documents are supported.",
        }

    # 3. Validate PDF files
    if extension == ".pdf":

        try:
            document = fitz.open(
                stream=file_bytes,
                filetype="pdf",
            )

            page_count = len(document)

            if page_count == 0:
                document.close()

                return {
                    "status": "FAILED",
                    "reason": "EMPTY_PDF",
                    "message": "The PDF contains no pages.",
                }

            if page_count > MAX_PAGES:
                document.close()

                return {
                    "status": "FAILED",
                    "reason": "PAGE_LIMIT_EXCEEDED",
                    "message": "The PDF exceeds the 3-page limit.",
                    "page_count": page_count,
                }

            document.close()

            return {
                "file_type": content_type or "application/pdf",
                "is_supported": True,
                "is_readable": True,
                "page_count": page_count,
                "status": "PASS",
            }

        except Exception:

            return {
                "status": "FAILED",
                "reason": "CORRUPTED_FILE",
                "message": "The PDF could not be read.",
            }

    # 4. Validate JPG / PNG files
    try:

        image = Image.open(BytesIO(file_bytes))

        image.verify()

        return {
            "file_type": content_type or "image",
            "is_supported": True,
            "is_readable": True,
            "page_count": 1,
            "status": "PASS",
        }

    except Exception:

        return {
            "status": "FAILED",
            "reason": "CORRUPTED_FILE",
            "message": "The image could not be read.",
        }