import os

from dotenv import load_dotenv
from openai import OpenAI

from backend.app.schemas.invoice_schema import (
    InvoiceExtraction,
)


load_dotenv()


api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError(
        "OPENAI_API_KEY was not found in .env"
    )


client = OpenAI(
    api_key=api_key
)


def extract_invoice_data(
    ocr_text: str,
) -> InvoiceExtraction:
    """
    Extract structured invoice information
    from OCR text using OpenAI.
    """

    prompt = f"""
You are a financial document extraction system.

The document type is INVOICE.

Extract information ONLY from the OCR text below.

IMPORTANT RULES:

1. Extract only information explicitly present
   in the OCR text.
2. Never invent information.
3. Never guess a missing value.
4. If a value is not available, return null.
5. Preserve all meaningful invoice information.
6. Extract every visible line item.
7. Preserve quantities, units, prices, taxes,
   and totals when available.
8. Preserve seller and client information.
9. Preserve addresses and tax IDs.
10. Preserve payment information.
11. Preserve additional meaningful information
    that does not fit the standard fields.
12. Do not perform financial calculations to
    create missing values.
13. Keep monetary values as strings so that the
    original formatting is not lost.

OCR TEXT
--------------------
{ocr_text}
--------------------
"""

    response = client.responses.parse(
        model="gpt-5.6-luna",
        input=prompt,
        text_format=InvoiceExtraction,
    )

    return response.output_parsed