from backend.app.schemas.profit_loss_schema import (
    ProfitLossExtraction,
)


result = ProfitLossExtraction(
    document_type="PROFIT_AND_LOSS",
    statement_title="Consolidated Profit and Loss Account",
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