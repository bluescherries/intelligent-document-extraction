from io import BytesIO

import cv2
import fitz
import numpy as np
import pytesseract
from PIL import Image, ImageEnhance


def preprocess_image(image: Image.Image) -> Image.Image:
    """
    Light preprocessing for scanned documents.
    """

    # Convert PIL image to OpenCV format
    image_array = np.array(image)

    # Convert RGB to grayscale
    gray = cv2.cvtColor(
        image_array,
        cv2.COLOR_RGB2GRAY,
    )

    # Upscale image
    gray = cv2.resize(
        gray,
        None,
        fx=2,
        fy=2,
        interpolation=cv2.INTER_CUBIC,
    )

    # Convert back to PIL
    processed = Image.fromarray(gray)

    # Slightly improve contrast
    enhancer = ImageEnhance.Contrast(processed)
    processed = enhancer.enhance(1.5)

    return processed


def run_tesseract(image: Image.Image) -> str:
    """
    Run Tesseract OCR on an image.
    """

    text = pytesseract.image_to_string(
        image,
        config="--psm 11",
    )

    return text.strip()


def extract_text_from_image(
    file_bytes: bytes,
    filename: str,
) -> list[dict]:

    image = Image.open(
        BytesIO(file_bytes)
    )

    processed_image = preprocess_image(
        image
    )

    text = run_tesseract(
        processed_image
    )

    return [
        {
            "page_number": 1,
            "text": text,
        }
    ]


def extract_text_from_pdf(
    file_bytes: bytes,
) -> list[dict]:

    document = fitz.open(
        stream=file_bytes,
        filetype="pdf",
    )

    pages = []

    for page_number, page in enumerate(
        document,
        start=1,
    ):

        # First try native PDF text
        text = page.get_text("text").strip()

        # If PDF has no text, use OCR
        if not text:

            pixmap = page.get_pixmap(
                matrix=fitz.Matrix(2, 2)
            )

            image = Image.frombytes(
                "RGB",
                [
                    pixmap.width,
                    pixmap.height,
                ],
                pixmap.samples,
            )

            processed_image = preprocess_image(
                image
            )

            text = run_tesseract(
                processed_image
            )

        pages.append(
            {
                "page_number": page_number,
                "text": text,
            }
        )

    document.close()

    return pages


def extract_text(
    file_bytes: bytes,
    filename: str,
) -> list[dict]:

    filename_lower = filename.lower()

    if filename_lower.endswith(".pdf"):

        return extract_text_from_pdf(
            file_bytes
        )

    if filename_lower.endswith(
        (".jpg", ".jpeg", ".png")
    ):

        return extract_text_from_image(
            file_bytes,
            filename,
        )

    raise ValueError(
        "Unsupported file type. "
        "Only PDF / JPG / PNG are supported."
    )