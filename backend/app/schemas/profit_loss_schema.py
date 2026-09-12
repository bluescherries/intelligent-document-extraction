from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


# =========================================================
# Period value
# =========================================================

class ProfitLossPeriodValue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    period: str
    value: Optional[str] = None


# =========================================================
# Profit & Loss line item
# =========================================================

class ProfitLossLineItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str

    schedule: Optional[str] = None

    line_type: Literal[
        "ITEM",
        "SUBTOTAL",
        "TOTAL",
        "HEADING",
    ] = "ITEM"

    values: list[ProfitLossPeriodValue] = Field(
        default_factory=list
    )


# =========================================================
# General / additional information
# =========================================================

class ProfitLossAdditionalField(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str

    value: Optional[str] = None


# =========================================================
# Profit & Loss extraction
# =========================================================

class ProfitLossExtraction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_type: str = "PROFIT_AND_LOSS"

    statement_title: Optional[str] = None

    statement_date: Optional[str] = None

    currency: Optional[str] = None

    periods: list[str] = Field(
        default_factory=list
    )

    # -----------------------------------------------------
    # Income section
    # -----------------------------------------------------

    income: list[ProfitLossLineItem] = Field(
        default_factory=list
    )

    # -----------------------------------------------------
    # Expenditure section
    # -----------------------------------------------------

    expenditure: list[ProfitLossLineItem] = Field(
        default_factory=list
    )

    # -----------------------------------------------------
    # Profit / appropriation related rows
    # -----------------------------------------------------

    profit_and_appropriations: list[ProfitLossLineItem] = Field(
        default_factory=list
    )

    # -----------------------------------------------------
    # General information
    # -----------------------------------------------------

    other_information: list[ProfitLossAdditionalField] = Field(
        default_factory=list
    )

    additional_fields: list[ProfitLossAdditionalField] = Field(
        default_factory=list
    )