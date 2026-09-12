import json

from backend.app.database.database import Base, SessionLocal, engine
from backend.app.database.models import Document


# =========================================================
# Create database tables
# =========================================================

Base.metadata.create_all(bind=engine)


# =========================================================
# Create database session
# =========================================================

db = SessionLocal()


try:

    print("=" * 70)
    print("DATABASE CRUD TEST")
    print("=" * 70)

    # -----------------------------------------------------
    # Example structured extraction result
    # -----------------------------------------------------

    extracted_result = {
        "document_type": "INVOICE",
        "invoice_number": "94404257",
        "date_of_issue": "07/03/2013",
        "seller": {
            "name": "Cruz PLC"
        },
        "client": {
            "name": "Sandoval-Phillipps"
        }
    }

    # -----------------------------------------------------
    # Example financial validation result
    # -----------------------------------------------------

    validation_result = {
        "overall_status": "PASS",
        "tolerance": "0.01",
        "validations": [
            {
                "validation": "line_item_calculation",
                "status": "PASS",
                "variance": "0.00"
            },
            {
                "validation": "invoice_total_calculation",
                "status": "PASS",
                "variance": "0.00"
            }
        ]
    }

    # -----------------------------------------------------
    # Create document record
    # -----------------------------------------------------

    document = Document(
        document_name="test_invoice.jpg",
        document_type="INVOICE",
        status=validation_result["overall_status"],
        extracted_data=json.dumps(
            extracted_result
        ),
        validation_data=json.dumps(
            validation_result
        ),
    )

    # -----------------------------------------------------
    # Save to database
    # -----------------------------------------------------

    db.add(document)
    db.commit()

    # Refresh object so generated ID is available
    db.refresh(document)

    print()
    print("DOCUMENT SAVED SUCCESSFULLY")
    print("-" * 70)

    print("ID:", document.id)
    print("Document name:", document.document_name)
    print("Document type:", document.document_type)
    print("Status:", document.status)

    # -----------------------------------------------------
    # Retrieve the document
    # -----------------------------------------------------

    saved_document = (
        db.query(Document)
        .filter(
            Document.id == document.id
        )
        .first()
    )

    print()
    print("DOCUMENT RETRIEVED SUCCESSFULLY")
    print("-" * 70)

    print(
        "Document name:",
        saved_document.document_name
    )

    print(
        "Document type:",
        saved_document.document_type
    )

    print(
        "Status:",
        saved_document.status
    )

    # -----------------------------------------------------
    # Convert JSON strings back to Python objects
    # -----------------------------------------------------

    saved_extracted_data = json.loads(
        saved_document.extracted_data
    )

    saved_validation_data = json.loads(
        saved_document.validation_data
    )

    print()
    print("EXTRACTED DATA")
    print("-" * 70)

    print(
        json.dumps(
            saved_extracted_data,
            indent=2
        )
    )

    print()
    print("VALIDATION DATA")
    print("-" * 70)

    print(
        json.dumps(
            saved_validation_data,
            indent=2
        )
    )

    print()
    print("=" * 70)
    print("DATABASE CRUD TEST PASSED")
    print("=" * 70)


finally:

    # -----------------------------------------------------
    # Always close the database session
    # -----------------------------------------------------

    db.close()