from backend.app.schemas.cash_flow_schema import (
    CashFlowExtraction,
)


result = CashFlowExtraction(
    document_type="CASH_FLOW_STATEMENT",
    statement_title="Consolidated Cash Flow Statement",
    statement_date="March 31, 2026",
    currency="₹000",
    periods=[
        "31-Mar-26",
        "31-Mar-25",
    ],
)

print(
    result.model_dump_json(
        indent=2
    )
)
