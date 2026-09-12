import os

from dotenv import load_dotenv
from openai import OpenAI

from backend.app.schemas.balance_sheet_schema import (
    BalanceSheetExtraction,
)


# =========================================================
# Load environment
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
# Balance Sheet extraction
# =========================================================

def extract_balance_sheet_data(
    ocr_text: str,
) -> BalanceSheetExtraction:

    prompt = f"""
You are a financial document extraction system.

The document type is:

BALANCE SHEET

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

10. Extract EVERY visible financial line item under
    Capital and Liabilities.

11. Extract EVERY visible financial line item under
    Assets.

12. Preserve the original financial line-item names as
    closely as possible.

13. Preserve schedule numbers or references when they
    are explicitly shown.

14. Preserve values for EACH reporting period separately.

15. Do not combine values from different periods.

16. If a financial line item has a value for one period
    but not another, use null for the missing period.

17. Do not calculate missing financial values.

18. Do not infer totals that are not explicitly reported.

19. Do not modify negative values.

20. Parentheses or brackets in financial values indicate
    negative values. Preserve the original representation.

21. Preserve monetary values as strings.

22. Classify every financial row using exactly one of
    these line types:

    ITEM:
        A normal individual financial component.

    SUBTOTAL:
        A subtotal that summarizes several other financial
        rows below or above it.

    TOTAL:
        A final or major total such as Total Assets or
        Total Capital and Liabilities.

    HEADING:
        A section heading that does not represent a
        financial amount.

23. Do NOT classify a row as ITEM if it is a subtotal or
    total.

24. For example, if the document contains:

    Cash
    Investments
    Total Investments

    then:

    Cash -> ITEM
    Investments -> ITEM
    Total Investments -> SUBTOTAL

25. If the document contains:

    Cash
    Investments
    Advances
    Total Assets

    then:

    Cash -> ITEM
    Investments -> ITEM
    Advances -> ITEM
    Total Assets -> TOTAL

26. Do not include a subtotal in the ITEM category merely
    so that it can be used in a component calculation.

27. General document information such as company name,
    report location, report date, auditor information,
    accounting policy references, or report title must NOT
    be represented as financial-period line items.

28. Put general/non-financial information into
    other_information or additional_fields using:

    {{
        "key": "...",
        "value": "..."
    }}

29. Do not use a fake period such as "Information" for
    general information.

30. Do not summarize the document.

31. Do not omit financial rows simply because they appear
    unusual, technical, or difficult to interpret.

32. Return data matching the supplied structured schema.

OCR TEXT
==================================================

{ocr_text}

==================================================
"""

    response = client.responses.parse(
        model="gpt-5.6-luna",
        input=prompt,
        text_format=BalanceSheetExtraction,
    )

    return response.output_parsed
