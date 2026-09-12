from backend.app.schemas.balance_sheet_schema import (
    BalanceSheetExtraction,
)


result = BalanceSheetExtraction(
    statement_title="CONSOLIDATED BALANCE SHEET",
    statement_date="As at March 31, 2026",
    currency="crore",

    periods=[
        "March 31, 2026",
        "March 31, 2025",
    ],
)

print(
    result.model_dump_json(
        indent=2
    )
)