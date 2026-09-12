from backend.app.schemas.invoice_schema import (
    InvoiceExtraction,
    InvoiceItem,
    InvoiceTotals,
)

from backend.app.services.financial_validation_service import (
    validate_invoice,
)


# Create a small test invoice.
#
# This is only test data for checking our calculation engine.
invoice = InvoiceExtraction(
    invoice_number="TEST-001",

    items=[
        InvoiceItem(
            item_number="1",
            description="Shoes",
            quantity="5,00",
            unit="each",
            unit_price="3,49",
            net_amount="17,45",
            vat_rate="10%",
            gross_amount="19,20",
        )
    ],

    summary=InvoiceTotals(
        net_amount="17,45",
        vat_amount="1,75",
        gross_amount="19,20",
    ),
)


result = validate_invoice(invoice)


print("=" * 70)
print("FINANCIAL VALIDATION RESULT")
print("=" * 70)

print()

print(f"Overall status: {result['overall_status']}")

print()

for validation in result["validations"]:

    print("-" * 70)

    print(
        f"Validation: {validation['validation']}"
    )

    print(
        f"Formula: {validation['formula']}"
    )

    print(
        f"Calculated: {validation['calculated']}"
    )

    print(
        f"Reported: {validation['reported']}"
    )

    print(
        f"Variance: {validation['variance']}"
    )

    print(
        f"Status: {validation['status']}"
    )