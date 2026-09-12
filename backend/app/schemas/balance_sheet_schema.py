from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


# =========================================================
# Period value
# =========================================================

class BalanceSheetPeriodValue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    period: str
    value: Optional[str] = None


# =========================================================
# Balance Sheet line item
# =========================================================

class BalanceSheetLineItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str

    schedule: Optional[str] = None

    line_type: Literal[
        "ITEM",
        "SUBTOTAL",
        "TOTAL",
        "HEADING",
    ] = "ITEM"

    values: list[BalanceSheetPeriodValue] = Field(
        default_factory=list
    )


# =========================================================
# Additional / general information
# =========================================================

class BalanceSheetAdditionalField(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str

    value: Optional[str] = None


# =========================================================
# Balance Sheet extraction
# =========================================================

class BalanceSheetExtraction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_type: str = "BALANCE_SHEET"

    statement_title: Optional[str] = None

    statement_date: Optional[str] = None

    currency: Optional[str] = None

    periods: list[str] = Field(
        default_factory=list
    )

    capital_and_liabilities: list[BalanceSheetLineItem] = Field(
        default_factory=list
    )

    assets: list[BalanceSheetLineItem] = Field(
        default_factory=list
    )

    other_information: list[BalanceSheetAdditionalField] = Field(
        default_factory=list
    )

    additional_fields: list[BalanceSheetAdditionalField] = Field(
        default_factory=list
    )