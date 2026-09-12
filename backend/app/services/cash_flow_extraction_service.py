import os

from dotenv import load_dotenv
from openai import OpenAI

from backend.app.schemas.cash_flow_schema import (
    CashFlowExtraction,
)


# =========================================================
# Load environment variables
# =========================================================

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError(
        "OPENAI_API_KEY was not found in .env"
    )


# =========================================================
# OpenAI client
# =========================================================

client = OpenAI(
    api_key=api_key
)


# =========================================================
# Cash Flow extraction
# =========================================================

def extract_cash_flow_data(
    ocr_text: str,
) -> CashFlowExtraction:

    prompt = f"""
You are a financial document extraction system.

The document type is:

CASH FLOW STATEMENT

Extract information ONLY from the OCR text provided
below.

IMPORTANT RULES:

1. Extract ONLY information explicitly present in the
   OCR text.

2. NEVER invent information.

3. NEVER guess missing values.

4. If a value cannot be determined from the OCR text,
   return null.

5. Extract ALL meaningful information visible in the
   document.

6. Extract the statement title when present.

7. Extract the statement date or reporting date when
   present.

8. Extract the currency, unit, or denomination when
   present.

9. Extract ALL reporting periods shown in the financial
   tables.

10. Preserve each reporting period separately.

11. Extract EVERY visible line item under operating
    activities.

12. Extract EVERY visible line item under investing
    activities.

13. Extract EVERY visible line item under financing
    activities.

14. Extract cash and cash-equivalent reconciliation
    information.

15. Preserve the original names of financial line items
    as closely as possible.

16. Preserve schedule references when explicitly shown.

17. Do not combine values from different periods.

18. If a row has a value for one period but not another,
    use null for the missing period.

19. Do not calculate missing financial values.

20. Do not infer totals that are not explicitly reported.

21. Preserve negative values.

22. Parentheses around a financial value represent a
    negative amount. Preserve that meaning in the
    extracted string.

23. Classify each financial row using exactly one of:

    ITEM
        Individual cash flow component.

    SUBTOTAL
        Intermediate subtotal.

    TOTAL
        Major or final total.

    HEADING
        Section heading without a financial amount.

24. Do not classify section headings as ITEM.

25. Preserve rows such as:

    Net cash from operating activities
    Net cash used in investing activities
    Net cash from financing activities
    Effect of foreign exchange rate changes
    Net increase / decrease in cash
    Cash and cash equivalents at beginning of year
    Cash and cash equivalents at end of year

    whenever they are present.

26. Do not assume that a missing activity category has
    a value of zero.

27. If a required value is absent, preserve it as null.

28. General document information such as company name,
    report location, report date, auditor information,
    accounting policies, and report references should
    NOT be represented as financial-period rows.

29. Put general information into other_information or
    additional_fields as:

    {{
        "key": "...",
        "value": "..."
    }}

30. Do NOT use a fake period such as "Information".

31. Do not summarize the document.

32. Do not omit unusual or technical cash flow rows.

33. Extract all meaningful visible information that can
    be reliably obtained from the OCR.

34. Return data matching the supplied structured schema.

OCR TEXT
==================================================

{ocr_text}

==================================================
"""

    response = client.responses.parse(
        model="gpt-5.6-luna",
        input=prompt,
        text_format=CashFlowExtraction,
    )

    return response.output_parsed