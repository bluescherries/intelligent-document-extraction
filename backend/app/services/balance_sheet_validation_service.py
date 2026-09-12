from decimal import Decimal, InvalidOperation
from typing import Optional

from backend.app.schemas.balance_sheet_schema import (
    BalanceSheetExtraction,
    BalanceSheetLineItem,
)


# =========================================================
# Default tolerance
# =========================================================

DEFAULT_TOLERANCE = Decimal("0.01")


# =========================================================
# Parse financial number
# =========================================================

def parse_decimal(
    value: Optional[str],
) -> Optional[Decimal]:

    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

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

    # Handle decimal + thousands separator.
    if "," in text and "." in text:

        if text.rfind(",") > text.rfind("."):

            # Example:
            # 1.234,56
            text = text.replace(".", "")
            text = text.replace(",", ".")

        else:

            # Example:
            # 1,234.56
            text = text.replace(",", "")

    elif "," in text:

        parts = text.split(",")

        if (
            len(parts) == 2
            and len(parts[1]) <= 2
        ):

            text = text.replace(",", ".")

        else:

            # Example:
            # 7,622,123,264
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
# PASS / FAILED
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
    line_item: BalanceSheetLineItem,
    period: str,
) -> Optional[Decimal]:

    for period_value in line_item.values:

        if period_value.period == period:

            return parse_decimal(
                period_value.value
            )

    return None


# =========================================================
# Normalize line-item name
# =========================================================

def normalize_name(
    name: str,
) -> str:

    return (
        name.lower()
        .strip()
        .replace(":", "")
        .replace("-", " ")
    )


# =========================================================
# Find the main total
# =========================================================

def find_main_total(
    line_items: list[BalanceSheetLineItem],
    total_type: str,
) -> Optional[BalanceSheetLineItem]:

    # -----------------------------------------------------
    # 1. First preference:
    #    AI explicitly classified the row as TOTAL
    # -----------------------------------------------------

    total_candidates = [
        item
        for item in line_items
        if item.line_type == "TOTAL"
    ]

    # Look for an explicitly named main total.
    for item in total_candidates:

        name = normalize_name(
            item.name
        )

        if total_type == "assets":

            if (
                "total assets" in name
                or name == "assets total"
                or name == "total"
            ):
                return item

        elif total_type == "capital_and_liabilities":

            if (
                "total capital and liabilities"
                in name
                or "total capital & liabilities"
                in name
                or "capital and liabilities total"
                in name
                or name == "total"
            ):
                return item

    # -----------------------------------------------------
    # 2. If there are TOTAL rows but the name is unusual,
    #    use the LAST TOTAL row in that section.
    #
    #    This is useful for statements where the final row
    #    is simply called "Total".
    # -----------------------------------------------------

    if total_candidates:

        return total_candidates[-1]

    # -----------------------------------------------------
    # 3. Fallback:
    #    Search all rows for an explicitly named main total.
    # -----------------------------------------------------

    for item in line_items:

        name = normalize_name(
            item.name
        )

        if total_type == "assets":

            if "total assets" in name:

                return item

        elif total_type == "capital_and_liabilities":

            if (
                "total capital and liabilities"
                in name
                or "total capital & liabilities"
                in name
            ):

                return item

    # -----------------------------------------------------
    # 4. Final fallback:
    #    In a section such as Assets or Capital &
    #    Liabilities, a final row named "Total" can
    #    represent the section total.
    # -----------------------------------------------------

    generic_total_candidates = []

    for item in line_items:

        name = normalize_name(
            item.name
        )

        if name == "total":

            generic_total_candidates.append(
                item
            )

    if generic_total_candidates:

        return generic_total_candidates[-1]

    return None


# =========================================================
# Validate Total Assets ≈ Total Capital & Liabilities
# =========================================================

def validate_balance_equation(
    period: str,
    assets: list[BalanceSheetLineItem],
    capital_and_liabilities: list[BalanceSheetLineItem],
    tolerance: Decimal,
) -> dict:

    total_assets_item = find_main_total(
        assets,
        "assets",
    )

    total_liabilities_item = find_main_total(
        capital_and_liabilities,
        "capital_and_liabilities",
    )

    if (
        total_assets_item is None
        or total_liabilities_item is None
    ):

        return {
            "validation": "balance_sheet_equation",
            "period": period,
            "formula": (
                "total_assets ≈ "
                "total_capital_and_liabilities"
            ),
            "inputs": {
                "total_assets_row": (
                    total_assets_item.name
                    if total_assets_item is not None
                    else None
                ),
                "total_capital_and_liabilities_row": (
                    total_liabilities_item.name
                    if total_liabilities_item is not None
                    else None
                ),
            },
            "calculated": None,
            "reported": None,
            "variance": None,
            "status": "NOT_APPLICABLE",
        }

    total_assets = get_period_value(
        total_assets_item,
        period,
    )

    total_capital_and_liabilities = (
        get_period_value(
            total_liabilities_item,
            period,
        )
    )

    if (
        total_assets is None
        or total_capital_and_liabilities is None
    ):

        return {
            "validation": "balance_sheet_equation",
            "period": period,
            "formula": (
                "total_assets ≈ "
                "total_capital_and_liabilities"
            ),
            "inputs": {
                "total_assets": (
                    str(total_assets)
                    if total_assets is not None
                    else None
                ),
                "total_capital_and_liabilities": (
                    str(
                        total_capital_and_liabilities
                    )
                    if (
                        total_capital_and_liabilities
                        is not None
                    )
                    else None
                ),
            },
            "calculated": None,
            "reported": None,
            "variance": None,
            "status": "NOT_APPLICABLE",
        }

    variance = calculate_variance(
        total_assets,
        total_capital_and_liabilities,
    )

    status = get_status(
        total_assets,
        total_capital_and_liabilities,
        tolerance,
    )

    return {
        "validation": "balance_sheet_equation",
        "period": period,
        "formula": (
            "total_assets ≈ "
            "total_capital_and_liabilities"
        ),
        "inputs": {
            "total_assets": str(
                total_assets
            ),
            "total_capital_and_liabilities": str(
                total_capital_and_liabilities
            ),
        },
        "calculated": str(
            total_assets
        ),
        "reported": str(
            total_capital_and_liabilities
        ),
        "variance": str(
            variance
        ),
        "status": status,
    }


# =========================================================
# Component reconciliation
# =========================================================

def validate_component_sum(
    period: str,
    line_items: list[BalanceSheetLineItem],
    section_name: str,
    total_type: str,
    tolerance: Decimal,
) -> dict:

    total_item = find_main_total(
        line_items,
        total_type,
    )

    if total_item is None:

        return {
            "validation": (
                f"{section_name}_component_sum"
            ),
            "period": period,
            "formula": (
                f"sum({section_name} ITEM rows) "
                f"≈ total {section_name}"
            ),
            "inputs": {},
            "calculated": None,
            "reported": None,
            "variance": None,
            "status": "NOT_APPLICABLE",
        }

    reported_total = get_period_value(
        total_item,
        period,
    )

    if reported_total is None:

        return {
            "validation": (
                f"{section_name}_component_sum"
            ),
            "period": period,
            "formula": (
                f"sum({section_name} ITEM rows) "
                f"≈ total {section_name}"
            ),
            "inputs": {},
            "calculated": None,
            "reported": None,
            "variance": None,
            "status": "NOT_APPLICABLE",
        }

    # -----------------------------------------------------
    # Only direct ITEM rows are included.
    #
    # SUBTOTAL, TOTAL and HEADING rows are excluded.
    # -----------------------------------------------------

    component_values = []

    component_names = []

    for item in line_items:

        if item is total_item:
            continue

        if item.line_type != "ITEM":
            continue

        value = get_period_value(
            item,
            period,
        )

        if value is not None:

            component_values.append(
                value
            )

            component_names.append(
                item.name
            )

    if not component_values:

        return {
            "validation": (
                f"{section_name}_component_sum"
            ),
            "period": period,
            "formula": (
                f"sum({section_name} ITEM rows) "
                f"≈ total {section_name}"
            ),
            "inputs": {},
            "calculated": None,
            "reported": str(
                reported_total
            ),
            "variance": None,
            "status": "NOT_APPLICABLE",
        }

    calculated_total = sum(
        component_values,
        Decimal("0"),
    )

    variance = calculate_variance(
        calculated_total,
        reported_total,
    )

    status = get_status(
        calculated_total,
        reported_total,
        tolerance,
    )

    return {
        "validation": (
            f"{section_name}_component_sum"
        ),
        "period": period,
        "formula": (
            f"sum({section_name} ITEM rows) "
            f"≈ total {section_name}"
        ),
        "inputs": {
            "components": component_names
        },
        "calculated": str(
            calculated_total
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
# Main Balance Sheet validator
# =========================================================

def validate_balance_sheet(
    balance_sheet: BalanceSheetExtraction,
    tolerance: Decimal = DEFAULT_TOLERANCE,
) -> dict:

    validations = []

    # -----------------------------------------------------
    # Validate each period independently.
    # -----------------------------------------------------

    for period in balance_sheet.periods:

        # -------------------------------------------------
        # 1. Main accounting equation
        # -------------------------------------------------

        equation_result = (
            validate_balance_equation(
                period=period,
                assets=balance_sheet.assets,
                capital_and_liabilities=(
                    balance_sheet.capital_and_liabilities
                ),
                tolerance=tolerance,
            )
        )

        validations.append(
            equation_result
        )

        # -------------------------------------------------
        # 2. Asset component reconciliation
        # -------------------------------------------------

        asset_result = validate_component_sum(
            period=period,
            line_items=balance_sheet.assets,
            section_name="assets",
            total_type="assets",
            tolerance=tolerance,
        )

        validations.append(
            asset_result
        )

        # -------------------------------------------------
        # 3. Capital/liability reconciliation
        # -------------------------------------------------

        liability_result = (
            validate_component_sum(
                period=period,
                line_items=(
                    balance_sheet.capital_and_liabilities
                ),
                section_name=(
                    "capital_and_liabilities"
                ),
                total_type=(
                    "capital_and_liabilities"
                ),
                tolerance=tolerance,
            )
        )

        validations.append(
            liability_result
        )

    # =====================================================
    # Overall status
    # =====================================================

    # If ANY validation genuinely fails,
    # the overall result is FAILED.
    if any(
        validation["status"] == "FAILED"
        for validation in validations
    ):

        overall_status = "FAILED"

    # If a required balance equation is not applicable,
    # we cannot claim that the Balance Sheet passed.
    elif any(
        validation["validation"]
        == "balance_sheet_equation"
        and validation["status"]
        == "NOT_APPLICABLE"
        for validation in validations
    ):

        overall_status = "NOT_APPLICABLE"

    else:

        overall_status = "PASS"

    return {
        "overall_status": overall_status,
        "tolerance": str(tolerance),
        "validations": validations,
    }