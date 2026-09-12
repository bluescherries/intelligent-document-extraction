from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Optional

from backend.app.schemas.invoice_schema import InvoiceExtraction


# ---------------------------------------------------------
# Default financial tolerance
# ---------------------------------------------------------

DEFAULT_TOLERANCE = Decimal("0.01")


# ---------------------------------------------------------
# Decimal parsing
# ---------------------------------------------------------

def parse_decimal(value: Optional[str]) -> Optional[Decimal]:
    """
    Convert a financial value stored as a string into Decimal.

    Examples:
        "17,45"       -> 17.45
        "17.45"       -> 17.45
        "$17.45"      -> 17.45
        "₹17.45"      -> 17.45
        "1,234.56"    -> 1234.56
        "1.234,56"    -> 1234.56
        "(100.00)"    -> -100.00

    Returns None when the value cannot be parsed.
    """

    if value is None:
        return None

    if isinstance(value, Decimal):
        return value

    text = str(value).strip()

    if not text:
        return None

    # Remove common currency symbols and spaces.
    text = (
        text.replace("$", "")
        .replace("€", "")
        .replace("£", "")
        .replace("₹", "")
        .replace(" ", "")
    )

    # Handle negative values written using parentheses.
    is_negative = text.startswith("(") and text.endswith(")")

    if is_negative:
        text = text[1:-1]

    # Handle values containing both comma and dot.
    #
    # Examples:
    #   1.234,56 -> 1234.56
    #   1,234.56 -> 1234.56
    if "," in text and "." in text:

        if text.rfind(",") > text.rfind("."):
            # European format:
            # 1.234,56
            text = text.replace(".", "")
            text = text.replace(",", ".")

        else:
            # Standard format:
            # 1,234.56
            text = text.replace(",", "")

    # Handle values containing only comma.
    elif "," in text:

        parts = text.split(",")

        # Example:
        # 17,45 -> 17.45
        if len(parts) == 2 and len(parts[1]) <= 2:
            text = text.replace(",", ".")

        else:
            # Example:
            # 1,234 -> 1234
            text = text.replace(",", "")

    try:

        number = Decimal(text)

        if is_negative:
            number = -number

        return number

    except (InvalidOperation, ValueError):

        return None


# ---------------------------------------------------------
# Percentage parsing
# ---------------------------------------------------------

def parse_percentage(value: Optional[str]) -> Optional[Decimal]:
    """
    Convert a percentage string into Decimal.

    Examples:
        "10%"   -> 10
        "10"    -> 10
        "5.5%"  -> 5.5
        "5,5%"  -> 5.5
    """

    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    # Remove percentage sign.
    text = text.replace("%", "").strip()

    return parse_decimal(text)


# ---------------------------------------------------------
# Calculate variance
# ---------------------------------------------------------

def calculate_variance(
    calculated: Decimal,
    reported: Decimal,
) -> Decimal:
    """
    Calculate:

        calculated - reported
    """

    return calculated - reported


# ---------------------------------------------------------
# Determine PASS / FAILED
# ---------------------------------------------------------

def get_status(
    calculated: Decimal,
    reported: Decimal,
    tolerance: Decimal = DEFAULT_TOLERANCE,
) -> str:
    """
    Determine whether a financial calculation passes.

    PASS:
        Absolute variance is within tolerance.

    FAILED:
        Absolute variance exceeds tolerance.
    """

    variance = abs(calculated - reported)

    if variance <= tolerance:
        return "PASS"

    return "FAILED"


# ---------------------------------------------------------
# Validate individual line item
# ---------------------------------------------------------

def validate_line_item(
    item_number: int,
    quantity: Optional[str],
    unit_price: Optional[str],
    reported_net_amount: Optional[str],
    tolerance: Decimal = DEFAULT_TOLERANCE,
) -> dict:
    """
    Validate:

        quantity × unit price ≈ net amount
    """

    quantity_value = parse_decimal(quantity)

    unit_price_value = parse_decimal(unit_price)

    reported_value = parse_decimal(
        reported_net_amount
    )

    # If required information is missing,
    # do not assume or invent anything.
    if (
        quantity_value is None
        or unit_price_value is None
        or reported_value is None
    ):

        return {
            "validation": "line_item_calculation",
            "item_number": item_number,
            "formula": "quantity × unit_price ≈ net_amount",
            "inputs": {
                "quantity": quantity,
                "unit_price": unit_price,
                "reported_net_amount": reported_net_amount,
            },
            "calculated": None,
            "reported": reported_value,
            "variance": None,
            "status": "NOT_APPLICABLE",
        }

    calculated = quantity_value * unit_price_value

    variance = calculate_variance(
        calculated,
        reported_value,
    )

    status = get_status(
        calculated,
        reported_value,
        tolerance,
    )

    return {
        "validation": "line_item_calculation",
        "item_number": item_number,
        "formula": "quantity × unit_price ≈ net_amount",
        "inputs": {
            "quantity": str(quantity_value),
            "unit_price": str(unit_price_value),
        },
        "calculated": str(calculated),
        "reported": str(reported_value),
        "variance": str(variance),
        "status": status,
    }


# ---------------------------------------------------------
# Validate complete invoice
# ---------------------------------------------------------

def validate_invoice(
    invoice: InvoiceExtraction,
    tolerance: Decimal = DEFAULT_TOLERANCE,
) -> dict:
    """
    Perform deterministic financial validations on an invoice.

    Validations:

    1. Quantity × Unit Price ≈ Line Net Amount
    2. Sum of Line Net Amounts ≈ Invoice Net Amount
    3. Net Amount × VAT Rate ≈ VAT Amount
    4. Net Amount + VAT Amount ≈ Gross Amount
    5. Amount Paid - Total ≈ Change
    """

    validations = []

    # =====================================================
    # 1. Validate each line item
    # =====================================================

    for index, item in enumerate(
        invoice.items,
        start=1,
    ):

        validation = validate_line_item(
            item_number=index,
            quantity=item.quantity,
            unit_price=item.unit_price,
            reported_net_amount=item.net_amount,
            tolerance=tolerance,
        )

        validations.append(validation)

    # =====================================================
    # 2. Validate sum of line items
    # =====================================================

    if invoice.summary is not None:

        reported_net = parse_decimal(
            invoice.summary.net_amount
        )

        line_amounts = [
            parse_decimal(item.net_amount)
            for item in invoice.items
        ]

        # Perform calculation only when all
        # required values are available.
        if (
            reported_net is not None
            and invoice.items
            and all(
                amount is not None
                for amount in line_amounts
            )
        ):

            calculated_net = sum(
                line_amounts,
                Decimal("0"),
            )

            variance = calculate_variance(
                calculated_net,
                reported_net,
            )

            status = get_status(
                calculated_net,
                reported_net,
                tolerance,
            )

            validations.append(
                {
                    "validation": "line_items_sum",
                    "formula": (
                        "sum(line item net amounts) "
                        "≈ invoice net amount"
                    ),
                    "inputs": {
                        "line_item_net_amounts": [
                            str(amount)
                            for amount in line_amounts
                        ],
                    },
                    "calculated": str(calculated_net),
                    "reported": str(reported_net),
                    "variance": str(variance),
                    "status": status,
                }
            )

        else:

            validations.append(
                {
                    "validation": "line_items_sum",
                    "formula": (
                        "sum(line item net amounts) "
                        "≈ invoice net amount"
                    ),
                    "inputs": {
                        "line_item_net_amounts": [
                            item.net_amount
                            for item in invoice.items
                        ],
                        "invoice_net_amount": (
                            invoice.summary.net_amount
                        ),
                    },
                    "calculated": None,
                    "reported": reported_net,
                    "variance": None,
                    "status": "NOT_APPLICABLE",
                }
            )

    # =====================================================
    # 3. Validate VAT rate
    # =====================================================

    if invoice.summary is not None:

        net_amount = parse_decimal(
            invoice.summary.net_amount
        )

        reported_vat = parse_decimal(
            invoice.summary.vat_amount
        )

        # Extract VAT rates from items.
        vat_rates = [
            parse_percentage(item.vat_rate)
            for item in invoice.items
            if item.vat_rate is not None
        ]

        # Remove None values.
        vat_rates = [
            rate
            for rate in vat_rates
            if rate is not None
        ]

        # We can safely perform the calculation
        # when there is exactly one unique VAT rate.
        unique_vat_rates = set(vat_rates)

        if (
            net_amount is not None
            and reported_vat is not None
            and len(unique_vat_rates) == 1
        ):

            vat_rate = vat_rates[0]

            calculated_vat = (
                net_amount
                * vat_rate
                / Decimal("100")
            )

            # Round to two decimal places because
            # financial documents generally report
            # monetary values to cents.
            calculated_vat = calculated_vat.quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP,
            )

            variance = calculate_variance(
                calculated_vat,
                reported_vat,
            )

            status = get_status(
                calculated_vat,
                reported_vat,
                tolerance,
            )

            validations.append(
                {
                    "validation": "vat_calculation",
                    "formula": (
                        "net amount × VAT rate "
                        "≈ VAT amount"
                    ),
                    "inputs": {
                        "net_amount": str(net_amount),
                        "vat_rate": f"{vat_rate}%",
                    },
                    "calculated": str(calculated_vat),
                    "reported": str(reported_vat),
                    "variance": str(variance),
                    "status": status,
                }
            )

        else:

            validations.append(
                {
                    "validation": "vat_calculation",
                    "formula": (
                        "net amount × VAT rate "
                        "≈ VAT amount"
                    ),
                    "inputs": {
                        "net_amount": (
                            invoice.summary.net_amount
                        ),
                        "vat_rates": [
                            str(rate)
                            for rate in vat_rates
                        ],
                    },
                    "calculated": None,
                    "reported": reported_vat,
                    "variance": None,
                    "status": "NOT_APPLICABLE",
                }
            )

    # =====================================================
    # 4. Validate net amount + VAT ≈ gross amount
    # =====================================================

    if invoice.summary is not None:

        net = parse_decimal(
            invoice.summary.net_amount
        )

        vat = parse_decimal(
            invoice.summary.vat_amount
        )

        gross = parse_decimal(
            invoice.summary.gross_amount
        )

        if (
            net is not None
            and vat is not None
            and gross is not None
        ):

            calculated = net + vat

            variance = calculate_variance(
                calculated,
                gross,
            )

            status = get_status(
                calculated,
                gross,
                tolerance,
            )

            validations.append(
                {
                    "validation": "invoice_total_calculation",
                    "formula": (
                        "net_amount + vat_amount "
                        "≈ gross_amount"
                    ),
                    "inputs": {
                        "net_amount": str(net),
                        "vat_amount": str(vat),
                    },
                    "calculated": str(calculated),
                    "reported": str(gross),
                    "variance": str(variance),
                    "status": status,
                }
            )

        else:

            validations.append(
                {
                    "validation": "invoice_total_calculation",
                    "formula": (
                        "net_amount + vat_amount "
                        "≈ gross_amount"
                    ),
                    "inputs": {
                        "net_amount": (
                            invoice.summary.net_amount
                        ),
                        "vat_amount": (
                            invoice.summary.vat_amount
                        ),
                    },
                    "calculated": None,
                    "reported": gross,
                    "variance": None,
                    "status": "NOT_APPLICABLE",
                }
            )

    # =====================================================
    # 5. Validate payment and change
    # =====================================================

    payment = invoice.payment_information

    if payment is not None:

        amount_paid = parse_decimal(
            payment.amount_paid
        )

        change = parse_decimal(
            payment.change
        )

        # Try total.gross_amount first.
        total_gross = None

        if invoice.total is not None:

            total_gross = parse_decimal(
                invoice.total.gross_amount
            )

        # If total is unavailable,
        # use summary.gross_amount.
        if (
            total_gross is None
            and invoice.summary is not None
        ):

            total_gross = parse_decimal(
                invoice.summary.gross_amount
            )

        if (
            amount_paid is not None
            and total_gross is not None
            and change is not None
        ):

            calculated = (
                amount_paid - total_gross
            )

            variance = calculate_variance(
                calculated,
                change,
            )

            status = get_status(
                calculated,
                change,
                tolerance,
            )

            validations.append(
                {
                    "validation": (
                        "payment_change_calculation"
                    ),
                    "formula": (
                        "amount_paid - total "
                        "≈ change"
                    ),
                    "inputs": {
                        "amount_paid": str(
                            amount_paid
                        ),
                        "total": str(
                            total_gross
                        ),
                    },
                    "calculated": str(
                        calculated
                    ),
                    "reported": str(change),
                    "variance": str(variance),
                    "status": status,
                }
            )

        else:

            validations.append(
                {
                    "validation": (
                        "payment_change_calculation"
                    ),
                    "formula": (
                        "amount_paid - total "
                        "≈ change"
                    ),
                    "inputs": {
                        "amount_paid": (
                            payment.amount_paid
                        ),
                        "total": (
                            str(total_gross)
                            if total_gross is not None
                            else None
                        ),
                    },
                    "calculated": None,
                    "reported": change,
                    "variance": None,
                    "status": "NOT_APPLICABLE",
                }
            )

    # =====================================================
    # 6. Determine overall validation status
    # =====================================================

    failed = any(
        validation["status"] == "FAILED"
        for validation in validations
    )

    if failed:

        overall_status = "FAILED"

    else:

        overall_status = "PASS"

    # =====================================================
    # Return complete validation result
    # =====================================================

    return {
        "overall_status": overall_status,
        "tolerance": str(tolerance),
        "validations": validations,
    }