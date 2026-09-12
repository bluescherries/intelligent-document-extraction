from decimal import Decimal

from backend.app.schemas.balance_sheet_schema import (
    BalanceSheetExtraction,
    BalanceSheetLineItem,
    BalanceSheetPeriodValue,
)

from backend.app.services.balance_sheet_validation_service import (
    validate_balance_sheet,
)


# =========================================================
# Test Balance Sheet
# =========================================================

balance_sheet = BalanceSheetExtraction(

    document_type="BALANCE_SHEET",

    statement_title="Test Balance Sheet",

    statement_date="31-Mar-2026",

    currency="₹000",

    periods=[
        "31-Mar-26",
        "31-Mar-25",
    ],

    capital_and_liabilities=[

        BalanceSheetLineItem(
            name="Capital",
            values=[
                BalanceSheetPeriodValue(
                    period="31-Mar-26",
                    value="100",
                ),
                BalanceSheetPeriodValue(
                    period="31-Mar-25",
                    value="80",
                ),
            ],
        ),

        BalanceSheetLineItem(
            name="Reserves",
            values=[
                BalanceSheetPeriodValue(
                    period="31-Mar-26",
                    value="200",
                ),
                BalanceSheetPeriodValue(
                    period="31-Mar-25",
                    value="150",
                ),
            ],
        ),

        BalanceSheetLineItem(
            name="Deposits",
            values=[
                BalanceSheetPeriodValue(
                    period="31-Mar-26",
                    value="700",
                ),
                BalanceSheetPeriodValue(
                    period="31-Mar-25",
                    value="770",
                ),
            ],
        ),

        BalanceSheetLineItem(
            name="Total Capital and Liabilities",
            values=[
                BalanceSheetPeriodValue(
                    period="31-Mar-26",
                    value="1000",
                ),
                BalanceSheetPeriodValue(
                    period="31-Mar-25",
                    value="1000",
                ),
            ],
        ),
    ],

    assets=[

        BalanceSheetLineItem(
            name="Cash",
            values=[
                BalanceSheetPeriodValue(
                    period="31-Mar-26",
                    value="100",
                ),
                BalanceSheetPeriodValue(
                    period="31-Mar-25",
                    value="120",
                ),
            ],
        ),

        BalanceSheetLineItem(
            name="Investments",
            values=[
                BalanceSheetPeriodValue(
                    period="31-Mar-26",
                    value="300",
                ),
                BalanceSheetPeriodValue(
                    period="31-Mar-25",
                    value="280",
                ),
            ],
        ),

        BalanceSheetLineItem(
            name="Advances",
            values=[
                BalanceSheetPeriodValue(
                    period="31-Mar-26",
                    value="600",
                ),
                BalanceSheetPeriodValue(
                    period="31-Mar-25",
                    value="600",
                ),
            ],
        ),

        BalanceSheetLineItem(
            name="Total Assets",
            values=[
                BalanceSheetPeriodValue(
                    period="31-Mar-26",
                    value="1000",
                ),
                BalanceSheetPeriodValue(
                    period="31-Mar-25",
                    value="1000",
                ),
            ],
        ),
    ],
)


# =========================================================
# Run validation
# =========================================================

result = validate_balance_sheet(
    balance_sheet
)


print("=" * 70)
print("BALANCE SHEET FINANCIAL VALIDATION")
print("=" * 70)

print()

print(
    f"Overall status: "
    f"{result['overall_status']}"
)

print()

for validation in result["validations"]:

    print("-" * 70)

    print(
        f"Period: "
        f"{validation['period']}"
    )

    print(
        f"Validation: "
        f"{validation['validation']}"
    )

    print(
        f"Formula: "
        f"{validation['formula']}"
    )

    print(
        f"Calculated: "
        f"{validation['calculated']}"
    )

    print(
        f"Reported: "
        f"{validation['reported']}"
    )

    print(
        f"Variance: "
        f"{validation['variance']}"
    )

    print(
        f"Status: "
        f"{validation['status']}"
    )