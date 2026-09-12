import json

from sqlalchemy.orm import Session

from backend.app.database.models import Document


# =========================================================
# Create a document
# =========================================================

def create_document(
    db: Session,
    document_name: str,
    document_type: str,
    status: str,
    extracted_data: dict,
    validation_data: dict,
) -> Document:

    document = Document(
        document_name=document_name,
        document_type=document_type,
        status=status,
        extracted_data=json.dumps(
            extracted_data,
            ensure_ascii=False,
        ),
        validation_data=json.dumps(
            validation_data,
            ensure_ascii=False,
        ),
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


# =========================================================
# Get latest document by name
# =========================================================

def get_latest_document_by_name(
    db: Session,
    document_name: str,
) -> Document | None:

    return (
        db.query(Document)
        .filter(
            Document.document_name == document_name
        )
        .order_by(
            Document.created_at.desc()
        )
        .first()
    )


# =========================================================
# Get all documents
# =========================================================

def get_all_documents(
    db: Session,
) -> list[Document]:

    return (
        db.query(Document)
        .order_by(
            Document.created_at.desc()
        )
        .all()
    )


# =========================================================
# Convert database document to API-friendly dictionary
# =========================================================

def document_to_dict(
    document: Document,
) -> dict:

    return {
        "id": document.id,
        "document_name": document.document_name,
        "document_type": document.document_type,
        "status": document.status,
        "extracted_data": (
            json.loads(document.extracted_data)
            if document.extracted_data
            else None
        ),
        "validation_data": (
            json.loads(document.validation_data)
            if document.validation_data
            else None
        ),
        "created_at": (
            document.created_at.isoformat()
            if document.created_at
            else None
        ),
    }