from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class InvoiceItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    item_number: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[str] = None
    unit: Optional[str] = None
    unit_price: Optional[str] = None
    net_amount: Optional[str] = None
    vat_rate: Optional[str] = None
    gross_amount: Optional[str] = None


class InvoiceParty(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Optional[str] = None
    address: list[str] = Field(default_factory=list)
    tax_id: Optional[str] = None


class InvoiceTotals(BaseModel):
    model_config = ConfigDict(extra="forbid")

    net_amount: Optional[str] = None
    vat_amount: Optional[str] = None
    gross_amount: Optional[str] = None


class InvoicePaymentInformation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    iban: Optional[str] = None
    payment_method: Optional[str] = None
    amount_paid: Optional[str] = None
    change: Optional[str] = None


class AdditionalField(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str
    value: Optional[str] = None


class InvoiceExtraction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_type: str = "INVOICE"

    invoice_number: Optional[str] = None
    date_of_issue: Optional[str] = None

    seller: Optional[InvoiceParty] = None
    client: Optional[InvoiceParty] = None

    items: list[InvoiceItem] = Field(default_factory=list)

    summary: Optional[InvoiceTotals] = None
    total: Optional[InvoiceTotals] = None

    payment_information: Optional[InvoicePaymentInformation] = None

    additional_fields: list[AdditionalField] = Field(
        default_factory=list
    )