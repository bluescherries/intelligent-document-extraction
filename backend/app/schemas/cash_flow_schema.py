from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


# =========================================================
# Period value
# =========================================================

class CashFlowPeriodValue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    period: str
    value: Optional[str] = None


# =========================================================
# Cash Flow line item
# =========================================================

class CashFlowLineItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str

    schedule: Optional[str] = None

    line_type: Literal[
        "ITEM",
        "SUBTOTAL",
        "TOTAL",
        "HEADING",
    ] = "ITEM"

    values: list[CashFlowPeriodValue] = Field(
        default_factory=list
    )


# =========================================================
# General / additional information
# =========================================================

class CashFlowAdditionalField(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str

    value: Optional[str] = None


# =========================================================
# Cash Flow extraction
# =========================================================

class CashFlowExtraction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_type: str = "CASH_FLOW"

    statement_title: Optional[str] = None

    statement_date: Optional[str] = None

    currency: Optional[str] = None

    periods: list[str] = Field(
        default_factory=list
    )

    # -----------------------------------------------------
    # Operating activities
    # -----------------------------------------------------

    operating_activities: list[CashFlowLineItem] = Field(
        default_factory=list
    )

    # -----------------------------------------------------
    # Investing activities
    # -----------------------------------------------------

    investing_activities: list[CashFlowLineItem] = Field(
        default_factory=list
    )

    # -----------------------------------------------------
    # Financing activities
    # -----------------------------------------------------

    financing_activities: list[CashFlowLineItem] = Field(
        default_factory=list
    )

    # -----------------------------------------------------
    # Cash / reconciliation section
    # -----------------------------------------------------

    cash_reconciliation: list[CashFlowLineItem] = Field(
        default_factory=list
    )

    # -----------------------------------------------------
    # General information
    # -----------------------------------------------------

    other_information: list[CashFlowAdditionalField] = Field(
        default_factory=list
    )

    additional_fields: list[CashFlowAdditionalField] = Field(
        default_factory=list
    )