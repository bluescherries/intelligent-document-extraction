from decimal import Decimal

from backend.app.services.document_validation_service import (
    validate_document,
)

from backend.app.services.ocr_service import (
    extract_text,
)

from backend.app.services.extraction_service import (
    extract_invoice_data,
)

from backend.app.services.financial_validation_service import (
    validate_invoice,
)

from backend.app.services.balance_sheet_extraction_service import (
    extract_balance_sheet_data,
)

from backend.app.services.balance_sheet_validation_service import (
    validate_balance_sheet,
)

from backend.app.services.profit_loss_extraction_service import (
    extract_profit_loss_data,
)

from backend.app.services.profit_loss_validation_service import (
    validate_profit_loss,
)

from backend.app.services.cash_flow_extraction_service import (
    extract_cash_flow_data,
)

from backend.app.services.cash_flow_validation_service import (
    validate_cash_flow,
)

from backend.app.database.document_repository import (
    create_document,
)

from backend.app.database.database import SessionLocal


# =========================================================
# Configuration
# =========================================================

DEFAULT_TOLERANCE = Decimal("0.01")


# =========================================================
# Convert Pydantic model to dictionary
# =========================================================

def model_to_dict(model):
    """
    Convert a Pydantic model into a normal Python dictionary.
    """

    if model is None:
        return None

    return model.model_dump()


# =========================================================
# Combine OCR pages
# =========================================================

def combine_ocr_pages(pages: list[dict]) -> str:
    """
    Combine OCR text from all pages into one string.
    """

    return "\n\n".join(
        page.get("text", "")
        for page in pages
        if page.get("text")
    )


# =========================================================
# Get overall validation status
# =========================================================

def get_overall_status(validation_result: dict) -> str:
    """
    Get PASS / FAILED / NOT_APPLICABLE status
    from a validation result.
    """

    status = validation_result.get(
        "overall_status"
    )

    if status:
        return status

    # Fallback:
    # inspect individual validations
    validations = validation_result.get(
        "validations",
        []
    )

    for validation in validations:

        if validation.get("status") == "FAILED":
            return "FAILED"

    return "PASS"


# =========================================================
# Process document
# =========================================================

def process_document(
    file_bytes: bytes,
    filename: str,
    document_type: str,
    content_type: str | None = None,
    tolerance: Decimal = DEFAULT_TOLERANCE,
) -> dict:

    # -----------------------------------------------------
    # Normalize document type
    # -----------------------------------------------------

    document_type = document_type.strip().upper()

    supported_types = {
        "INVOICE",
        "BALANCE_SHEET",
        "PROFIT_AND_LOSS",
        "CASH_FLOW",
    }

    if document_type not in supported_types:

        raise ValueError(
            "Unsupported document type. "
            "Supported types are: "
            "INVOICE, BALANCE_SHEET, "
            "PROFIT_AND_LOSS, CASH_FLOW."
        )

    # -----------------------------------------------------
    # Step 1: Validate uploaded document
    # -----------------------------------------------------

    validation_result = validate_document(
        file_bytes=file_bytes,
        filename=filename,
        content_type=content_type,
    )

    # -----------------------------------------------------
    # If document is invalid, stop before OCR / AI
    # -----------------------------------------------------

    if validation_result.get("status") != "PASS":
        failed_result = {
            "document_name": filename,
            "document_type": document_type,
            "status": "FAILED",
            "validation": validation_result,
            "extracted_data": None,
            "financial_validation": None,
            "extracted_data": None,
            "database_id": None,
            "error": validation_result,
        }

        return failed_result

    # -----------------------------------------------------
    # Step 2: OCR / text extraction
    # -----------------------------------------------------

    pages = extract_text(
        file_bytes=file_bytes,
        filename=filename,
    )

    # -----------------------------------------------------
    # Make sure OCR produced something
    # -----------------------------------------------------

    ocr_text = combine_ocr_pages(
        pages
    )

    if not ocr_text.strip():

        failed_result = {
            "document_name": filename,
            "document_type": document_type,
            "status": "FAILED",
            "validation": validation_result,
            "extracted_data": None,
            "financial_validation": None,
            "error": "No readable text could be extracted from the document.",
        }

        return failed_result

    # -----------------------------------------------------
    # Step 3: AI extraction
    # -----------------------------------------------------

    extracted_model = None
    financial_validation = None

    # =====================================================
    # INVOICE
    # =====================================================

    if document_type == "INVOICE":

        extracted_model = extract_invoice_data(
            ocr_text
        )

        financial_validation = validate_invoice(
            extracted_model,
            tolerance=tolerance,
        )

    # =====================================================
    # BALANCE SHEET
    # =====================================================

    elif document_type == "BALANCE_SHEET":

        extracted_model = extract_balance_sheet_data(
            ocr_text
        )

        financial_validation = validate_balance_sheet(
            extracted_model,
            tolerance=tolerance,
        )

    # =====================================================
    # PROFIT & LOSS
    # =====================================================

    elif document_type == "PROFIT_AND_LOSS":

        extracted_model = extract_profit_loss_data(
            ocr_text
        )

        financial_validation = validate_profit_loss(
            extracted_model,
            tolerance=tolerance,
        )

    # =====================================================
    # CASH FLOW
    # =====================================================

    elif document_type == "CASH_FLOW":

        extracted_model = extract_cash_flow_data(
            ocr_text
        )

        financial_validation = validate_cash_flow(
            extracted_model,
            tolerance=tolerance,
        )

    # -----------------------------------------------------
    # Convert Pydantic extraction to dictionary
    # -----------------------------------------------------

    extracted_data = model_to_dict(
        extracted_model
    )

    # -----------------------------------------------------
    # Determine final status
    # -----------------------------------------------------

    overall_status = get_overall_status(
        financial_validation
    )

    # -----------------------------------------------------
    # Step 4: Save result to database
    # -----------------------------------------------------

    db = SessionLocal()

    try:

        saved_document = create_document(
            db=db,
            document_name=filename,
            document_type=document_type,
            status=overall_status,
            extracted_data=extracted_data,
            validation_data=financial_validation,
        )

    finally:

        db.close()

    # -----------------------------------------------------
    # Step 5: Return complete result
    # -----------------------------------------------------

    return {
        "id": saved_document.id,
        "document_name": filename,
        "document_type": document_type,
        "status": overall_status,
        "extracted_data": extracted_data,
        "financial_validation": financial_validation,
        "created_at": (
            saved_document.created_at.isoformat()
            if saved_document.created_at
            else None
        ),
    }