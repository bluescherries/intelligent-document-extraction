from decimal import Decimal, InvalidOperation
import re

from backend.app.schemas.cash_flow_schema import CashFlowExtraction


# =========================================================
# Number parsing
# =========================================================

def parse_decimal(value):
    """
    Convert financial strings into Decimal.

    Examples:
        "1,230,615,562" -> 1230615562
        "(8,521,873)"   -> -8521873
        "-58,929,743"   -> -58929743
        "-"             -> None
        None            -> None
    """

    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    # Dash means no value reported.
    if text in {"-", "—", "–"}:
        return None

    # Remove currency symbols and other non-numeric
    # characters except comma, decimal point and minus.
    text = re.sub(
        r"[^\d,\.\-\(\)]",
        "",
        text,
    )

    if not text:
        return None

    # Parentheses mean negative.
    is_negative = (
        text.startswith("(")
        and text.endswith(")")
    )

    text = text.replace("(", "")
    text = text.replace(")", "")
    text = text.replace(",", "")

    if not text:
        return None

    try:
        number = Decimal(text)

    except InvalidOperation:
        return None

    if is_negative:
        number = -number

    return number


# =========================================================
# Variance
# =========================================================

def calculate_variance(
    calculated: Decimal,
    reported: Decimal,
) -> Decimal:

    return calculated - reported


# =========================================================
# Validation status
# =========================================================

def get_status(
    calculated: Decimal,
    reported: Decimal,
    tolerance: Decimal,
) -> str:

    variance = abs(
        calculate_variance(
            calculated,
            reported,
        )
    )

    if variance <= tolerance:
        return "PASS"

    return "FAILED"


# =========================================================
# Find line item
# =========================================================

def find_line_item(
    items,
    keywords,
):
    """
    Find the first line item whose name contains
    one of the supplied keywords.
    """

    for item in items:

        name = item.name.lower()

        for keyword in keywords:

            if keyword.lower() in name:
                return item

    return None


# =========================================================
# Get value for period
# =========================================================

def get_period_value(
    item,
    period,
):

    if item is None:
        return None

    for value in item.values:

        if value.period == period:
            return parse_decimal(
                value.value
            )

    return None


# =========================================================
# Main Cash Flow validation
# =========================================================

def validate_cash_flow(
    cash_flow: CashFlowExtraction,
    tolerance: Decimal = Decimal("0.01"),
) -> dict:

    validations = []

    # =====================================================
    # Validate each reporting period independently
    # =====================================================

    for period in cash_flow.periods:

        # -------------------------------------------------
        # Find major activity totals
        # -------------------------------------------------

        operating_item = find_line_item(
            cash_flow.operating_activities,
            [
                "net cash from operating activities",
                "net cash generated from operating activities",
                "net cash provided by operating activities",
            ],
        )

        investing_item = find_line_item(
            cash_flow.investing_activities,
            [
                "net cash used in investing activities",
                "net cash from investing activities",
                "net cash generated from investing activities",
            ],
        )

        financing_item = find_line_item(
            cash_flow.financing_activities,
            [
                "net cash (used in) / from financing activities",
                "net cash used in financing activities",
                "net cash from financing activities",
                "net cash generated from financing activities",
            ],
        )

        net_increase_item = find_line_item(
            cash_flow.cash_reconciliation,
            [
                "net increase in cash and cash equivalents",
                "net increase / decrease in cash and cash equivalents",
                "net increase/(decrease) in cash and cash equivalents",
                "net decrease in cash and cash equivalents",
            ],
        )

        fx_item = find_line_item(
            cash_flow.cash_reconciliation,
            [
                "effect of exchange fluctuation",
                "effect of foreign exchange",
                "exchange rate changes",
                "foreign exchange rate changes",
            ],
        )

        # -------------------------------------------------
        # Find explicit amalgamation adjustment
        # -------------------------------------------------

        amalgamation_item = find_line_item(
            cash_flow.cash_reconciliation,
            [
                "cash and cash equivalents on amalgamation",
                "cash and cash equivalents on amalgamations",
                "cash on amalgamation",
            ],
        )

        # -------------------------------------------------
        # Extract values
        # -------------------------------------------------

        operating = get_period_value(
            operating_item,
            period,
        )

        investing = get_period_value(
            investing_item,
            period,
        )

        financing = get_period_value(
            financing_item,
            period,
        )

        net_increase = get_period_value(
            net_increase_item,
            period,
        )

        fx = get_period_value(
            fx_item,
            period,
        )

        amalgamation_adjustment = get_period_value(
            amalgamation_item,
            period,
        )

        # -------------------------------------------------
        # Validation 1:
        #
        # Operating
        # + Investing
        # + Financing
        # + FX
        # + Amalgamation adjustment, when explicitly reported
        # ≈ Net increase
        # -------------------------------------------------

        inputs_available = (
            operating is not None
            and investing is not None
            and financing is not None
            and net_increase is not None
        )

        if inputs_available:

            calculated = (
                operating
                + investing
                + financing
            )

            formula = (
                "operating_cash_flow + "
                "investing_cash_flow + "
                "financing_cash_flow"
            )

            inputs = {
                "operating_cash_flow": str(
                    operating
                ),
                "investing_cash_flow": str(
                    investing
                ),
                "financing_cash_flow": str(
                    financing
                ),
            }

            # -------------------------------------------------
            # FX adjustment is applicable only when explicitly
            # reported in the document.
            # -------------------------------------------------

            if fx is not None:

                calculated += fx

                formula += (
                    " + fx_adjustment"
                )

                inputs["fx_adjustment"] = str(
                    fx
                )

            # -------------------------------------------------
            # Amalgamation adjustment is applicable only when
            # explicitly reported in the document.
            #
            # We NEVER invent this value.
            # -------------------------------------------------

            if amalgamation_adjustment is not None:

                calculated += (
                    amalgamation_adjustment
                )

                formula += (
                    " + amalgamation_adjustment"
                )

                inputs["amalgamation_adjustment"] = str(
                    amalgamation_adjustment
                )

            variance = calculate_variance(
                calculated,
                net_increase,
            )

            status = get_status(
                calculated,
                net_increase,
                tolerance,
            )

            validations.append(
                {
                    "period": period,
                    "validation": "cash_flow_activity_reconciliation",
                    "formula": (
                        formula
                        + " ≈ net_increase_in_cash"
                    ),
                    "inputs": inputs,
                    "calculated": str(calculated),
                    "reported": str(net_increase),
                    "variance": str(variance),
                    "status": status,
                }
            )

        else:

            # -------------------------------------------------
            # Build inputs for NOT_APPLICABLE case.
            # -------------------------------------------------

            inputs = {
                "operating_cash_flow": (
                    str(operating)
                    if operating is not None
                    else None
                ),
                "investing_cash_flow": (
                    str(investing)
                    if investing is not None
                    else None
                ),
                "financing_cash_flow": (
                    str(financing)
                    if financing is not None
                    else None
                ),
                "fx_adjustment": (
                    str(fx)
                    if fx is not None
                    else None
                ),
                "amalgamation_adjustment": (
                    str(amalgamation_adjustment)
                    if amalgamation_adjustment is not None
                    else None
                ),
            }

            validations.append(
                {
                    "period": period,
                    "validation": "cash_flow_activity_reconciliation",
                    "formula": (
                        "operating_cash_flow + "
                        "investing_cash_flow + "
                        "financing_cash_flow "
                        "+ optional_fx_adjustment "
                        "+ optional_amalgamation_adjustment "
                        "≈ net_increase_in_cash"
                    ),
                    "inputs": inputs,
                    "calculated": None,
                    "reported": (
                        str(net_increase)
                        if net_increase is not None
                        else None
                    ),
                    "variance": None,
                    "status": "NOT_APPLICABLE",
                }
            )

        # -------------------------------------------------
        # Find opening and closing cash
        # -------------------------------------------------

        opening_item = find_line_item(
            cash_flow.cash_reconciliation,
            [
                "cash and cash equivalents as at april 1st",
                "cash and cash equivalents at beginning",
                "cash and cash equivalents as at april 1",
                "cash and cash equivalents at 1 april",
            ],
        )

        closing_item = find_line_item(
            cash_flow.cash_reconciliation,
            [
                "cash and cash equivalents as at march 31st",
                "cash and cash equivalents at end",
                "cash and cash equivalents as at march 31",
            ],
        )

        opening_cash = get_period_value(
            opening_item,
            period,
        )

        closing_cash = get_period_value(
            closing_item,
            period,
        )

        # -------------------------------------------------
        # Validation 2:
        #
        # Opening cash + net increase
        # ≈ closing cash
        #
        # -------------------------------------------------

        if (
            opening_cash is not None
            and net_increase is not None
            and closing_cash is not None
        ):

            calculated_closing = (
                opening_cash
                + net_increase
            )

            variance = calculate_variance(
                calculated_closing,
                closing_cash,
            )

            status = get_status(
                calculated_closing,
                closing_cash,
                tolerance,
            )

            validations.append(
                {
                    "period": period,
                    "validation": "cash_balance_reconciliation",
                    "formula": (
                        "opening_cash + "
                        "net_increase_in_cash "
                        "≈ closing_cash"
                    ),
                    "inputs": {
                        "opening_cash": str(
                            opening_cash
                        ),
                        "net_increase_in_cash": str(
                            net_increase
                        ),
                    },
                    "calculated": str(
                        calculated_closing
                    ),
                    "reported": str(
                        closing_cash
                    ),
                    "variance": str(
                        variance
                    ),
                    "status": status,
                }
            )

        else:

            validations.append(
                {
                    "period": period,
                    "validation": "cash_balance_reconciliation",
                    "formula": (
                        "opening_cash + "
                        "net_increase_in_cash "
                        "≈ closing_cash"
                    ),
                    "inputs": {
                        "opening_cash": (
                            str(opening_cash)
                            if opening_cash is not None
                            else None
                        ),
                        "net_increase_in_cash": (
                            str(net_increase)
                            if net_increase is not None
                            else None
                        ),
                    },
                    "calculated": None,
                    "reported": (
                        str(closing_cash)
                        if closing_cash is not None
                        else None
                    ),
                    "variance": None,
                    "status": "NOT_APPLICABLE",
                }
            )

    # =====================================================
    # Overall status
    # =====================================================

    failed = any(
        validation["status"] == "FAILED"
        for validation in validations
    )

    overall_status = (
        "FAILED"
        if failed
        else "PASS"
    )

    return {
        "overall_status": overall_status,
        "tolerance": str(tolerance),
        "validations": validations,
    }