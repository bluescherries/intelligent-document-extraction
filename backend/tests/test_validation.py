from backend.app.services.document_validation_service import validate_document


def test_empty_file_is_rejected():

    result = validate_document(
        file_bytes=b"",
        filename="test.pdf",
        content_type="application/pdf",
    )

    assert result["status"] == "FAILED"
    assert result["reason"] == "EMPTY_FILE"


def test_unsupported_file_is_rejected():

    result = validate_document(
        file_bytes=b"some data",
        filename="test.docx",
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )

    assert result["status"] == "FAILED"
    assert result["reason"] == "UNSUPPORTED_FILE_TYPE"