import os

from dotenv import load_dotenv
from openai import OpenAI

from backend.app.schemas.profit_loss_schema import (
    ProfitLossExtraction,
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
# Profit & Loss extraction
# =========================================================

def extract_profit_loss_data(
    ocr_text: str,
) -> ProfitLossExtraction:

    prompt = f"""
You are a financial document extraction system.

The document type is:

PROFIT AND LOSS STATEMENT

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
    the income section.

11. Extract EVERY visible financial line item under
    the expenditure section.

12. Extract EVERY visible financial line item related
    to profit, loss, minority interest, and
    appropriations.

13. Preserve the original financial line-item names
    as closely as possible.

14. Preserve schedule numbers or references when they
    are explicitly shown.

15. Preserve values for EACH reporting period
    separately.

16. Do not combine values from different periods.

17. If a financial line item has a value for one period
    but not another, use null for the missing period.

18. Do not calculate missing financial values.

19. Do not infer totals that are not explicitly
    reported.

20. Preserve negative values exactly as represented
    where possible.

21. Parentheses or brackets around financial values
    indicate negative values. Preserve this meaning.

22. Preserve monetary values as strings.

23. Classify every financial row using exactly one of
    these line types:

    ITEM:
        A normal individual financial component.

    SUBTOTAL:
        A subtotal that summarizes several other
        financial rows.

    TOTAL:
        A final or major total such as Total Income,
        Total Expenditure, or a final profit/loss total.

    HEADING:
        A section heading that does not represent a
        financial amount.

24. Do NOT classify a subtotal or total as ITEM.

25. For example:

    Interest earned
    Other income
    Total income

    should normally be classified as:

    Interest earned -> ITEM
    Other income -> ITEM
    Total income -> TOTAL

26. If the document contains intermediate subtotals,
    classify them as SUBTOTAL.

27. Do not include the same financial amount twice merely
    because it appears in a subtotal and in its underlying
    components.

28. General document information such as company name,
    report location, report date, auditor information,
    accounting policy references, or report title must
    NOT be represented as financial-period line items.

29. Put general/non-financial information into
    other_information or additional_fields using:

    {{
        "key": "...",
        "value": "..."
    }}

30. Do not use a fake period such as "Information" for
    general information.

31. Do not summarize the document.

32. Do not omit financial rows simply because they appear
    unusual, technical, or difficult to interpret.

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
        text_format=ProfitLossExtraction,
    )

    return response.output_parsed