from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, Text

from backend.app.database.database import Base


# =========================================================
# Documents table
# =========================================================

class Document(Base):
    __tablename__ = "documents"

    # -----------------------------------------------------
    # Primary key
    # -----------------------------------------------------

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # -----------------------------------------------------
    # Original uploaded filename
    # -----------------------------------------------------

    document_name = Column(
        Text,
        nullable=False,
        index=True,
    )

    # -----------------------------------------------------
    # Document type
    #
    # Examples:
    # INVOICE
    # BALANCE_SHEET
    # PROFIT_AND_LOSS
    # CASH_FLOW
    # -----------------------------------------------------

    document_type = Column(
        Text,
        nullable=False,
    )

    # -----------------------------------------------------
    # Processing status
    #
    # Examples:
    # PASS
    # FAILED
    # -----------------------------------------------------

    status = Column(
        Text,
        nullable=False,
    )

    # -----------------------------------------------------
    # Structured AI extraction JSON
    # -----------------------------------------------------

    extracted_data = Column(
        Text,
        nullable=True,
    )

    # -----------------------------------------------------
    # Financial validation JSON
    # -----------------------------------------------------

    validation_data = Column(
        Text,
        nullable=True,
    )

    # -----------------------------------------------------
    # Time when the document was processed
    # -----------------------------------------------------

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )