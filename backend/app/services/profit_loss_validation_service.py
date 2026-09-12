from decimal import Decimal, InvalidOperation
from typing import Optional

from backend.app.schemas.profit_loss_schema import (
    ProfitLossExtraction,
    ProfitLossLineItem,
)


# =========================================================
# Default tolerance
# =========================================================

DEFAULT_TOLERANCE = Decimal("0.01")


# =========================================================
# Parse financial values
# =========================================================

def parse_decimal(
    value: Optional[str],
) -> Optional[Decimal]:

    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    # Remove common currency symbols and spaces.
    text = (
        text.replace("₹", "")
        .replace("$", "")
        .replace("€", "")
        .replace("£", "")
        .replace(" ", "")
    )

    # Parentheses represent negative values.
    is_negative = (
        text.startswith("(")
        and text.endswith(")")
    )

    if is_negative:
        text = text[1:-1]

    # Handle both:
    # 1,234.56
    # 1.234,56
    if "," in text and "." in text:

        if text.rfind(",") > text.rfind("."):

            # European style
            text = text.replace(".", "")
            text = text.replace(",", ".")

        else:

            # Standard thousands separator
            text = text.replace(",", "")

    elif "," in text:

        parts = text.split(",")

        # Example:
        # 123,45
        if (
            len(parts) == 2
            and len(parts[1]) <= 2
        ):
            text = text.replace(",", ".")

        else:

            # Example:
            # 732,713,529
            text = text.replace(",", "")

    try:

        number = Decimal(text)

        if is_negative:
            number = -number

        return number

    except (
        InvalidOperation,
        ValueError,
    ):

        return None


# =========================================================
# Calculate variance
# =========================================================

def calculate_variance(
    calculated: Decimal,
    reported: Decimal,
) -> Decimal:

    return calculated - reported


# =========================================================
# Determine PASS / FAILED
# =========================================================

def get_status(
    calculated: Decimal,
    reported: Decimal,
    tolerance: Decimal,
) -> str:

    variance = abs(
        calculated - reported
    )

    if variance <= tolerance:
        return "PASS"

    return "FAILED"


# =========================================================
# Get value for a particular period
# =========================================================

def get_period_value(
    line_item: ProfitLossLineItem,
    period: str,
) -> Optional[Decimal]:

    for period_value in line_item.values:

        if period_value.period == period:

            return parse_decimal(
                period_value.value
            )

    return None


# =========================================================
# Normalize row name
# =========================================================

def normalize_name(
    name: str,
) -> str:

    return (
        name.lower()
        .strip()
        .replace(":", "")
        .replace("-", " ")
        .replace("–", " ")
        .replace("—", " ")
    )


# =========================================================
# Find a row by keywords
# =========================================================

def find_line_item(
    line_items: list[ProfitLossLineItem],
    keywords: list[str],
    line_types: Optional[list[str]] = None,
) -> Optional[ProfitLossLineItem]:

    for item in line_items:

        if (
            line_types is not None
            and item.line_type not in line_types
        ):
            continue

        name = normalize_name(
            item.name
        )

        if all(
            keyword.lower() in name
            for keyword in keywords
        ):

            return item

    return None


# =========================================================
# Find TOTAL row
# =========================================================

def find_total_row(
    line_items: list[ProfitLossLineItem],
) -> Optional[ProfitLossLineItem]:

    # First look for explicitly classified TOTAL rows.
    total_rows = [
        item
        for item in line_items
        if item.line_type == "TOTAL"
    ]

    if total_rows:

        return total_rows[-1]

    # Fallback for a row literally named "Total".
    for item in line_items:

        if normalize_name(item.name) == "total":

            return item

    return None


# =========================================================
# Validate:
#
# Interest earned + Other income ≈ Total income
# =========================================================

def validate_total_income(
    period: str,
    income: list[ProfitLossLineItem],
    tolerance: Decimal,
) -> dict:

    interest_earned = find_line_item(
        income,
        ["interest", "earned"],
        ["ITEM"],
    )

    other_income = find_line_item(
        income,
        ["other", "income"],
        ["ITEM"],
    )

    total_income = find_total_row(
        income
    )

    if (
        interest_earned is None
        or other_income is None
        or total_income is None
    ):

        return {
            "validation": "total_income_calculation",
            "period": period,
            "formula": (
                "interest_earned + other_income "
                "≈ total_income"
            ),
            "inputs": {
                "interest_earned": None,
                "other_income": None,
            },
            "calculated": None,
            "reported": None,
            "variance": None,
            "status": "NOT_APPLICABLE",
        }

    interest_value = get_period_value(
        interest_earned,
        period,
    )

    other_income_value = get_period_value(
        other_income,
        period,
    )

    reported_total = get_period_value(
        total_income,
        period,
    )

    if (
        interest_value is None
        or other_income_value is None
        or reported_total is None
    ):

        return {
            "validation": "total_income_calculation",
            "period": period,
            "formula": (
                "interest_earned + other_income "
                "≈ total_income"
            ),
            "inputs": {
                "interest_earned": (
                    str(interest_value)
                    if interest_value is not None
                    else None
                ),
                "other_income": (
                    str(other_income_value)
                    if other_income_value is not None
                    else None
                ),
            },
            "calculated": None,
            "reported": (
                str(reported_total)
                if reported_total is not None
                else None
            ),
            "variance": None,
            "status": "NOT_APPLICABLE",
        }

    calculated = (
        interest_value
        + other_income_value
    )

    variance = calculate_variance(
        calculated,
        reported_total,
    )

    status = get_status(
        calculated,
        reported_total,
        tolerance,
    )

    return {
        "validation": "total_income_calculation",
        "period": period,
        "formula": (
            "interest_earned + other_income "
            "≈ total_income"
        ),
        "inputs": {
            "interest_earned": str(
                interest_value
            ),
            "other_income": str(
                other_income_value
            ),
        },
        "calculated": str(
            calculated
        ),
        "reported": str(
            reported_total
        ),
        "variance": str(
            variance
        ),
        "status": status,
    }


# =========================================================
# Validate:
#
# Interest expended
# + Operating expenses
# + Provisions and contingencies
# ≈ Total expenditure
# =========================================================

def validate_total_expenditure(
    period: str,
    expenditure: list[ProfitLossLineItem],
    tolerance: Decimal,
) -> dict:

    interest_expended = find_line_item(
        expenditure,
        ["interest", "expended"],
        ["ITEM"],
    )

    operating_expenses = find_line_item(
        expenditure,
        ["operating", "expenses"],
        ["ITEM"],
    )

    provisions = find_line_item(
        expenditure,
        ["provisions", "contingencies"],
        ["ITEM"],
    )

    total_expenditure = find_total_row(
        expenditure
    )

    if (
        interest_expended is None
        or operating_expenses is None
        or provisions is None
        or total_expenditure is None
    ):

        return {
            "validation": "total_expenditure_calculation",
            "period": period,
            "formula": (
                "interest_expended + operating_expenses "
                "+ provisions_and_contingencies "
                "≈ total_expenditure"
            ),
            "inputs": {},
            "calculated": None,
            "reported": None,
            "variance": None,
            "status": "NOT_APPLICABLE",
        }

    interest_value = get_period_value(
        interest_expended,
        period,
    )

    operating_value = get_period_value(
        operating_expenses,
        period,
    )

    provisions_value = get_period_value(
        provisions,
        period,
    )

    reported_total = get_period_value(
        total_expenditure,
        period,
    )

    if (
        interest_value is None
        or operating_value is None
        or provisions_value is None
        or reported_total is None
    ):

        return {
            "validation": "total_expenditure_calculation",
            "period": period,
            "formula": (
                "interest_expended + operating_expenses "
                "+ provisions_and_contingencies "
                "≈ total_expenditure"
            ),
            "inputs": {
                "interest_expended": (
                    str(interest_value)
                    if interest_value is not None
                    else None
                ),
                "operating_expenses": (
                    str(operating_value)
                    if operating_value is not None
                    else None
                ),
                "provisions_and_contingencies": (
                    str(provisions_value)
                    if provisions_value is not None
                    else None
                ),
            },
            "calculated": None,
            "reported": (
                str(reported_total)
                if reported_total is not None
                else None
            ),
            "variance": None,
            "status": "NOT_APPLICABLE",
        }

    calculated = (
        interest_value
        + operating_value
        + provisions_value
    )

    variance = calculate_variance(
        calculated,
        reported_total,
    )

    status = get_status(
        calculated,
        reported_total,
        tolerance,
    )

    return {
        "validation": "total_expenditure_calculation",
        "period": period,
        "formula": (
            "interest_expended + operating_expenses "
            "+ provisions_and_contingencies "
            "≈ total_expenditure"
        ),
        "inputs": {
            "interest_expended": str(
                interest_value
            ),
            "operating_expenses": str(
                operating_value
            ),
            "provisions_and_contingencies": str(
                provisions_value
            ),
        },
        "calculated": str(
            calculated
        ),
        "reported": str(
            reported_total
        ),
        "variance": str(
            variance
        ),
        "status": status,
    }


# =========================================================
# Validate:
#
# Total income - Total expenditure
# ≈ Net profit for the year
# =========================================================

def validate_net_profit(
    period: str,
    income: list[ProfitLossLineItem],
    expenditure: list[ProfitLossLineItem],
    profit_rows: list[ProfitLossLineItem],
    tolerance: Decimal,
) -> dict:

    total_income_row = find_total_row(
        income
    )

    total_expenditure_row = find_total_row(
        expenditure
    )

    net_profit_row = find_line_item(
        profit_rows,
        ["net", "profit", "year"],
        ["SUBTOTAL", "TOTAL"],
    )

    if (
        total_income_row is None
        or total_expenditure_row is None
        or net_profit_row is None
    ):

        return {
            "validation": "net_profit_calculation",
            "period": period,
            "formula": (
                "total_income - total_expenditure "
                "≈ net_profit_for_year"
            ),
            "inputs": {},
            "calculated": None,
            "reported": None,
            "variance": None,
            "status": "NOT_APPLICABLE",
        }

    total_income = get_period_value(
        total_income_row,
        period,
    )

    total_expenditure = get_period_value(
        total_expenditure_row,
        period,
    )

    reported_profit = get_period_value(
        net_profit_row,
        period,
    )

    if (
        total_income is None
        or total_expenditure is None
        or reported_profit is None
    ):

        return {
            "validation": "net_profit_calculation",
            "period": period,
            "formula": (
                "total_income - total_expenditure "
                "≈ net_profit_for_year"
            ),
            "inputs": {
                "total_income": (
                    str(total_income)
                    if total_income is not None
                    else None
                ),
                "total_expenditure": (
                    str(total_expenditure)
                    if total_expenditure is not None
                    else None
                ),
            },
            "calculated": None,
            "reported": (
                str(reported_profit)
                if reported_profit is not None
                else None
            ),
            "variance": None,
            "status": "NOT_APPLICABLE",
        }

    calculated = (
        total_income
        - total_expenditure
    )

    variance = calculate_variance(
        calculated,
        reported_profit,
    )

    status = get_status(
        calculated,
        reported_profit,
        tolerance,
    )

    return {
        "validation": "net_profit_calculation",
        "period": period,
        "formula": (
            "total_income - total_expenditure "
            "≈ net_profit_for_year"
        ),
        "inputs": {
            "total_income": str(
                total_income
            ),
            "total_expenditure": str(
                total_expenditure
            ),
        },
        "calculated": str(
            calculated
        ),
        "reported": str(
            reported_profit
        ),
        "variance": str(
            variance
        ),
        "status": status,
    }


# =========================================================
# Validate consolidated profit
#
# Net profit
# - Minority interest
# + Share in profits of associates
# ≈ Consolidated profit attributable to Group
# =========================================================

def validate_consolidated_profit(
    period: str,
    profit_rows: list[ProfitLossLineItem],
    tolerance: Decimal,
) -> dict:

    net_profit_row = find_line_item(
        profit_rows,
        ["net", "profit", "year"],
        ["SUBTOTAL", "TOTAL"],
    )

    minority_interest_row = find_line_item(
        profit_rows,
        ["minority", "interest"],
        ["ITEM"],
    )

    associate_profit_row = find_line_item(
        profit_rows,
        ["share", "profits", "associates"],
        ["ITEM"],
    )

    consolidated_profit_row = find_line_item(
        profit_rows,
        ["consolidated", "profit", "attributable"],
        ["SUBTOTAL", "TOTAL"],
    )

    if (
        net_profit_row is None
        or minority_interest_row is None
        or associate_profit_row is None
        or consolidated_profit_row is None
    ):

        return {
            "validation": "consolidated_profit_calculation",
            "period": period,
            "formula": (
                "net_profit - minority_interest "
                "+ share_in_profits_of_associates "
                "≈ consolidated_profit_attributable_to_group"
            ),
            "inputs": {},
            "calculated": None,
            "reported": None,
            "variance": None,
            "status": "NOT_APPLICABLE",
        }

    net_profit = get_period_value(
        net_profit_row,
        period,
    )

    minority_interest = get_period_value(
        minority_interest_row,
        period,
    )

    associate_profit = get_period_value(
        associate_profit_row,
        period,
    )

    reported_consolidated = get_period_value(
        consolidated_profit_row,
        period,
    )

    if (
        net_profit is None
        or minority_interest is None
        or associate_profit is None
        or reported_consolidated is None
    ):

        return {
            "validation": "consolidated_profit_calculation",
            "period": period,
            "formula": (
                "net_profit - minority_interest "
                "+ share_in_profits_of_associates "
                "≈ consolidated_profit_attributable_to_group"
            ),
            "inputs": {},
            "calculated": None,
            "reported": (
                str(reported_consolidated)
                if reported_consolidated is not None
                else None
            ),
            "variance": None,
            "status": "NOT_APPLICABLE",
        }

    calculated = (
        net_profit
        - minority_interest
        + associate_profit
    )

    variance = calculate_variance(
        calculated,
        reported_consolidated,
    )

    status = get_status(
        calculated,
        reported_consolidated,
        tolerance,
    )

    return {
        "validation": "consolidated_profit_calculation",
        "period": period,
        "formula": (
            "net_profit - minority_interest "
            "+ share_in_profits_of_associates "
            "≈ consolidated_profit_attributable_to_group"
        ),
        "inputs": {
            "net_profit": str(
                net_profit
            ),
            "minority_interest": str(
                minority_interest
            ),
            "share_in_profits_of_associates": str(
                associate_profit
            ),
        },
        "calculated": str(
            calculated
        ),
        "reported": str(
            reported_consolidated
        ),
        "variance": str(
            variance
        ),
        "status": status,
    }


# =========================================================
# Main P&L validator
# =========================================================

def validate_profit_loss(
    profit_loss: ProfitLossExtraction,
    tolerance: Decimal = DEFAULT_TOLERANCE,
) -> dict:

    validations = []

    # -----------------------------------------------------
    # Validate each reporting period independently.
    # -----------------------------------------------------

    for period in profit_loss.periods:

        # -------------------------------------------------
        # 1. Total income
        # -------------------------------------------------

        validations.append(
            validate_total_income(
                period=period,
                income=profit_loss.income,
                tolerance=tolerance,
            )
        )

        # -------------------------------------------------
        # 2. Total expenditure
        # -------------------------------------------------

        validations.append(
            validate_total_expenditure(
                period=period,
                expenditure=profit_loss.expenditure,
                tolerance=tolerance,
            )
        )

        # -------------------------------------------------
        # 3. Net profit
        # -------------------------------------------------

        validations.append(
            validate_net_profit(
                period=period,
                income=profit_loss.income,
                expenditure=profit_loss.expenditure,
                profit_rows=(
                    profit_loss.profit_and_appropriations
                ),
                tolerance=tolerance,
            )
        )

        # -------------------------------------------------
        # 4. Consolidated profit
        # -------------------------------------------------

        validations.append(
            validate_consolidated_profit(
                period=period,
                profit_rows=(
                    profit_loss.profit_and_appropriations
                ),
                tolerance=tolerance,
            )
        )

    # =====================================================
    # Overall status
    # =====================================================

    # Any actual calculation failure means FAILED.
    if any(
        item["status"] == "FAILED"
        for item in validations
    ):

        overall_status = "FAILED"

    # If a required validation could not be performed,
    # do not claim the whole P&L passed.
    elif any(
        item["status"] == "NOT_APPLICABLE"
        for item in validations
    ):

        overall_status = "NOT_APPLICABLE"

    else:

        overall_status = "PASS"

    return {
        "overall_status": overall_status,
        "tolerance": str(tolerance),
        "validations": validations,
    }