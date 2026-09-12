from backend.app.database.database import Base, SessionLocal, engine
from backend.app.database.document_repository import (
    create_document,
    get_latest_document_by_name,
    get_all_documents,
    document_to_dict,
)


# =========================================================
# Create tables
# =========================================================

Base.metadata.create_all(bind=engine)


# =========================================================
# Create database session
# =========================================================

db = SessionLocal()


try:

    print("=" * 70)
    print("DOCUMENT REPOSITORY TEST")
    print("=" * 70)

    # -----------------------------------------------------
    # Test data
    # -----------------------------------------------------

    extracted_data = {
        "document_type": "INVOICE",
        "invoice_number": "TEST-001",
        "seller": {
            "name": "Test Seller"
        },
        "client": {
            "name": "Test Client"
        }
    }

    validation_data = {
        "overall_status": "PASS",
        "tolerance": "0.01",
        "validations": [
            {
                "validation": "invoice_total_calculation",
                "status": "PASS",
                "variance": "0.00"
            }
        ]
    }

    # -----------------------------------------------------
    # Create document
    # -----------------------------------------------------

    document = create_document(
        db=db,
        document_name="repository_test.pdf",
        document_type="INVOICE",
        status="PASS",
        extracted_data=extracted_data,
        validation_data=validation_data,
    )

    print()
    print("DOCUMENT CREATED")
    print("-" * 70)

    print("ID:", document.id)
    print("Name:", document.document_name)
    print("Type:", document.document_type)
    print("Status:", document.status)

    # -----------------------------------------------------
    # Retrieve latest document
    # -----------------------------------------------------

    latest = get_latest_document_by_name(
        db=db,
        document_name="repository_test.pdf",
    )

    print()
    print("LATEST DOCUMENT")
    print("-" * 70)

    if latest:

        print(
            document_to_dict(latest)
        )

    else:

        print("Document was not found.")

    # -----------------------------------------------------
    # Retrieve all documents
    # -----------------------------------------------------

    documents = get_all_documents(
        db=db
    )

    print()
    print("ALL DOCUMENTS")
    print("-" * 70)

    print(
        "Total documents:",
        len(documents)
    )

    for item in documents:

        print(
            f"ID={item.id} | "
            f"Name={item.document_name} | "
            f"Type={item.document_type} | "
            f"Status={item.status}"
        )

    print()
    print("=" * 70)
    print("DOCUMENT REPOSITORY TEST PASSED")
    print("=" * 70)


finally:

    db.close()