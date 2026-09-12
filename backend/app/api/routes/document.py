from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.app.database.database import SessionLocal
from backend.app.database.document_repository import (
    create_document,
    get_all_documents,
    get_latest_document_by_name,
)
from backend.app.services.document_processing_service import process_document


router = APIRouter(
    prefix="/api/v1/documents",
    tags=["Documents"],
)


# =========================================================
# DATABASE SESSION
# =========================================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# =========================================================
# POST /api/v1/documents/process
# =========================================================

@router.post("/process")
async def process_document_endpoint(
    file: UploadFile = File(...),
    document_type: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    Upload and process a financial document.

    Supported document types:
    - INVOICE
    - BALANCE_SHEET
    - PROFIT_AND_LOSS
    - CASH_FLOW
    """

    # -----------------------------------------------------
    # Validate document type
    # -----------------------------------------------------

    allowed_document_types = {
        "INVOICE",
        "BALANCE_SHEET",
        "PROFIT_AND_LOSS",
        "CASH_FLOW",
    }

    document_type = document_type.strip().upper()

    if document_type not in allowed_document_types:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Unsupported document type",
                "supported_types": sorted(allowed_document_types),
            },
        )

    # -----------------------------------------------------
    # Validate filename
    # -----------------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    # -----------------------------------------------------
    # Read uploaded file
    # -----------------------------------------------------

    try:
        file_bytes = await file.read()
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to read uploaded file: {str(exc)}",
        )

    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    # -----------------------------------------------------
    # Process complete document pipeline
    # -----------------------------------------------------

    try:
        result = process_document(
            file_bytes=file_bytes,
            filename=file.filename,
            document_type=document_type,
            content_type=file.content_type,
            tolerance=Decimal("0.01"),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Document processing failed",
                "message": str(exc),
            },
        )

    # -----------------------------------------------------
    # Save result to database
    # -----------------------------------------------------

    try:
        document = create_document(
            db=db,
            document_name=file.filename,
            document_type=document_type,
            status=result.get("status", "FAILED"),
            extracted_data=result.get("extracted_data"),
            validation_data=result.get("financial_validation"),
        )

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Database persistence failed",
                "message": str(exc),
            },
        )

    # -----------------------------------------------------
    # Return API response
    # -----------------------------------------------------

    return {
        "id": document.id,
        "document_name": document.document_name,
        "document_type": document.document_type,
        "status": document.status,
        "extracted_data": result.get("extracted_data"),
        "financial_validation": result.get("financial_validation"),
        "created_at": document.created_at,
    }


# =========================================================
# GET /api/v1/documents/{document_name}
# =========================================================

@router.get("/{document_name}")
def get_document(
    document_name: str,
    db: Session = Depends(get_db),
):
    """
    Return the latest processed result for a document name.
    """

    document = get_latest_document_by_name(
        db=db,
        document_name=document_name,
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail=f"Document '{document_name}' was not found.",
        )

    return {
        "id": document.id,
        "document_name": document.document_name,
        "document_type": document.document_type,
        "status": document.status,
        "extracted_data": document.extracted_data,
        "financial_validation": document.validation_data,
        "created_at": document.created_at,
    }


# =========================================================
# GET /api/v1/documents
# =========================================================

@router.get("")
def get_documents(
    db: Session = Depends(get_db),
):
    """
    Return all processed documents.
    """

    documents = get_all_documents(db=db)

    return {
        "total": len(documents),
        "documents": [
            {
                "id": document.id,
                "document_name": document.document_name,
                "document_type": document.document_type,
                "status": document.status,
                "created_at": document.created_at,
            }
            for document in documents
        ],
    }